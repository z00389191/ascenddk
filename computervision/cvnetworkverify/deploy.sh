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

remote_host=$1
app_type=$2

script_path="$( cd "$(dirname "$0")" ; pwd -P )"
common_path="${script_path}/../../common"

. ${common_path}/utils/scripts/func_deploy.sh
. ${common_path}/utils/scripts/func_util.sh

# define supported type
type_array=("classfication" "faster_rcnn")

# ******************************************************************************
# Description: check app type
# param $1: app_type
# ******************************************************************************
function check_app_type(){
    type=$1
    for var in ${type_array[@]}
    do
        if [[ $type"X" == $var"X" ]]; then
            return 0
        fi
    done
    return 1
}

# ******************************************************************************
# Description:  deploy computer vision network verify demo
# ******************************************************************************
function deploy_cvverify()
{
    #set remote_port
    parse_remote_port

    #build common
    echo "[Step] Build common libs..."
    bash ${common_path}/build.sh "libascend_ezdvpp.so"
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #build app
    echo "[Step] Build app libs..."
    bash ${script_path}/build.sh $app_type
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #deploy common libs
    echo "[Step] Deploy common libs..."
    bash ${common_path}/deploy.sh ${remote_host} "libascend_ezdvpp.so"
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #deploy app
    if [ -d ${script_path}/cvnetworkverify/out ];then
        echo "[Step] Deploy app libs..."
        upload_path ${script_path}/cvnetworkverify/out "~/HIAI_PROJECTS/ascend_workspace/cvnetworkverify/out"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi
}

main()
{
    check_ip_addr ${remote_host}
    if [[ $? -ne 0 ]];then
        echo "ERROR: invalid host ip, please check your command."
        exit 1
    fi
    
    check_app_type ${app_type}
    if [[ $? -ne 0 ]];then
        echo "ERROR: invalid app type, please input type as [${type_array[@]}]."
        exit 1
    fi
    
    deploy_cvverify
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    
    echo "Finish to deploy cvnetworkverify."
    exit 0
}

main