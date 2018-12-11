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

import comm.util as util


def main():
    ret = util.execute("git branch")

    if ret[0] is False:
        exit(-1)

    branch_info = ret[1]
    code_branch = branch_info[0]
    print(code_branch)

    file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "../../.travis.yml")

    try:
        file_stream = open(file_path, 'r')
        travis_dict = yaml.load(file_stream)
        env_varaibles = travis_dict.get("env")
        env_varaibles.append("TRAVIS_BRANCH=" + code_branch)

        env_varaibles = list(map(lambda x: "export " + x, env_varaibles))

        env_file = os.path.join(os.getenv("HOME"), ".bashrc_rc")
        env_stream = open(env_file, 'w')
        env_stream.write_array(env_varaibles)

        bashrc_file = os.path.join(os.getenv("HOME"), ".bashrc")
        bashrc_read_stream = open(bashrc_file, 'r')
        all_lines = []
        while True:
            lines = bashrc_read_stream.readlines(10000)
            if not lines:
                break
            all_lines.extend(lines)
        if ". ~/.bashrc" not in all_lines:
            bashrc_write_stream = open(bashrc_file, 'a')
            bashrc_write_stream.write(". ~/.bashrc")
    except OSError as reason:
        print(reason)
    finally:
        if file_stream in locals():
            file_stream.close()
        if env_stream in locals():
            env_stream.close()
        if bashrc_read_stream in locals():
            bashrc_read_stream.close()
        if bashrc_write_stream in locals():
            bashrc_write_stream.close()


if __name__ == '__main__':
    main()
