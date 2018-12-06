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
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(THIS_FILE_NAME)), ".."))

import comm.ci_log as cilog

CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(THIS_FILE_NAME)), "config")

class InstallationCommands(object):
    '''
    read commands from yaml file
    '''
    def __init__(self, command_file_name = None):
        self.commands = {}
        self.command_file_name = command_file_name
        self.error = False
        if self.command_file_name is None:
            self.command_file_name = "default"
        
        self.command_file = os.path.join(CONFIG_PATH, self.command_file_name + ".yaml")
        if not os.path.exists(self.command_file):
            self.error = True
            cilog.cilog_error(THIS_FILE_NAME, "command yaml file is not exist: %s", self.command_file)
            return
        cilog.cilog_debug(THIS_FILE_NAME, "read command yaml file: %s", self.command_file)
        
        try:
            stream = open(self.command_file, 'r')
            self.commands = yaml.load(stream)
        except OSError as reason:
            self.error = True
            cilog.cilog_error(THIS_FILE_NAME, "read command file failed: %s", reason)
        finally:
            #if stream in current symbol table:locals(), close it
            if stream in locals():
                stream.close()
            
    def get_install_commands(self):       
        if self.error:
            cilog.cilog_error(THIS_FILE_NAME, "no command yaml or config yaml not exist.");
            return False, None    
        commands = self.commands.get("install")
        return True, commands    
            
            
            
            