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
import os
import re
import sys

import comm.ci_log as cilog
import comm.util as util
import static_check_util as sc_util


THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))


def single_pylint(cmd, params):

    for key, value in params.items():
        cmd = re.sub(key, value, cmd)

    ret = util.execute(cmd, print_output_flag=True)

    # pylint check failed will return False
    if ret[0] is False:
        return False

    return True


def pylint(cmd, sub_params):
    ret = sc_util.find_checked_path()
    if ret is False:
        return False
    checked_path = ret[1]

    if len(checked_path) == 0:
        cilog.cilog_info(THIS_FILE_NAME, "no path to check in pylint")
        return True

    init_path_list = []

    for each_path in checked_path:
        initfile_cmd = "find " + each_path + " -name \"__init__.py\""
        ret = util.execute(initfile_cmd, print_output_flag=True)
        if ret[0] is False:
            return False
        initfiles = list(map(lambda x: os.path.split(x)[0], ret[1]))
        init_path_list.extend(initfiles)

    if len(init_path_list) == 0:
        cilog.cilog_info(THIS_FILE_NAME, "no path to check in pylint")
        return True

    init_path_list.sort()
    sub_params.sort()
    params_list = []

    for cur_index in range(len(init_path_list)):
        if cur_index > len(init_path_list) - 1:
            break
        next_index = cur_index + 1
        if next_index <= len(init_path_list) - 1:
            while True:
                if init_path_list[cur_index] not in init_path_list[next_index]:
                    break
                init_path_list.remove(init_path_list[next_index])
        pylint_path = init_path_list[cur_index]
        pylint_ignore_file_list = []
        for sub_cur_index in range(len(sub_params)):
            if sub_cur_index > len(sub_params) - 1:
                break
            pylint_ignore_file = sub_params[sub_cur_index]
            if pylint_path not in pylint_ignore_file:
                break
            sub_params.remove(pylint_ignore_file)
            pylint_ignore_file_list.append(
                os.path.split(pylint_ignore_file)[1])

        each_param = {"__PYLINT_PATH__": pylint_path,
                      "__PYLINT_IGNORE_PATH__": ",".join(pylint_ignore_file_list)}
        params_list.append(each_param)

    result = True
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures_pool = {executor.submit(
            single_pylint, cmd, params): params for params in params_list}
        for future in as_completed(futures_pool):
            if future.result() is False:
                result = False
    return result
