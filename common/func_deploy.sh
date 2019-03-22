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
    ret=`IDE-daemon-client --host $remote_host:$remote_port --hostcmd "wc -l ${filePath}"`
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
# ******************************************************************************
function upload_tar_gz_file()
{
    local_file=$1
    remote_path=$2

    file_name=`basename ${local_file}`
    remote_file="${remote_path}/${file_name}"

    upload_file ${local_file} ${remote_path}
    
    #uncompress tar.gz file
    ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "tar -zxvf ${remote_file} -C ${remote_path}/"`
    if [[ $? -ne 0 ]];then
        echo "ERROR: uncompress ${remote_host}:${remote_file} failed, please check /var/log/syslog for details."
    fi
    
    ret=`IDE-daemon-client --host ${remote_host}:${remote_port} --hostcmd "rm ${remote_file}"`
    if [[ $? -ne 0 ]];then
        echo "ERROR: delete ${remote_host}:${remote_file} failed, please check /var/log/syslog for details."
    fi
    
}

# ************************uplooad path****************************************
# Description:  upload a file
# $1: local path(absolute)
# $2: remote path
# ******************************************************************************
function upload_path()
{
    local_path=$1
    remote_path=$2
    file_list=`find ${local_path} -name "*"`
    for file in ${file_list}
    do
        remote_file=`echo ${file} | sed 's/${local_path}/${remote_path}'`
        remote_file_path=`dirname ${remote_file}`
        file_extension="${remote_file##*.}"
        
        if [[ ${file_extension} == "tar.gz" ]];then
            upload_tar_gz_file ${file} ${remote_file_path}
        else
            upload_file ${file} ${remote_file_path}
        fi
    done
}

# ************************deploy ***********************************************
# Description:  upload a file
# $1: app path(absolute)
# $2: common path(absolute)
# $3: remote_host(host ip)
# $4: remote port(IDE-daemon-client port)
# $5: model_version(none-no need to do model, empty-do with local model, 1.1.T8.xxxx-download from internet)
# ******************************************************************************
function deploy_app()
{
    app_name=$1
    app_path=$2
    common_path=$3
    remote_host=$4
    model_version=$5
    remote_port=$6
    
    if [ ! -n ${remote_port} ];then
        remote_port="22118"
    fi
    
    #build common
    bash ${common_path}/build.sh
    if [[ $? -ne 0 ]];then
        return 1
    fi
    
    #build app
    bash ${app_path}/build.sh
    if [[ $? -ne 0 ]];then
        return 1
    fi

    #prepare_model.sh: model_mode
    if [[ ${model_version} != "none" ]];then
        bash ${app_path}/prepare_model.sh ${mode_version}
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi

    #deploy commonmodel_version
    bash ${common_path}/deploy.sh ${remote_host} ${remote_port}
    if [[ $? -ne 0 ]];then
        return 1
    fi
    
    #deploy dataset
    if [ -d ${app_path}/MyDataset ];then
        upload_path ${app_path}/MyDataset "~/HIAI_DATANDMODELSET/workspace_mind_studio"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi

    #deploy models
    if [ -d ${app_path}/MyModel ];then
        upload_path ${app_path}/MyModel "~/HIAI_DATANDMODELSET/workspace_mind_studio"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi
    
    #deploy app
    if [ -d ${app_path}/out ];then
        upload_path ${app_path}/out "~/HIAI_PROJECTS/workspace_mind_studio/${app_name}/out"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi
    
    if [-d ${app_path}/${app_name}/out ];then
        upload_path ${app_path}/${app_name}/out "~/HIAI_PROJECTS/workspace_mind_studio/${app_name}/out"
        if [[ $? -ne 0 ]];then
            return 1
        fi
    fi
    
    #deploy graph
    if [ -f ${app_path}/graph.config ];then
        upload_file ${app_path}/graph.config "~/HIAI_PROJECTS/workspace_mind_studio/${app_name}/out"
    fi

    if [ -f ${app_path}/${app_name}/graph.config ];then
        upload_file ${app_path}/${app_name}/graph.config "~/HIAI_PROJECTS/workspace_mind_studio/${app_name}/out"
    fi
}