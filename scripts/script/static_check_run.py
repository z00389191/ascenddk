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
import sys
import re

from static_check_commands import StaticCheckCommands
from static_check_util import check_file_is_empty
from static_check_util import warn_check

THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))

import comm.util as util
import comm.ci_log as cilog

def static_check_func(command):
    function_name = command.get("function_name")

    if "args" in command:
        args = command.get("args")
    else:
        args = []

    if "kwargs" in command:
        kwargs = command.get("kwargs")
    else:
        kwargs = {}

    cilog.cilog_info_color(
        THIS_FILE_NAME, cilog.COLOR_F_YELLOW,
        "execute the func: %s(%s, %s)", function_name, args, kwargs)

    ret = eval(function_name)(*args, **kwargs)

    expected_result = command.get("expected_result")

    if ret == expected_result:
        cilog.cilog_info(
            THIS_FILE_NAME,
            "execute the func as expected_result: %s", expected_result)
        return True
    else:
        cilog.cilog_error(
            THIS_FILE_NAME, "execute the func failed: actural result: %s,"
            " expected_result: %s", ret, expected_result)
        return False

def static_check_cmd(command):
    cmd = command.get("cmd")
    args = command.get("args")
    result = True
    if args is None:
        ret = util.execute(cmd, print_output_flag=True)
        result = ret[0]
    else:
        for each_arg in args:
            #replace all parameters in the command
            for param_key, param_value in each_arg.items():
                if param_value is None:
                    param_value = ""
                cmd = re.sub(param_key, param_value, cmd)
            
            ret = util.execute(cmd, print_output_flag=True)
            
            #not return here, check every args
            if not ret[0]:
                result = False

    if not result:
        cilog.cilog_error(THIS_FILE_NAME, "static check failed.")

    return result

def main():
    check_type = os.sys.argv[1]

    static_check_commands = StaticCheckCommands(check_type)
    ret, commands = static_check_commands.get_commands()
    if not ret:
        exit(-1)

    for command_dict in commands:
        comand_type = command_dict.get("type")
        command = command_dict.get("command")
        if comand_type == "command":
            ret = static_check_cmd(command)
            if not ret:
                exit(-1)
        elif comand_type == "function":
            ret = static_check_func(command)
            if not ret:
                exit(-1)
        else:
            cilog.cilog_error(
                THIS_FILE_NAME, "unsupported command: %s", command_dict)
            exit(-1)
    exit(0)


if __name__ == '__main__':
    main()
