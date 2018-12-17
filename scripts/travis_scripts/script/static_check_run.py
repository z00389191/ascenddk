'''static check'''
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
import operator
import os
import re
import sys

THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))

import comm.ci_log as cilog
import comm.util as util


from static_check_commands import StaticCheckCommands
from static_check_pylint import pylint
from static_check_util import check_file_is_empty
from static_check_warn_check import filter_warn_check_is_none
from static_check_warn_check import warn_check


def static_check_func(command, sub_params):
    '''static check in function mode'''
    function_name = command.get("function_name")
    params = command.get("params")
    sub_commands = None
    if "sub_params" in command.keys():
        sub_commands = sub_params.get(command.get("sub_params"))
    args = []
    kwargs = {}
    if isinstance(params, list):
        args.extend(params)
        if sub_commands is not None:
            args.append(sub_commands)
    elif isinstance(params, dict):
        if sub_commands is not None:
            kwargs["sub_params"] = sub_commands
        kwargs.update(params)
    else:
        cilog.cilog_error(THIS_FILE_NAME, "unsuppoted sub commands type")
        return False

    cilog.cilog_info(
        THIS_FILE_NAME,
        "execute the func: %s(%s, %s)", function_name, args, kwargs)

    ret = eval(function_name)(*args, **kwargs)

    expected_result = command.get("expected_result")

    result = True
    # not break here, finish every check
    if ret == expected_result:
        cilog.cilog_info(
            THIS_FILE_NAME,
            "execute the func as expected_result: %s", expected_result)
    else:
        cilog.cilog_error(
            THIS_FILE_NAME, "execute the func failed: actural result: %s,"
            " expected_result: %s", ret, expected_result)
        result = False
    return result


def static_check_cmd(command, sub_params):
    '''static check in command mode'''
    cmd = command.get("cmd")
    sub_commands = None
    if "sub_params" in command.keys():
        sub_commands = sub_params.get(command.get("sub_params"))

    replaced_vars = re.findall(r"(__[\w+_\w+]*__)", cmd)
    replaced_vars.sort()
    vars_length = len(replaced_vars)

    result = True
    if sub_commands is None and vars_length != 0:
        cilog.cilog_error(
            THIS_FILE_NAME, "sub commands %s is not match" \
            " replaced vars length %s", sub_commands, vars_length)
        result = False
    elif sub_commands is None and vars_length == 0:
        ret = util.execute(cmd, print_output_flag=True)
        result = ret[0]
    else:
        if isinstance(sub_commands, list):
            for each_arg in sub_commands:
                args = each_arg.split()
                if vars_length != len(args):
                    cilog.cilog_error(
                        THIS_FILE_NAME, "sub commands %s is not match" \
                        " replaced vars length %s", sub_commands, vars_length)
                    return False
                temp_cmd = cmd
                for index in range(0, len(replaced_vars)):
                    temp_cmd = re.sub(
                        replaced_vars[index], args[index], temp_cmd)

                ret = util.execute(temp_cmd, print_output_flag=True)

                # not return here, check every args
                if not ret[0]:
                    result = False
        elif isinstance(sub_commands, dict):
            for each_arg in sub_commands:
                if len(replaced_vars) != len(each_arg):
                    cilog.cilog_error(
                        THIS_FILE_NAME, "sub commands %s is not match" \
                        " replaced vars length %s", sub_commands, vars_length)
                    return False
                key_list = each_arg.keys().sort()
                if not operator.eq(replaced_vars, key_list):
                    cilog.cilog_error(
                        THIS_FILE_NAME, "sub commands %s is not match" \
                        " replaced vars %s", key_list, replaced_vars)
                    return False
                temp_cmd = cmd

                # replace all parameters in the command
                for param_key, param_value in each_arg.items():
                    if param_value is None:
                        param_value = ""
                    temp_cmd = re.sub(param_key, param_value, temp_cmd)

                ret = util.execute(temp_cmd, print_output_flag=True)

                # not return here, check every args
                if not ret[0]:
                    result = False
        else:
            cilog.cilog_error(THIS_FILE_NAME, "unsuppoted sub commands type")
            result = False

    if not result:
        cilog.cilog_error(THIS_FILE_NAME, "static check failed.")

    return result


def main():
    '''static check'''
    check_type = os.sys.argv[1]

    static_check_commands = StaticCheckCommands(check_type)
    ret, commands = static_check_commands.get_commands()
    if not ret:
        exit(-1)
    ret, sub_params = static_check_commands.get_sub_params()
    if not ret:
        exit(-1)

    for command_dict in commands:
        comand_type = command_dict.get("type")
        if comand_type == "command":
            ret = static_check_cmd(command_dict, sub_params)
            if not ret:
                exit(-1)
        elif comand_type == "function":
            ret = static_check_func(command_dict, sub_params)
            if not ret:
                exit(-1)
        else:
            cilog.cilog_error(
                THIS_FILE_NAME, "unsupported command: %s", command_dict)
            exit(-1)
    exit(0)


if __name__ == '__main__':
    main()
