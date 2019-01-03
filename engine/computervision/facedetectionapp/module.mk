LOCAL_PATH := $(call my-dir)

## face detection post process
include $(CLEAR_VARS)
local_lib_inc_path := $(TOPDIR)inc \
                      $(TOPDIR)inc/custom \
                      $(TOPDIR)libc_sec/include \
                      $(TOPDIR)third_party/opencv/include \
                      $(TOPDIR)third_party/protobuf/include \
                      $(TOPDIR)third_party/cereal/include \
                      $(LOCAL_PATH)/facedetectionapp/face_detection_post_process \
                      $(LOCAL_PATH)/facedetectionapp/common/include \
                      $(TOPDIR)ascenddk/common/osd \
                      $(TOPDIR)ascenddk/common/utils/ascend_ezdvpp \
                      $(TOPDIR)ascenddk/common/presenter/agent/include

local_lib_src_files := proto/ai_types.proto \
                       proto/graph_config.proto \
                       facedetectionapp/face_detection_post_process/face_detection_post_process.cpp


LOCAL_MODULE := libfacedetection_post

LOCAL_C_INCLUDES := $(local_lib_inc_path)

LOCAL_SRC_FILES := $(local_lib_src_files)

LOCAL_SHARED_LIBRARIES := libhiai_common libpresenteragent libascend_ezdvpp libascenddk_osd libprotobuf libc_sec libmatrixdaemon

LOCAL_CFLAGS := -O2 -Wall

include $(BUILD_SHARED_LIBRARY)

## face detection inference engine
include $(CLEAR_VARS)
local_lib_inc_path := $(TOPDIR)inc \
                      $(TOPDIR)inc/custom \
                      $(TOPDIR)libc_sec/include \
                      $(TOPDIR)third_party/opencv/include \
                      $(TOPDIR)third_party/protobuf/include \
                      $(TOPDIR)third_party/cereal/include \
                      $(LOCAL_PATH)/facedetectionapp/face_detection_inference \
                      $(LOCAL_PATH)/facedetectionapp/common/include \
                      $(TOPDIR)ascenddk/common/osd \
                      $(TOPDIR)ascenddk/common/utils/ascend_ezdvpp \
                      $(TOPDIR)ascenddk/common/presenter/agent/include

local_lib_src_files := proto/ai_types.proto \
                       proto/graph_config.proto \
                       facedetectionapp/face_detection_inference/face_detection_inference.cpp


LOCAL_MODULE := libfacedetection_inference

LOCAL_C_INCLUDES := $(local_lib_inc_path)

LOCAL_SRC_FILES := $(local_lib_src_files)

LOCAL_SHARED_LIBRARIES := libhiai_server libhiai_common libprotobuf libc_sec libmatrixdaemon

LOCAL_CFLAGS := -O2 -Wall

include $(BUILD_SHARED_LIBRARY)

## face detection pre-process
include $(CLEAR_VARS)
local_lib_inc_path := $(TOPDIR)inc \
                      $(TOPDIR)inc/custom \
                      $(TOPDIR)libc_sec/include \
                      $(TOPDIR)third_party/opencv/include \
                      $(TOPDIR)third_party/protobuf/include \
                      $(TOPDIR)third_party/cereal/include \
                      $(LOCAL_PATH)/facedetectionapp/face_detection_pre_process \
                      $(LOCAL_PATH)/facedetectionapp/common/include \
                      $(TOPDIR)ascenddk/common/osd \
                      $(TOPDIR)ascenddk/common/utils/ascend_ezdvpp \
                      $(TOPDIR)ascenddk/common/presenter/agent/include

local_lib_src_files := proto/ai_types.proto \
                       proto/graph_config.proto \
                       facedetectionapp/face_detection_pre_process/face_detection_pre_process.cpp


LOCAL_MODULE := libfacedetection_pre

LOCAL_C_INCLUDES := $(local_lib_inc_path)

LOCAL_SRC_FILES := $(local_lib_src_files)

LOCAL_SHARED_LIBRARIES := libprotobuf libc_sec libmatrixdaemon libDvpp_api

LOCAL_CFLAGS := -O2 -Wall

include $(BUILD_SHARED_LIBRARY)

## face detection camera
include $(CLEAR_VARS)
local_lib_inc_path := $(TOPDIR)inc \
                      $(TOPDIR)inc/custom \
                      $(TOPDIR)libc_sec/include \
                      $(TOPDIR)third_party/opencv/include \
                      $(TOPDIR)third_party/protobuf/include \
                      $(TOPDIR)third_party/cereal/include \
                      $(LOCAL_PATH)/facedetectionapp/camera_datasets \
                      $(LOCAL_PATH)/facedetectionapp/common/include \
                      $(TOPDIR)ascenddk/common/osd \
                      $(TOPDIR)ascenddk/common/utils/ascend_ezdvpp \
                      $(TOPDIR)ascenddk/common/presenter/agent/include

local_lib_src_files := proto/ai_types.proto \
                       proto/graph_config.proto \
                       facedetectionapp/camera_datasets/Mind_camera_datasets.cpp


LOCAL_MODULE := libfacedetection_camera

LOCAL_C_INCLUDES := $(local_lib_inc_path)

LOCAL_SRC_FILES := $(local_lib_src_files)

LOCAL_SHARED_LIBRARIES := libprotobuf libc_sec libmatrixdaemon libmedia_mini

LOCAL_CFLAGS := -O2 -Wall

include $(BUILD_SHARED_LIBRARY)
