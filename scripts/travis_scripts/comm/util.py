'''common utils module'''
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
import platform
import signal
import subprocess
import time

import comm.ci_log as cilog


THIS_FILE_NAME = __file__


def execute(cmd, timeout=3600, print_output_flag=False, print_cmd=True, cwd=""):
    '''execute os command'''
    if print_cmd:
        if len(cmd) > 2000:
            cilog.print_in_color("%s ... %s" %
                                 (cmd[0:100], cmd[-100:]), cilog.COLOR_F_YELLOW)
        else:
            cilog.print_in_color(cmd, cilog.COLOR_F_YELLOW)

    is_linux = platform.system() == 'Linux'

    # 生成一个子进程，执行cmd命令
    if not cwd:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, cwd=cwd, bufsize=32768, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               preexec_fn=os.setsid if is_linux else None)

    # 判断子进程执行时间是否超时
    t_beginning = time.time()

    # 计算循环次数
    time_gap = 0.01

    str_std_output = ""
    while True:

        # 检查子进程是否结束
        str_out = str(process.stdout.read().decode())
        str_std_output = str_std_output + str_out

        if process.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:
            # 杀掉命令进程
            if is_linux:
                os.kill(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            cilog.cilog_error(THIS_FILE_NAME,
                              "execute %s timeout! excute seconds passed " \
                              " :%s, timer length:%s, return code %s",
                              cmd, seconds_passed, timeout, process.returncode)
            return False, process.stdout.readlines()
        time.sleep(time_gap)
    str_std_output = str_std_output.strip()
    std_output_lines_last = []
    std_output_lines = str_std_output.split("\n")
    for i in std_output_lines:
        std_output_lines_last.append(i)

    if process.returncode != 0 or "Traceback" in str_std_output:
        cilog.print_in_color(str_std_output, cilog.COLOR_F_RED)
        return False, std_output_lines_last

    if print_output_flag:
        cilog.print_in_color(str_std_output, cilog.COLOR_F_YELLOW)

    return True, std_output_lines_last
