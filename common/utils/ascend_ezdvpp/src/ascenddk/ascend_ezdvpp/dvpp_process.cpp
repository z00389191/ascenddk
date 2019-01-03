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

#include <cstdlib>
#include <malloc.h>
#include "ascenddk/ascend_ezdvpp/dvpp_process.h"

using namespace std;
namespace ascend {
namespace utils {
DvppProcess::DvppProcess(const DvppToJpgPara &para) {
  // construct a instance used to convert to JPG
  dvpp_instance_para_.jpg_para = para;
  convert_mode_ = kJpeg;
}

DvppProcess::DvppProcess(const DvppToH264Para &para) {
  // construct a instance used to convert to h264
  dvpp_instance_para_.h264_para = para;
  convert_mode_ = kH264;
}

DvppProcess::DvppProcess(const DvppToYuvPara &para) {
  // construct a instance used to convert to YUV420SPNV12
  dvpp_instance_para_.yuv_para = para;
  convert_mode_ = kYuv;
}

ascend::utils::DvppProcess::~DvppProcess() {
  // destructor
}

int DvppProcess::DvppOperationProc(char *input_buf, int input_size,
                                   DvppOutput *output_data) {
  int ret = kDvppOperationOk;

  // yuv change to h264
  if (convert_mode_ == kH264) {
    shared_ptr<AutoBuffer> output_data_queue;

    // process of coversion
    ret = DvppYuvChangeToH264(input_buf, input_size, &output_data_queue);
    if (ret != kDvppOperationOk) {
      return ret;
    }

    // new output buffer
    output_data->buffer = new unsigned char[output_data_queue->getBufferSize()];

    // output the h264 data
    output_data->size = output_data_queue->getBufferSize();
    ret = memcpy_s(output_data->buffer, output_data_queue->getBufferSize(),
                   output_data_queue->getBuffer(), output_data->size);
    CHECK_MEMCPY_RESULT(ret, output_data->buffer); // if error,program exit
    // yuv change to jpg
  } else if (convert_mode_ == kJpeg) {
    sJpegeOut jpg_output_data;

    // yuv change jpg
    ret = DvppYuvChangeToJpeg(input_buf, input_size, &jpg_output_data);
    if (ret != kDvppOperationOk) {
      return ret;
    }

    // new output buffer
    output_data->buffer = new unsigned char[jpg_output_data.jpgSize];

    // ouput the jpg data
    output_data->size = jpg_output_data.jpgSize;
    ret = memcpy_s(output_data->buffer, output_data->size,
                   jpg_output_data.jpgData, jpg_output_data.jpgSize);
    jpg_output_data.cbFree();
    CHECK_MEMCPY_RESULT(ret, output_data->buffer); // if error,program exit
  } else {
    // the size of output buffer
    int data_size = dvpp_instance_para_.yuv_para.resolution.width
        * dvpp_instance_para_.yuv_para.resolution.height *
        DVPP_YUV420SP_SIZE_MOLECULE /
    DVPP_YUV420SP_SIZE_DENOMINATOR;

    // new output buffer
    unsigned char *yuv_output_data = new unsigned char[data_size];

    // bgr change to yuv420spnv12
    ret = DvppBgrChangeToYuv(input_buf, input_size, yuv_output_data);
    if (ret != kDvppOperationOk) {
      delete[] yuv_output_data;
      return ret;
    }

    // output the nv12 data
    output_data->buffer = yuv_output_data;
  }
  return ret;
}

int DvppProcess::DvppProc(const sJpegeIn &input_data, sJpegeOut *output_data) {
  if (output_data == nullptr) {
    return kDvppErrorInvalidParameter;
  }

  dvppapi_ctl_msg dvpp_api_ctl_msg;
  dvpp_api_ctl_msg.in = (void *) &input_data;
  dvpp_api_ctl_msg.in_size = sizeof(input_data);
  dvpp_api_ctl_msg.out = (void *) output_data;
  dvpp_api_ctl_msg.out_size = sizeof(sJpegeOut);

  // create Dvpp instance
  IDVPPAPI *dvpp_api = nullptr;
  int ret = CreateDvppApi(dvpp_api);
  if ((dvpp_api == nullptr) || (ret == DVPP_RETURN_ERROR)) {
    ret = kDvppErrorCreateDvppFail;
    ASC_LOG_ERROR("Failed to create instance of dvpp(yuv to jpeg).");
    return ret;
  }

  // convert
  ret = DvppCtl(dvpp_api, DVPP_CTL_JPEGE_PROC, &dvpp_api_ctl_msg);
  if (ret == DVPP_RETURN_ERROR) {
    ret = kDvppErrorDvppCtlFail;
    ASC_LOG_ERROR("Failed to convert in dvpp(yuv to jpeg).");
  }

  // destroy Dvpp instance
  (void) DestroyDvppApi(dvpp_api);

  return ret;
}

int DvppProcess::DvppYuvChangeToJpeg(char *input_buf, int input_size,
                                     sJpegeOut *output_data) {
  sJpegeIn input_data;
  int ret = kDvppOperationOk;

  if ((input_buf == nullptr) || (input_size <= 0) || (output_data == nullptr)) {
    ASC_LOG_ERROR(
        "The input parameter is error in dvpp(yuv to jpeg)." "parameter is pInput_buf:%d input_size:%d pOut_data:%d.",
        input_buf, input_size, output_data);
    return kDvppErrorInvalidParameter;
  }

  // yuv image width/height/encoding quality level(1-100)/format/height
  // after aligned
  input_data.width = dvpp_instance_para_.jpg_para.resolution.width;
  input_data.height = dvpp_instance_para_.jpg_para.resolution.height;
  input_data.level = dvpp_instance_para_.jpg_para.level;
  input_data.format = (eEncodeFormat) dvpp_instance_para_.jpg_para.format;
  input_data.heightAligned = dvpp_instance_para_.jpg_para.resolution.height;

  if (JPGENC_FORMAT_YUV420 == (input_data.format & JPGENC_FORMAT_BIT)) {
    // align width to 16
    input_data.stride = ALIGN_UP(input_data.width, JPEGE_WIDTH_ALGIN);

    // bufsize calculate according to  stride and heightAligned.
    // bufsize finally align height to 4k
    input_data.bufSize =
        ALIGN_UP(
            input_data.stride * input_data.heightAligned * DVPP_YUV420SP_SIZE_MOLECULE / DVPP_YUV420SP_SIZE_DENOMINATOR,
            PAGE_SIZE);
  }

  unsigned int mmap_size = ALIGN_UP(input_data.bufSize + kJpegEAddressAlgin,
                                    MAP_2M);

  // apply for memory: 1.Large-page
  unsigned char* addr_orig = (unsigned char*) mmap(
      0, mmap_size, PROT_READ | PROT_WRITE,
      MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | API_MAP_VA32BIT,
      0, 0);
  if (addr_orig == nullptr) {
    ASC_LOG_ERROR("Failed to malloc memory in dvpp(yuv to jpeg).");
    return kDvppErrorMallocFail;
  }

  // first address of buffer align to 128
  input_data.buf = (unsigned char*) ALIGN_UP((uint64_t ) addr_orig,
                                             kJpegEAddressAlgin);

  char *temp_buf = nullptr;

  // input data align to specify requirement
  if (JPGENC_FORMAT_YUV420 == (input_data.format & JPGENC_FORMAT_BIT)) {
    temp_buf = input_buf;
    for (unsigned int j = 0; j < input_data.height; j++) {
      ret = memcpy_s(input_data.buf + ((ptrdiff_t) j * input_data.stride),
                     (unsigned) (mmap_size - j * input_data.stride), temp_buf,
                     (unsigned) (input_data.width));
      CHECK_MEMCPY_RESULT(ret, nullptr); // if exist error,program exit
      temp_buf += input_data.width;
    }
    for (unsigned int j = input_data.heightAligned;
        j < input_data.heightAligned + input_data.height / 2; j++) {
      ret = memcpy_s(input_data.buf + ((ptrdiff_t) j * input_data.stride),
                     (unsigned) (mmap_size - j * input_data.stride), temp_buf,
                     (unsigned) (input_data.width));
      CHECK_MEMCPY_RESULT(ret, nullptr); // if exist error,program exit
      temp_buf += input_data.width;
    }
  }

  // call dvpp
  ret = DvppProc(input_data, output_data);

  // release buffer
  if (addr_orig != nullptr) {
    munmap(
        addr_orig,
        (unsigned) (ALIGN_UP(input_data.bufSize + kJpegEAddressAlgin, MAP_2M)));
  }

  return ret;
}

int DvppProcess::DvppYuvChangeToH264(char *input_buf, int input_size,
                                     shared_ptr<AutoBuffer> *output_buf) {
  // YUV width/height/coding protocol/stroage type
  venc_in_msg venc_msg;
  venc_msg.width = dvpp_instance_para_.h264_para.resolution.width;
  venc_msg.height = dvpp_instance_para_.h264_para.resolution.height;
  venc_msg.coding_type = dvpp_instance_para_.h264_para.coding_type;
  venc_msg.YUV_store_type = dvpp_instance_para_.h264_para.yuv_store_type;
  venc_msg.input_data = input_buf;
  venc_msg.input_data_size = input_size;
  venc_msg.output_data_queue = make_shared<AutoBuffer>();

  dvppapi_ctl_msg dvpp_api_ctl_msg;
  dvpp_api_ctl_msg.in = (void*) (&venc_msg);
  dvpp_api_ctl_msg.in_size = sizeof(venc_in_msg);

  // create Dvpp instance
  IDVPPAPI *dvpp_api = nullptr;
  int ret = CreateDvppApi(dvpp_api);

  // success to create a dvpp instance.
  if ((dvpp_api != nullptr) && (ret != DVPP_RETURN_ERROR)) {
    // convert
    if (DvppCtl(dvpp_api, DVPP_CTL_VENC_PROC,
                &dvpp_api_ctl_msg) == DVPP_RETURN_ERROR) {
      // failed to convert.
      ret = kDvppErrorDvppCtlFail;
      ASC_LOG_ERROR("Failed to convert in dvpp(yuv to h264).");
      DestroyDvppApi(dvpp_api);
      return ret;
    }

    // check the output date.
    if ((dvpp_api_ctl_msg.in == nullptr)
        || ((dvpp_api_ctl_msg.in != nullptr)
            && (((venc_in_msg *) (dvpp_api_ctl_msg.in))->output_data_queue
                == nullptr))) {
      ret = kDvppErrorNoOutputInfo;
      ASC_LOG_ERROR("Failed to get data in dvpp(yuv to h264).");
      DestroyDvppApi(dvpp_api);
      return ret;
    }

    *output_buf = venc_msg.output_data_queue;
  } else { // failed to create dvpp.
    ASC_LOG_ERROR("Failed to create instance of dvpp(yuv to h264).");
    return kDvppErrorCreateDvppFail;
  }

  // destroy Dvpp instance
  DestroyDvppApi(dvpp_api);

  return ret;
}

int DvppProcess::GetMode() const {
  return convert_mode_;
}

void DvppProcess::PrintErrorInfo(int code) const {

  static ErrorDescription dvpp_description[] = { { kDvppErrorInvalidParameter,
      "The parameter is invaild." }, { kDvppErrorMallocFail,
      "Failed to malloc memory in dvpp." }, { kDvppErrorCreateDvppFail,
      "Failed to create dvpp." }, { kDvppErrorDvppCtlFail,
      "Failed to operate dvpp." }, { kDvppErrorNoOutputInfo,
      "The dvpp output is no data." }, { kDvppErrorMemcpyFail,
      "Failed to copy info." }, };

  // find same errorcode and get error description
  int num = sizeof(dvpp_description) / sizeof(ErrorDescription);

  for (int i = 0; i < num; i++) {
    if (code == dvpp_description[i].code) {
      cerr << "[ERROR] " << dvpp_description[i].code_info.c_str() << endl;
      return;
    }
  }

  // not found same errorcode,return
  cerr << "[ERROR] Other error." << endl;
}

int DvppProcess::DvppBgrChangeToYuv(char *input_buf, int input_size,
                                    unsigned char *output_buf) {
  DvppUtils dvpp_utils;

  // check input param
  int ret = dvpp_utils.CheckBgrToYuvParam(input_buf, input_size, output_buf);

  if (ret != kDvppOperationOk) {
    return ret;
  }

  // construct vpc parameters
  dvppapi_ctl_msg dvpp_api_ctl_msg;
  vpc_in_msg vpc_in_msg;

  vpc_in_msg.format = dvpp_instance_para_.yuv_para.image_type;
  vpc_in_msg.cvdr_or_rdma = dvpp_instance_para_.yuv_para.cvdr_or_rdma;
  vpc_in_msg.bitwidth = dvpp_instance_para_.yuv_para.bit_width;
  vpc_in_msg.rank = dvpp_instance_para_.yuv_para.rank;
  vpc_in_msg.width = dvpp_instance_para_.yuv_para.resolution.width;
  vpc_in_msg.high = dvpp_instance_para_.yuv_para.resolution.height;
  vpc_in_msg.hmax = dvpp_instance_para_.yuv_para.horz_max;
  vpc_in_msg.hmin = dvpp_instance_para_.yuv_para.horz_min;
  vpc_in_msg.vmax = dvpp_instance_para_.yuv_para.vert_max;
  vpc_in_msg.vmin = dvpp_instance_para_.yuv_para.vert_min;
  vpc_in_msg.vinc = dvpp_instance_para_.yuv_para.vert_inc;
  vpc_in_msg.hinc = dvpp_instance_para_.yuv_para.horz_inc;

  // 1 pixel in the BGR image occupies 3 bytes, so the application space
  // is 3 times the number of pixels.
  int rgb_width = vpc_in_msg.width * DVPP_BGR_BUFFER_MULTIPLE;

  // 128 byte memory alignment in width direction of bgr image
  vpc_in_msg.stride = ALIGN_UP(rgb_width, VPC_WIDTH_ALGIN);

  // 16 byte memory alignment in height direction of bgr image
  int high_align = ALIGN_UP(vpc_in_msg.high, VPC_HEIGHT_ALGIN);

  // total storage size of bgr image after the memory is aligned
  int in_buffer_size = vpc_in_msg.stride * high_align;

  // input data address 128 byte alignment
  char *in_buffer = (char *) memalign(VPC_ADDRESS_ALGIN, in_buffer_size);

  // check image whether need to align
  int image_align = kImageNeedAlign;
  image_align = dvpp_utils.CheckImageNeedAlign(vpc_in_msg.width,
                                               vpc_in_msg.high);

  // If original image is already memory aligned, directly copy all memory.
  if (image_align == kImageNotNeedAlign) {
    ret = memcpy_s(in_buffer, in_buffer_size, input_buf, input_size);
    CHECK_VPC_MEMCPY_S_RESULT(ret, in_buffer, nullptr);
  } else { //If image is not aligned, memory copy from line to line.
    // remain memory size in input buffer
    int remain_in_buffer_size = in_buffer_size;

    for (int i = 0; i < vpc_in_msg.high; ++i) {
      ret = memcpy_s(in_buffer + ((ptrdiff_t) i * vpc_in_msg.stride),
                     remain_in_buffer_size, input_buf, rgb_width);
      CHECK_VPC_MEMCPY_S_RESULT(ret, in_buffer, nullptr);
      //Point the pointer to next row of data
      input_buf += rgb_width;
      remain_in_buffer_size -= vpc_in_msg.stride;
    }
  }

  vpc_in_msg.in_buffer = in_buffer;
  vpc_in_msg.in_buffer_size = in_buffer_size;

  shared_ptr<AutoBuffer> auto_out_buffer = make_shared<AutoBuffer>();
  vpc_in_msg.auto_out_buffer_1 = auto_out_buffer;
  dvpp_api_ctl_msg.in = (void *) (&vpc_in_msg);
  dvpp_api_ctl_msg.in_size = sizeof(vpc_in_msg);

  // Create DVPP API
  IDVPPAPI *dvpp_api = nullptr;
  ret = CreateDvppApi(dvpp_api);

  // call DVPP VPC interface
  if (dvpp_api != nullptr && ret == DVPP_RETURN_OK) {
    if (0 != DvppCtl(dvpp_api, DVPP_CTL_VPC_PROC, &dvpp_api_ctl_msg)) {
      ASC_LOG_ERROR("call dvppctl process faild!");
      DestroyDvppApi(dvpp_api);
      free(in_buffer);
      return kDvppErrorDvppCtlFail;
    }
  } else { // create dvpp api fail, directly return
    ASC_LOG_ERROR("piDvppApi is null!");
    DestroyDvppApi(dvpp_api);
    free(in_buffer);
    return kDvppErrorCreateDvppFail;
  }

  // 128 byte memory alignment in width direction of yuv image
  int yuv_stride = ALIGN_UP(vpc_in_msg.width, VPC_WIDTH_ALGIN);

  int out_buffer_size = vpc_in_msg.width * vpc_in_msg.high *
  DVPP_YUV420SP_SIZE_MOLECULE /
  DVPP_YUV420SP_SIZE_DENOMINATOR;

  // The output image is also memory aligned, so if original image is already
  // memory aligned, directly copy all memory.
  if (image_align == kImageNotNeedAlign) {
    ret = memcpy_s(output_buf, out_buffer_size,
                   vpc_in_msg.auto_out_buffer_1->getBuffer(),
                   vpc_in_msg.out_buffer_1_size);
    CHECK_VPC_MEMCPY_S_RESULT(ret, in_buffer, dvpp_api);
  } else { // If image is not aligned, memory copy from line to line.
    // dvpp output buffer
    char *vpc_out_buffer = vpc_in_msg.auto_out_buffer_1->getBuffer();

    // DvppBgrChangeToYuv output buffer index, like array indexes,
    // start at 0
    int out_index = 0;

    // remain memory size in DvppBgrChangeToYuv output buffer
    int remain_out_buffer_size = out_buffer_size;

    // y channel data copy
    for (int j = 0; j < vpc_in_msg.high; ++j) {
      ret = memcpy_s(output_buf + (ptrdiff_t) out_index * vpc_in_msg.width,
                     remain_out_buffer_size, vpc_out_buffer, vpc_in_msg.width);
      CHECK_VPC_MEMCPY_S_RESULT(ret, in_buffer, dvpp_api);

      // Point the pointer to next row of data
      vpc_out_buffer += yuv_stride;
      out_index++;
      remain_out_buffer_size -= vpc_in_msg.width;
    }

    // uv channel data copy
    vpc_out_buffer += (ptrdiff_t) (high_align - vpc_in_msg.high) * yuv_stride;

    for (int k = high_align; k < high_align + vpc_in_msg.high / 2; ++k) {
      ret = memcpy_s(output_buf + (ptrdiff_t) out_index * vpc_in_msg.width,
                     remain_out_buffer_size, vpc_out_buffer, vpc_in_msg.width);
      CHECK_VPC_MEMCPY_S_RESULT(ret, in_buffer, dvpp_api);

      // Point the pointer to next row of data
      vpc_out_buffer += yuv_stride;
      out_index++;
      remain_out_buffer_size -= vpc_in_msg.width;
    }
  }

  // free memory
  free(in_buffer);
  DestroyDvppApi(dvpp_api);

  return ret;
}
}
}
