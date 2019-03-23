
# ************************parse remote port****************************************
# Description:  parse remote port
# ******************************************************************************
function parse_remote_port()
{
    remote_port=`grep HOST_PORT ~/ide_daemon/ide_daemon.cfg | awk -F '=' '{print $2}'`

    if [[ ${remote_port}"X" == "X" ]];then
        remote_port="22118"
    fi
}

# ************************check remote file****************************************
# Description:  upload a file
# $1: remote file(relative ~/xxxxx)
# ******************************************************************************
function check_remote_file()
{
    filePath=$1
    if [ ! -n ${filePath} ];then
        return 1
    fi
    ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "wc -l ${filePath}"`
    if [[ $? -ne 0 ]];then
        return 1
    fi

    return 0
}


# ************************uplooad file****************************************
# Description:  upload a file
# $1: local file(absolute)
# $2: remote file path
# ******************************************************************************
function upload_file()
{
    local_file=$1
    remote_path=$2

    file_name=`basename ${local_file}`
    remote_file="${remote_path}/${file_name}"

    #check remote path
    check_remote_file ${remote_file}

    #check whether overwrite remote file
    if [[ $? -eq 0 ]];then
        if [[ ${is_overwrite} == "false" ]];then
            echo "${remote_file} already exists, skip to upload it."
            return 0
        else
            ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "rm ${remote_file}"`
            if [[ $? -ne 0 ]];then
                echo "ERROR: delete ${remote_host}:${remote_file} failed, please check /var/log/syslog for details."
                return 1
            fi
        fi
    fi

    ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "mkdir -p ${remote_path}"`
    if [[ $? -ne 0 ]];then
        echo "ERROR: mkdir ${remote_host}:${remote_path} failed, please check /var/log/syslog for details."
        return 1
    fi

    #copy to remote path
    ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --sync ${local_file} ${remote_path}`
    if [[ $? -ne 0 ]];then
        echo "ERROR: sync ${local_file} to ${remote_host}:${remote_path} failed, please check /var/log/syslog for details."
    fi
}

# ************************uplooad tar.gz file****************************************
# Description:  upload a file
# $1: local file(absolute)
# $2: remote path
# $3: is_uncompress(true/false, default:true)
# ******************************************************************************
function upload_tar_gz_file()
{
    local_file=$1
    remote_path=$2

    file_name=`basename ${local_file}`
    remote_file="${remote_path}/${file_name}"

    upload_file ${local_file} ${remote_path}

    #uncompress tar.gz file
    if [[ ${is_uncompress}"X" != "falseX" ]];then
        ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "tar -zxvf ${remote_file} -C ${remote_path}/"`
        if [[ $? -ne 0 ]];then
            echo "ERROR: uncompress ${remote_host}:${remote_file} failed, please check /var/log/syslog for details."
        fi

        ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "rm ${remote_file}"`
        if [[ $? -ne 0 ]];then
            echo "ERROR: delete ${remote_host}:${remote_file} failed, please check /var/log/syslog for details."
        fi
    fi

}

# ************************uplooad path****************************************
# Description:  upload a file
# $1: local path(absolute)
# $2: remote path
# $3: ignore_local_path(true/false, default=false)
#    #${local_path}
#    #      |-----path1
#    #              |-----path11
#    #                        |----file1
#    #      |-----path2
#    #              |-----file2
#    #true: upload file1 to ${remote_path}/file1
#    #      upload file2 to ${remote_path}/file2
#    #false/empty: upload file1 upload to ${remote_path}/path1/path11/file1
#    #             upload file2 to ${remote_path}/path2/file2
# $4: is_uncompress(true/fase, default:true)
# ******************************************************************************
function upload_path()
{
    local_path=$1
    remote_supper_path=$2
    ignore_local_path=$3
    is_uncompress=$4

    file_list=`find ${local_path} -name "*"`
    for file in ${file_list}
    do
        if [[ -d ${file} ]];then
            continue
        fi
        file_extension="${file##*.}"
        
        if [[ ${ignore_local_path}"X" == "trueX" ]];then
            remote_file_path=${remote_supper_path}
        else
            remote_file=`echo ${file} | sed "s#${local_path}#${remote_supper_path}#g"`
            remote_file_path=`dirname ${remote_file}`
        fi

        if [[ ${file_extension} == "tar.gz" ]];then
            upload_tar_gz_file ${file} ${remote_file_path} ${is_uncompress}
            if [[ $? -ne 0 ]];then
                return 1
            fi
        else
            upload_file ${file} ${remote_file_path}
            if [[ $? -ne 0 ]];then
                return 1
            fi
        fi
    done
    
    return 0
}

# ************************deploy ***********************************************
# Description:  upload a file
# $1: app_name
# $2: app path(absolute)
# $3: common path(absolute)
# $4: remote_host(host ip)
# $5: model_mode(none-no need to do model, local-do with local model, internet-download model based on ddk version)
# ******************************************************************************
function deploy_app()
{
    app_name=$1
    app_path=$2
    common_path=$3
    remote_host=$4
    model_mode=$5

    #set remote_port
    parse_remote_port

    #build common
    echo "[Step] Build common libs..."
    bash ${common_path}/build.sh
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #build app
    echo "[Step] Build app libs..."
    bash ${app_path}/build.sh
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #prepare_model.sh: model_mode
    if [[ ${model_mode} != "none" ]];then
        echo "[Step] Prepare models..."
        if [[ ${model_mode} == "local" ]];then
            model_version=""
        else
            model_version=`grep VERSION ${DDK_HOME}/ddk_info | awk -F '"' '{print $4}'`
            if [[ $? -ne 0 ]];then
                echo "ERROR: can not get version in ${DDK_HOME}/ddk_info, please check your env."
                return 1
            fi
        fi
        bash ${app_path}/prepare_model.sh ${model_version}
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi

    #deploy common libs
    echo "[Step] Deploy common libs..."
    bash ${common_path}/deploy.sh ${remote_host}
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #deploy dataset
    if [ -d ${app_path}/MyDataset ];then
        echo "[Step] Deploy dataset..."
        upload_path ${app_path}/MyDataset "~/HIAI_DATANDMODELSET/ascend_workspace"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi

    #deploy models
    if [ -d ${app_path}/MyModel ];then
        echo "[Step] Deploy models..."
        upload_path ${app_path}/MyModel "~/HIAI_DATANDMODELSET/ascend_workspace" "true"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi

    if [ -d ${app_path}/${app_name}/out ];then
        echo "[Step] Deploy app libs..."
        upload_path ${app_path}/${app_name}/out "~/HIAI_PROJECTS/ascend_workspace/${app_name}/out"
        if [[ $? -ne 0 ]];then
            return 1
        fi
        iRet=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "chmod +x ~/HIAI_PROJECTS/ascend_workspace/${app_name}/out/*"`
        if [[ $? -ne 0 ]];then
            echo "ERROR: change excution mode ${remote_host}:./HIAI_PROJECTS/ascend_workspace/${app_name}/out/* failed, please check /var/log/slog for details."
            return 1
        fi
    fi
    return 0
}