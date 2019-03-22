#!/bin/bash
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

# ************************Variable*********************************************

script_path="$( cd "$(dirname "$0")" ; pwd -P )"

compilation_target=$1

. ${script_path}/func_libraries.sh

function compile()
{
    libs=$1
    atlas_target=$2
    for lib_name in ${libs}
    do
        echo "Build ${lib_name}..."
        echo "${host_libraries[@]}" | grep "${lib_name}" 1>/dev/null
        if [ $? -eq 0 ];then
            lib_path=${host_map[${lib_name}]}
            make clean mode=${atlas_target} -C ${lib_path} 1>/dev/null
            if [[ $? -ne 0 ]];then
                echo "ERROR: compile ${lib_name} failed, please check the env."
                return 1
            fi
            make install mode=${atlas_target} -C ${lib_path} 1>/dev/null
            if [[ $? -ne 0 ]];then
                echo "ERROR: compile ${lib_name} failed, please check the env."
                return 1
            fi
        fi
        
        echo "${device_libraries[@]}" | grep "${lib_name}" 1>/dev/null
        if [ $? -eq 0 ];then
            lib_path=${device_map[${lib_name}]}
            make clean mode=${atlas_target} -C ${lib_path} 1>/dev/null
            if [[ $? -ne 0 ]];then
                echo "ERROR: compile ${lib_name} failed, please check the env."
                return 1
            fi
            make install mode=${atlas_target} -C ${lib_path} 1>/dev/null
            if [[ $? -ne 0 ]];then
                echo "ERROR: compile ${lib_name} failed, please check the env."
                return 1
            fi
        fi
    done
}

main()
{
    libs=`get_compilation_targets ${compilation_target}`
    if [[ $? -ne 0 ]];then
        echo "ERROR: unknown compilation target, please check your command."
        exit 1
    fi
    
    atlas_target=`grep "TARGET" ${DDK_HOME}/ddk_info | awk -F '"' '{print $4}'`
    if [[ $? -ne 0 ]];then
        echo "ERROR: can not get TARGET from ${DDK_HOME}/ddk_info, please check your env"
    fi
    
    #remove blank
    atlas_target=`echo ${atlas_target} | sed 's/ //g' `
    compile "${libs}" ${atlas_target}
    echo "Finish to build common libs."
    exit 0
}

main
