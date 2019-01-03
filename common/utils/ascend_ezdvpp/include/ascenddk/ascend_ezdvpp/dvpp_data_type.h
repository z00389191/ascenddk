/**
 * ============================================================================
 *
 * Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *   1 Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 *   2 Redistributions in binary form must reproduce the above copyright notice,
 *     this list of conditions and the following disclaimer in the documentation
 *     and/or other materials provided with the distribution.
 *
 *   3 Neither the names of the copyright holders nor the names of the
 *   contributors may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * ============================================================================
 */

#ifndef ASCENDDK_ASCEND_EZDVPP_DVPP_DATA_TYPE_H_
#define ASCENDDK_ASCEND_EZDVPP_DVPP_DATA_TYPE_H_

#include "securec.h"
#include "dvpp/dvpp_config.h"
#include "toolchain/slog.h"

#define CHECK_MEMCPY_RESULT(ret, buffer) \
if (ret != EOK) { \
    ASC_LOG_ERROR("Failed to copy memory,Ret=%d.", ret); \
    unsigned char *buf = buffer; \
    if (buf != nullptr){ \
        delete[] buf; \
    } \
    return kDvppErrorMemcpyFail; \
}

#define CHECK_VPC_MEMCPY_S_RESULT(err_ret, in_buffer, p_dvpp_api) \
if (err_ret != EOK) { \
    ASC_LOG_ERROR("Failed to copy memory,Ret=%d.", err_ret); \
    if (in_buffer != nullptr) \
    { \
        free(in_buffer); \
    } \
    IDVPPAPI *dvpp_api = p_dvpp_api; \
    if (p_dvpp_api != nullptr) \
    { \
        DestroyDvppApi(dvpp_api); \
    } \
    return kDvppErrorMemcpyFail; \
}

#define ASC_LOG_ERROR(fmt, ...) \
dlog_error(ASCENDDK, "[%s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

// The memory size of the BGR image is 3 times that of width*height.
#define DVPP_BGR_BUFFER_MULTIPLE 3

// The memory size of the YUV image is 1.5 times that of width*height.
#define DVPP_YUV420SP_SIZE_MOLECULE    3
#define DVPP_YUV420SP_SIZE_DENOMINATOR 2

#define VPC_WIDTH_ALGIN 128

#define VPC_HEIGHT_ALGIN 16

#define VPC_ADDRESS_ALGIN 128

#define JPEGE_WIDTH_ALGIN 16

#define DVPP_RETURN_ERROR -1

#define DVPP_RETURN_OK 0

namespace ascend {
namespace utils {
const unsigned int kJpegEAddressAlgin = 128;

// Bgr image need memory align
const int kImageNeedAlign = 0;

// Bgr image don't need memory align
const int kImageNotNeedAlign = 1;

struct ErrorDescription {
  int code;
  std::string code_info;
};

enum DvppEncodeType {
  kH265Main = 0, // H265-main level
  kH264Base = 1, // H264-baseline level
  kH264Main = 2, // H264-main level
  kH264High = 3, // H264-high level
};

enum YuvType {
  kYuv420sp, // YUV420 semi-planner
  kYvu420sp, // YVU420 semi-planner
};

enum CaptureObjFlag {
  kJpeg, // convert to jpg
  kH264, // convert to h264
  kYuv, // convert to yuv
};

enum DvppErrorCode {
  kDvppOperationOk = 0,
  kDvppErrorInvalidParameter = -1,
  kDvppErrorMallocFail = -2,
  kDvppErrorCreateDvppFail = -3,
  kDvppErrorDvppCtlFail = -4,
  kDvppErrorNoOutputInfo = -5,
  kDvppErrorMemcpyFail = -6,
};

struct ResolutionRatio {
  int width = 0;
  int height = 0;
};

struct DvppToJpgPara {
  // used to indicate the input format.
  eEncodeFormat format = JPGENC_FORMAT_NV12;

  // used to indicate the output quality while output is jpg.
  int level = 100;

  // image resolution.
  ResolutionRatio resolution;
};

struct DvppToH264Para {
  // coding protocol. 0:H265-main level 1:H264-baseline level
  //                  2:H264-main level 3:H264-high level
  int coding_type = 3;

  // YUV storage method.0:YUV420 semi-planner 1:YVU420 semi-planner
  int yuv_store_type = 0;

  // resolution
  ResolutionRatio resolution;
};

struct DvppToYuvPara {
  int image_type = 0; // Dvpp image format
  int rank = 0;  // Image arrangement format
  int bit_width = 0; // Image bit depth
  int cvdr_or_rdma = 0; // Image path.default is cvdr
  ResolutionRatio resolution; // Image resolution
  int horz_max = 0; // The maximum deviation from the origin in horz direction
  int horz_min = 0; // The minimum deviation from the origin in horz direction
  int vert_max = 0; // The maximum deviation from the origin in vert direction
  int vert_min = 0; // The minimum deviation from the origin in vert direction
  double horz_inc = 0; // Horizontal magnification
  double vert_inc = 0; // Vertical magnification
};

struct DvppOutput {
  // output buffer
  unsigned char *buffer;

  // size of output buffer
  unsigned int size;
};

struct DvppPara {
  DvppToJpgPara jpg_para;
  DvppToH264Para h264_para;
  DvppToYuvPara yuv_para;
};
}
}

#endif /* ASCENDDK_ASCEND_EZDVPP_DVPP_DATA_TYPE_H_ */
