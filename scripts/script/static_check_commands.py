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
import yaml

THIS_FILE_NAME = __file__
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))

import comm.ci_log as cilog

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), "config")


class StaticCheckCommands(object):
    '''
    read commands from yaml file
    '''

    def __init__(self, command_type):
        self.commands = {}
        self.command_type = command_type
        self.error = False

        self.static_check_command_file = os.path.join(
            CONFIG_PATH, "static_check.yaml")
        if not os.path.exists(self.static_check_command_file):
            self.error = True
            cilog.cilog_error(
                THIS_FILE_NAME, "static check file is not exist: static_check.yaml")

        self.command_file = os.path.join(
            CONFIG_PATH, "static_check_" + self.command_type + ".yaml")
        if not os.path.exists(self.command_file):
            self.error = True
            cilog.cilog_error(
                THIS_FILE_NAME, "command yaml file is not exist: %s", self.command_file)
            return
        cilog.cilog_debug(
            THIS_FILE_NAME, "read command yaml file: %s__%s", self.static_check_command_file, self.command_file)

        try:
            static_stream = open(self.static_check_command_file, 'r')
            sub_stream = open(self.command_file, 'r')
            static_dict = yaml.load(static_stream)
            sub_dict = yaml.load(sub_stream)
            command_list = static_dict.get(command_type)

            for command in command_list:
                arg_name = command.get("arg_name")
                args = sub_dict.get(arg_name)
                if args is None:
                    self.error = True
                    cilog.cilog_error(
                THIS_FILE_NAME, "args in %s is invalid", self.command_file)
                    return
                for key, value in args.items():
                    command[key] = value
            self.commands = command_list
            self.validate_commands()
        except OSError as reason:
            self.error = True
            cilog.cilog_error(
                THIS_FILE_NAME, "read command file failed: %s", reason)
        finally:
            # if stream in current symbol table:locals(), close it
            if static_stream in locals():
                static_stream.close()
            if sub_stream in locals():
                sub_stream.close()

    def get_commands(self):
        if self.error is True:
            cilog.cilog_error(
                THIS_FILE_NAME, "get command failed.")
            return False, None
        return True, self.commands

    def validate_commands(self):
        for each_command in self.commands:
            command_type = each_command.get("type")
            if command_type is None:
                cilog.cilog_error(
                    THIS_FILE_NAME, "type is invalid: %s", each_command)
                self.error = True
                break

            command = each_command.get("command")
            if command is None:
                cilog.cilog_error(
                    THIS_FILE_NAME, "command is invalid: %s", each_command)
                self.error = True
                break
            if command_type == "command":
                if "cmd" not in command.keys():
                    cilog.cilog_error(
                        THIS_FILE_NAME, "cmd is invalid: %s", each_command)
                    self.error = True
                    break
            elif command_type == "function":
                if "function_name" not in command.keys():
                    cilog.cilog_error(
                        THIS_FILE_NAME, "function_name is invalid: %s", each_command)
                    self.error = True
                    break
            else:
                cilog.cilog_error(
                    THIS_FILE_NAME, "type is invalid: %s", each_command)
                self.error = True
                break
