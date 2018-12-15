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

import yaml

import comm.ci_log as cilog
import comm.util as util


def main():
    base_path = os.path.dirname(
        os.path.realpath(__file__))
    ret = util.execute("git branch", cwd=base_path)

    if ret[0] is False:
        exit(-1)

    branch_info = ret[1]
    code_branch = branch_info[0].split(" ")[1]
    cilog.print_in_color(code_branch, cilog.COLOR_F_YELLOW)

    file_path = os.path.join(base_path, "../../.travis.yml")

    try:
        file_stream = open(file_path, 'r')
        travis_dict = yaml.load(file_stream)
        env_variables = travis_dict.get("env")
    except OSError as reason:
        print(reason)
        exit(-1)
    finally:
        if file_stream in locals():
            file_stream.close()
    try:
        env_variables_list = env_variables.split(" ")

        env_variables_list.append("TRAVIS_BRANCH=" + code_branch)

        env_variables_list = list(
            map(lambda x: "export " + x + "\n", env_variables_list))
        cilog.print_in_color("env list: %s" %
                             env_variables_list, cilog.COLOR_F_YELLOW)
        env_file = os.path.join(os.getenv("HOME"), ".bashrc_ascend")
        env_stream = open(env_file, 'w')
        env_stream.writelines(env_variables_list)
    except OSError as reason:
        print(reason)
        exit(-1)
    finally:
        if env_stream in locals():
            env_stream.close()

    # add env to bashrc
    bashrc_file = os.path.join(os.getenv("HOME"), ".bashrc")
    try:
        bashrc_read_stream = open(bashrc_file, 'r')
        all_lines = []
        while True:
            lines = bashrc_read_stream.readlines(10000)
            if not lines:
                break
            all_lines.extend(lines)
    except OSError as reason:
        print(reason)
        exit(-1)
    finally:
        if bashrc_read_stream in locals():
            bashrc_read_stream.close()
    # if bashrc haven been added, skip it
    if ". ~/.bashrc_ascend" not in all_lines:
        try:
            bashrc_write_stream = open(bashrc_file, 'a')
            bashrc_write_stream.write(". ~/.bashrc_ascend")
        except OSError as reason:
            print(reason)
        finally:
            if bashrc_write_stream in locals():
                bashrc_write_stream.close()


if __name__ == '__main__':
    main()
