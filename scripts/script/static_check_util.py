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
ENV_DICT = {"\$\{BUILD_TEMP_PATH\}" : os.getenv("BUILD_TEMP_PATH"),
            "\$\{ASCEND_ROOT_PATH\}" : os.getenv("ASCEND_ROOT_PATH")}

def replace_env(file_name):
    for key, value in ENV_DICT.items():
        file_name = re.sub(key, value, file_name)
    return file_name

def check_file_is_empty(file_name):
    
    #replace env in the file_name
    file_name = replace_env(file_name)
    if os.path.getsize(file_name) == FILE_EMPTY_SIZE:
        return True
    else:
        return False

def get_compiler_headers():
    ddk_root_path = os.getenv("DDK_ROOT_PATH")
    cmd = "find " + ddk_root_path + "/include/ -type d -print"
    return util.execute(cmd)


def warn_check(file_name, cmd):
    file_name = replace_env(file_name)
    if not os.path.exists(file_name):
        cilog.cilog_error(THIS_FILE_NAME, "can not find cpp list file: %s", file_name)
        return False;
    
    ret, header_list = get_compiler_headers()
    
    if not ret:
        cilog.cilog_error(THIS_FILE_NAME, "get ddk headers failed.")
        return False
    
    headers = " -I".join(header_list)
    headers = "-I" + headers
    cmd = re.sub("__WARN_CHECK_HEADERS__", headers, cmd)
    try:
        checked_file = open(file_name, 'r')
        while True:
            files = checked_file.readlines(100000)
            if not files:
                break
            for file in files:
                temp_cmd = re.sub("__WARN_CHECK_FILE__", file, cmd)
                ret = util.execute(temp_cmd, print_output_flag=True)
    except OSError as reason:
        cilog.cilog_error(THIS_FILE_NAME, "open file failed: %s", reason)
        return False
    finally:
        if checked_file in locals():
            checked_file.close()
    return True