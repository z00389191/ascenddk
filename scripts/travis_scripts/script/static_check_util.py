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
import os
import re
import sys

THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))

import comm.util as util
import comm.ci_log as cilog

FILE_EMPTY_SIZE = 0

#{replace_pattern : replace_value}
ENV_DICT = {"\$\{BUILD_TEMP_PATH\}": os.getenv("BUILD_TEMP_PATH"),
            "\$\{ASCEND_ROOT_PATH\}": os.getenv("ASCEND_ROOT_PATH")}


def replace_env(file_name):
    for key, value in ENV_DICT.items():
        file_name = re.sub(key, value, file_name)
    return file_name


def check_file_is_empty(file_name):
    # replace env in the file_name
    file_name = replace_env(file_name)
    if os.path.getsize(file_name) == FILE_EMPTY_SIZE:
        return True
    else:
        return False


def warn_check_compile(cmd, checked_path, headers_list):
    checked_path = replace_env(checked_path)
    if not os.path.exists(checked_path):
        cilog.cilog_error(
            THIS_FILE_NAME, "can not find cpp list file: %s", checked_path)
        return False
    checked_file_cmd = "find " + checked_path + " -name \"*.cpp\" -o -name \"*.h\""
    ret = util.execute(checked_file_cmd)
    if ret[0] is False:
        cilog.cilog_error(
            THIS_FILE_NAME, "can not find cpp list file: %s", checked_path)
        return False

    checked_file = ret[1]

    headers = ""
    if headers_list is not None:
        headers = " -I".join(headers_list)
        headers = "-I" + headers

    cmd = re.sub("__WARN_CHECK_HEADERS__", headers, cmd)

    for file in checked_file:
        file_names = os.path.split(file)
        temp_cmd = re.sub("__WARN_CHECK_FILE__", file, cmd)
        temp_cmd = re.sub("__WARN_CHECK_FILE_NAME__", file_names[1], temp_cmd)
        util.execute(temp_cmd, print_output_flag=True)
    return True


def filter_warn_check_is_none(file_name):
    # replace env in the file_name
    file_name = replace_env(file_name)
    try:
        file_stream = open(file_name, 'r')
        while True:
            lines = file_stream.readlines(100000)
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
