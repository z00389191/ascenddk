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
import platform
import subprocess
import time
import os
import signal

import comm.ci_log as cilog
from comm.ci_log import COLOR_F_RED

THIS_FILE_NAME = __file__


def execute(cmd, timeout=3600, print_output_flag=False, print_cmd=True, cwd=""):
    if print_cmd:
        if len(cmd) > 200:
            cilog.cilog_info_color(
                THIS_FILE_NAME, cilog.COLOR_F_YELLOW, "execute the cmd: %s ... %s", cmd[0:100], cmd[-100:])
        else:
            cilog.cilog_info_color(
                THIS_FILE_NAME, cilog.COLOR_F_YELLOW, "execute the cmd: %s", cmd)

    is_linux = platform.system() == 'Linux'

    # 生成一个子进程，执行cmd命令
    if not cwd:
        cwd = os.getcwd()
    p = subprocess.Popen(cmd, cwd=cwd, bufsize=32768, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, shell=True,
                         preexec_fn=os.setsid if is_linux else None)

    # 判断子进程执行时间是否超时
    t_beginning = time.time()

    # 计算循环次数
    time_gap = 0.01
    loop = timeout * 100 + 200

    str_std_output = ""
    for loop_index in range(0, loop):

        # 检查子进程是否结束
        str_std_output = str_std_output + str(p.stdout.read())
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:
            # 杀掉命令进程
            if is_linux:
                os.kill(p.pid, signal.SIGTERM)
            else:
                p.terminate()
            cilog.cilog_error(THIS_FILE_NAME,
                              "execute %s timeout! excute seconds passed :%s, timer length:%s, return code %s",
                              cmd, seconds_passed, timeout, p.returncode)
            return False, p.stdout.readlines()
        time.sleep(time_gap)

    std_output_lines_last = []
    std_output_lines = str_std_output.split("\n")
    for i in std_output_lines:
        std_output_lines_last.append(i + "\n")

    if p.returncode != 0 or "Traceback" in str_std_output:
        cilog.print_in_color(str_std_output, cilog.COLOR_F_RED)
        cilog.cilog_info(
            THIS_FILE_NAME, "execute, return code: %s", p.returncode)
        return False, std_output_lines_last
    else:
        if print_output_flag:
            cilog.print_in_color(str_std_output, cilog.COLOR_F_YELLOW)        
            cilog.cilog_info(
                THIS_FILE_NAME, "execute, return code: %s", p.returncode)
    return True, std_output_lines_last
