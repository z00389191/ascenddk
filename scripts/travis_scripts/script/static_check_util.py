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

import comm.ci_log as cilog
import comm.util as util


THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))


FILE_EMPTY_SIZE = 0

GLOBAL_IGNORE_PATH = [os.path.join(os.getenv("ASCENDDK_ROOT_PATH"), "ascenddk/test"),
                      os.path.join(os.getenv("ASCENDDK_ROOT_PATH"),
                                   "ascenddk/scripts"),
                      os.path.join(os.getenv("ASCENDDK_ROOT_PATH"), "ascenddk/.git")]

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


def find_checked_path():
    checked_path_cmd = "find " + os.path.join(os.getenv(
        "ASCEND_ROOT_PATH"), "ascenddk") + " -maxdepth 1 -mindepth 1  -type d -print"
    ret = util.execute(checked_path_cmd, print_output_flag=True)
    if ret[0] is False:
        return False, []
    found_path = []
    for each_path in ret[1]:
        if each_path not in GLOBAL_IGNORE_PATH:
            found_path.append(each_path)

    return True, found_path
