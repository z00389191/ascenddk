# -*- coding: UTF-8 -*-
#
#    =======================================================================
#    Copyright (C), 2018, Huawei Tech. Co., Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#    =======================================================================
#
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed
import json
import os
import re
import sys

import comm.ci_log as cilog
import comm.util as util
import static_check_util as sc_util


THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))


BASE_SO_PATH = [os.path.join(sc_util.ASCEND_ROOT_PATH, "ascenddk/common/presenter/agent"),
                os.path.join(sc_util.ASCEND_ROOT_PATH,
                             "ascenddk/common/utils/ascend_ezdvpp"),
                os.path.join(sc_util.ASCEND_ROOT_PATH, "ascenddk/common/osd")]


def single_warn_check_compile(cmd, mind_file, oi_engine_config_dict):
    mind_file_paths = os.path.split(mind_file)
    mind_file_path = mind_file_paths[0]

    try:
        mind_file_stream = open(mind_file, 'r')
        mind_file_info = json.load(mind_file_stream)
        mind_nodes = mind_file_info.get("node")
    except OSError as reason:
        cilog.cilog_error(
            THIS_FILE_NAME, "read %s failed: %s", mind_file, reason)
        return False

    result = True
    for mind_node in mind_nodes:
        if mind_node.get("groups") == "MyModel":
            continue

        name = mind_node.get("name")
        run_side = mind_node.get("params").get("runSide")

        checked_file_path = os.path.join(mind_file_path, name)

        header_list = oi_engine_config_dict.get(
            run_side.lower()).get("includes").get("include")
        header_list = list(map(lambda x:
                               re.sub("\$\(SRC_DIR\)", checked_file_path, x), header_list))
        header_list = list(map(lambda x:
                               re.sub("\.\.", mind_file_path, x), header_list))
        header_list = list(map(lambda x:
                               re.sub(" \\\\", "", x), header_list))
        header_list = list(map(lambda x:
                               re.sub("\$\(DDK_HOME\)", os.getenv("DDK_HOME"), x), header_list))

        temp_cmd = re.sub("__WARN_CHECK_HEADERS__", " ".join(header_list), cmd)

        checked_file_cmd = "find " + checked_file_path + \
            " -name \"*.cpp\" -o -name \"*.h\""
        ret = util.execute(checked_file_cmd, print_output_flag=True)
        if ret[0] is False:
            result = False
            continue

        checked_files = ret[1]

        for file in checked_files:
            file_names = os.path.split(file)
            temp_cmd = re.sub("__WARN_CHECK_FILE__", file, temp_cmd)
            temp_cmd = re.sub("__WARN_CHECK_FILE_NAME__",
                              file_names[1], temp_cmd)
            ret = util.execute(temp_cmd, print_output_flag=True)
            if ret[0] is False:
                result = False

        return result


def warn_check_compile(cmd):
    engine_mind_cmd = "find " + \
        os.path.join(sc_util.ASCEND_ROOT_PATH,
                     "ascenddk/engine") + " -name \"*.mind\""
    ret = util.execute(engine_mind_cmd, print_output_flag=True)
    if ret[0] is False:
        return False
    mind_files = ret[1]

    ddk_engine_config_path = os.path.join(
        os.getenv("DDK_HOME"), "conf/settings_engine.conf")
    try:
        ddk_engine_config_file = open(ddk_engine_config_path, 'r')
        ddk_engine_config_info = json.load(ddk_engine_config_file)
        oi_engine_config_dict = ddk_engine_config_info.get(
            "configuration").get("OI")
    except OSError as reason:
        cilog.cilog_error(
            THIS_FILE_NAME, "read ddk conf/settings_engine.conf failed: %s", reason)
        return False
    finally:
        if ddk_engine_config_file in locals():
            ddk_engine_config_file.close()

    oi_lower_dict = {k.lower(): v for k, v in oi_engine_config_dict.items()}

    result = True
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures_pool = {executor.submit(
            single_warn_check_compile, cmd, mind_file, oi_lower_dict): mind_file for mind_file in mind_files}
        for future in as_completed(futures_pool):
            if future.result() is False:
                result = False
    return result


def single_warn_check_makefile(cmd, makefile_path):
    cmd = re.sub("(__[\w+_\w+]*__)", makefile_path, cmd)
    ret = util.execute(cmd, print_output_flag=True)
    return ret[0]


def warn_check_makefile(cmd):

    # find path which need to be checked
    ret = sc_util.find_checked_path()
    if ret[0] is False:
        return False
    checked_path = ret[1]

    if len(checked_path) == 0:
        cilog.cilog_info(THIS_FILE_NAME, "no path to check in makefile mode")
        return True

    makefile_path_list = []

    for each_path in checked_path:
        makefile_cmd = "find " + each_path + " -name \"Makefile\""
        ret = util.execute(makefile_cmd, print_output_flag=True)
        if ret[0] is False:
            return False
        makefiles = list(map(lambda x: os.path.split(x)[0], ret[1]))
        makefile_path_list.extend(makefiles)

    # base so should be executed fist in sequence and copy to DDK path
    copy_cmd = "cp -R __MAKEFILE_OUT_PATH__/out/lib* " + \
        os.path.join(os.getenv("DDK_HOME"), "lib/aarch64-linux-gcc5.4")
    for each_path in BASE_SO_PATH:
        makefile_path_list.remove(each_path)
        ret = single_warn_check_makefile(cmd, each_path)
        if ret is False:
            return False
        temp_copy_cmd = re.sub("__MAKEFILE_OUT_PATH__", each_path, copy_cmd)
        ret = util.execute(temp_copy_cmd, print_output_flag=True)
        if ret[0] is False:
            return False
    
    makefile_path_list.remove("")
    if len(makefile_path_list) == 0:
        cilog.cilog_info(
            THIS_FILE_NAME, "no Makefile to check in makefile mode")
        return True

    result = True
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures_pool = {executor.submit(
            single_warn_check_makefile, cmd, mind_file_path): mind_file_path for mind_file_path in makefile_path_list}
        for future in as_completed(futures_pool):
            if future.result() is False:
                result = False
    return result


def warn_check(compile_cmd, makefile_cmd):
    result = warn_check_makefile(makefile_cmd)

    ret = warn_check_compile(compile_cmd)

    if ret is False:
        result = ret

    return result


def filter_warn_check_is_none(file_name):
    # replace env in the file_name
    file_name = sc_util.replace_env(file_name)
    try:
        file_stream = open(file_name, 'r')
        while True:
            lines = file_stream.readlines(100000)
            if not lines:
                break
            for line in lines:
                if "warning" in line:
                    return False
    except OSError as reason:
        cilog.cilog_error(
            THIS_FILE_NAME, "read file failed: %s", reason)
        return False
    finally:
        if file_stream in locals():
            file_stream.close()
    return True
