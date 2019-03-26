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

remote_host=$1
compilation_target=$2

HOST_LIB_PATH="${HOME}/ascend_ddk/device/lib"
DEVICE_LIB_PATH="${HOME}/ascend_ddk/device/lib"

. ${script_path}/utils/scripts/func_libraries.sh
. ${script_path}/utils/scripts/func_deploy.sh
. ${script_path}/utils/scripts/func_util.sh

function deploy()
{
    libs=$1
    for lib_name in ${libs}
    do
        echo "${host_libraries[@]}" | grep "${lib_name}" 1>/dev/null
        if [ $? -eq 0 ];then
            upload_file "${HOST_LIB_PATH}/${lib_name}" "~/HIAI_PROJECTS/ascend_lib"
            if [ $? -ne 0 ];then
                return 1
            fi
        fi

        echo "${device_libraries[@]}" | grep "${lib_name}" 1>/dev/null
        if [ $? -eq 0 ];then
            upload_file "${DEVICE_LIB_PATH}/${lib_name}" "~/HIAI_PROJECTS/ascend_lib"
            if [ $? -ne 0 ];then
                return 1
            fi
        fi
    done
    echo "Finish to upload libs."
    return 0
}

main()
{
    check_ip_addr ${remote_host}
    if [[ $? -ne 0 ]];then
        echo "ERROR: invalid host ip, please check your command format: ./deploy.sh host_ip [lib_name]."
        exit 1
    fi
    #deploy
    libs=`get_compilation_targets ${compilation_target}`
    if [[ $? -ne 0 ]];then
        echo "ERROR: unknown compilation target, please check your command format: ./deploy.sh host_ip [lib_name]."
        exit 1
    fi

    #parse remote port
    parse_remote_port

    deploy "${libs}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    exit 0
}

main
