'''pylint check'''
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
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed
import os
import re
import sys

import comm.ci_log as cilog
import comm.util as util
import scripts_util as sc_util


THIS_FILE_NAME = __file__

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(THIS_FILE_NAME)), ".."))


def single_pylint(cmd, params):
    '''single pylint path check'''
    for key, value in params.items():
        cmd = re.sub(key, value, cmd)

    ret = util.execute(cmd, print_output_flag=True)

    # pylint check failed will return False
    if ret[0] is False:
        return False

    return True


def pylint(cmd, sub_params):
    '''check pylint'''
    ret = sc_util.find_checked_path()
    if ret is False:
        return False
    checked_path = ret[1]

    if checked_path is None:
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

    if init_path_list is None:
        cilog.cilog_info(THIS_FILE_NAME, "no path to check in pylint")
        return True
    if "" in init_path_list:
        init_path_list.remove("")
    init_path_list.sort()
    sub_params.sort()
    params_list = []
    init_length = len(init_path_list)
    for cur_index in range(init_length):
        if cur_index > len(init_path_list) - 1:
            break

        pylint_path = init_path_list[cur_index]

        next_index = cur_index + 1
        while True:
            if next_index > len(init_path_list) - 1 \
                or pylint_path not in init_path_list[next_index]:
                break
            init_path_list.remove(init_path_list[next_index])

        pylint_ignore_file_list = []
        sub_length = len(sub_params)
        for sub_cur_index in range(sub_length):
            if sub_cur_index > len(sub_params) - 1:
                break
            ignore_file = sub_params[sub_cur_index]
            pylint_ignore_file = sc_util.replace_env(ignore_file)
            if pylint_path not in pylint_ignore_file:
                break
            sub_params.remove(ignore_file)
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
