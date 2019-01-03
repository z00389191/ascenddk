"""presenter server module"""

#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
#   =======================================================================
#
# Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1 Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================
#
import os
import sys
import signal
import logging
from logging.config import fileConfig
import face_detection.src.webapp as webapp
from face_detection.src.config_parser import ConfigParser
from common.presenter_socket_server import PresenterSocketServer
from common.channel_manager import ChannelManager

# global variable, SOCKET_SERVER is a thread server
# for presenter agent communication
SOCKET_SERVER = None

def config_log():
    '''config log based on log config file'''
    log_file_path = os.path.join(ConfigParser.root_path, "config/logging.conf")
    fileConfig(log_file_path)
    logging.getLogger('presenterserver')

def close_all_thread(signum, frame):
    '''close all thread of the process, and exit.'''
    logging.info("receive signal, signum:%s, frame:%s", signum, frame)
    webapp.stop_webapp()
    SOCKET_SERVER.stop_thread()
    channel_manager = ChannelManager()
    channel_manager.close_all_thread()
    logging.info("presenter server exit by Ctrl + c")

    sys.exit()

def main_process():
    '''Main function entrance'''

    # read config file
    config = ConfigParser()
    if not config.config_verify():
        return False

    # config log
    config_log()

    # start socket server for presenter agent communication
    global SOCKET_SERVER
    SOCKET_SERVER = PresenterSocketServer((config.presenter_server_ip,
                                           config.presenter_server_port))


    # process signal, when receive "Ctrl + c" signal,
    # stop all thead and exit the progress.
    signal.signal(signal.SIGINT, close_all_thread)
    signal.signal(signal.SIGTERM, close_all_thread)

    logging.info("presenter server is starting...")

    # start http server
    webapp.start_webapp()
    return True

def _module_name():
    return __name__

def main():
    '''Main function entrance'''
    module_name = _module_name()
    if module_name == '__main__':
        main_process()

# start here
main()
