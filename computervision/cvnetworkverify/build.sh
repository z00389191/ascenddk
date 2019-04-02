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

app_type=$1

script_path="$( cd "$(dirname "$0")" ; pwd -P )"

# define supported type
declare -A type_flag=()
type_flag["classification"]="CLASSIFICATION"
type_flag["faster_rcnn"]="FASTER_RCNN"

function get_cc_flag(){
    for key in ${!type_flag[@]}
    do
        if [[ $1"X" == $key"X" ]]; then
            echo ${type_flag[$key]}
            break
        fi
    done
}

main()
{
    # check app_type
    cc_flag=`get_cc_flag $app_type`
    if [[ $cc_flag"X" == "X" ]]; then
        echo "please input correct app_type: [${!type_flag[@]}]"
        exit 1
    fi
    
    # check DDK_HOME
    if [ ! -n ${DDK_HOME} ];then
        echo "Can not find DDK_HOME env, please set it in environment!."
        exit 1
    fi
    
    # get target
    atlas_target=`grep "TARGET" ${DDK_HOME}/ddk_info | awk -F '"' '{print $4}'`
    if [[ $? -ne 0 ]];then
        echo "ERROR: can not get TARGET from ${DDK_HOME}/ddk_info, please check your env"
        exit 1
    fi
    # remove blank
    atlas_target=`echo ${atlas_target} | sed 's/ //g' `

    echo "Clear app build path..."
    rm -rf ${script_path}/cvnetworkverify/out

    echo "Build main..."
    make mode=${atlas_target} -C ${script_path}/cvnetworkverify 1>/dev/null
    if [ $? -ne 0 ];then
        exit 1
    fi

    for file in `find ${script_path}/cvnetworkverify -name "Makefile"`
    do
        if [ ${file} == "${script_path}/cvnetworkverify/Makefile" ];then
            continue
        fi
        path=`dirname ${file}`
        lib_path_name=`basename ${path}`
        echo "Build ${lib_path_name} lib..."
        make install mode=${atlas_target} CC_OPTS=${cc_flag} -C ${path} 1>/dev/null
        if [ $? -ne 0 ];then
            exit 1
        fi
    done
    
    # copy other file to out
    if [[ $app_type"X" == "classificationX" ]]; then
        cp ${script_path}/run_classification.py ${script_path}/cvnetworkverify/out
    else
        cp ${script_path}/run_object_detection_faster_rcnn.py ${script_path}/cvnetworkverify/out
    fi
    cp ${script_path}/cvnetworkverify/graph.template ${script_path}/cvnetworkverify/out

    echo "Finish to Build app."
    exit 0
}

main
