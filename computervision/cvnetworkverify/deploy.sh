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
type_array=("classification" "faster_rcnn")

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

    #deploy thirdparty app
    atlas_target=`grep "TARGET" ${DDK_HOME}/ddk_info | awk -F '"' '{print $4}'`
    if [[ $? -ne 0 ]];then
        echo "ERROR: can not get TARGET from ${DDK_HOME}/ddk_info, please check your env"
        return 1
    fi
    
    #set remote_port
    parse_remote_port

    #build common
    echo "[Step] Build common libs..."
    bash ${common_path}/build.sh "libascend_ezdvpp.so"
    if [[ $? -ne 0 ]];then
        return 1
    fi

    

    #build third_party
    if [[ ${atlas_target} == "ASIC" ]];then
        echo "[Step] Build third party libs..."
        bash ${script_path}/build_opencv.sh
        if [[ $? -ne 0 ]];then
            return 1
        fi
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

    if [[ ${atlas_target} == "ASIC" ]];then
        echo "[Step] Deploy third party libs..."
        upload_tar_file "${script_path}/opencv_lib.tar" "~/HIAI_PROJECTS/ascend_lib"
    fi
    #deploy app
    if [ -d ${script_path}/cvnetworkverify/out ];then
        echo "[Step] Deploy app libs..."
        iRet=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "rm -rf ~/HIAI_PROJECTS/ascend_workspace/cvnetworkverify"`
        if [[ $? -ne 0 ]];then
            echo "ERROR: delete ${remote_host}:./HIAI_PROJECTS/ascend_workspace/cvnetworkverify failed, please check /var/log/syslog for details."
            return 1
        fi
        upload_path ${script_path}/cvnetworkverify/out "~/HIAI_PROJECTS/ascend_workspace/cvnetworkverify/out"
        if [[ $? -ne 0 ]];then
            return 1
        fi
        iRet=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "chmod +x ~/HIAI_PROJECTS/ascend_workspace/cvnetworkverify/out/ascend_cvnetworkverify"`
        if [[ $? -ne 0 ]];then
            echo "ERROR: change excution mode ${remote_host}:./HIAI_PROJECTS/ascend_workspace/cvnetworkverify/out/* failed, please check /var/log/syslog for details."
            return 1
        fi
    fi
}

main()
{
    if [[ $# -lt 2 ]];then
        echo "ERROR: invalid command, please check your command format: ./deploy.sh host_ip app_type"
        exit 1
    fi

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

main $*
