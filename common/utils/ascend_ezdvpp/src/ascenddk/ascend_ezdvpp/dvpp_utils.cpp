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

#include "ascenddk/ascend_ezdvpp/dvpp_utils.h"

namespace ascend {
namespace utils {

DvppUtils::DvppUtils() {
  // TODO Auto-generated constructor stub

}

DvppUtils::~DvppUtils() {
  // TODO Auto-generated destructor stub
}

int DvppUtils::CheckBgrToYuvParam(char *input_buf, int input_size,
                                  int output_size, unsigned char *output_buf) {
  if (input_buf == nullptr || output_buf == nullptr || input_size <= 0
      || output_size <= 0) {
    ASC_LOG_ERROR("Input param and output param can not be null!");
    return kDvppErrorInvalidParameter;
  }

  return kDvppOperationOk;
}

int DvppUtils::CheckImageNeedAlign(int width, int high) {
  // check width and height whether need to align
  if ((width % VPC_WIDTH_ALGIN) == 0 && (high % VPC_HEIGHT_ALGIN) == 0) {
    return kImageNotNeedAlign;
  }

  return kImageNeedAlign;
}

} /* namespace utils */
} /* namespace ascend */
