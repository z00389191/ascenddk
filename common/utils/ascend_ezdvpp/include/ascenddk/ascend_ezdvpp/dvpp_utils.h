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

#ifndef ASCENDDK_ASCEND_EZDVPP_DVPP_UTILS_H_
#define ASCENDDK_ASCEND_EZDVPP_DVPP_UTILS_H_

#include "dvpp_data_type.h"

namespace ascend {
namespace utils {

class DvppUtils {
 public:
  DvppUtils();
  virtual ~DvppUtils();

  /**
   * @brief check dvppBgrChangeToYuv function parameter
   * @param [in] input_buf:input image data
   *             (dvpp need char *,so pInputBuf do not use const)
   * @param [in] input_size: input image data size
   * @param [in] output_buf: image data after conversion
   * @return enum DvppErrorCode
   */
  int CheckBgrToYuvParam(char *input_buf, int input_size,
                         unsigned char *output_buf);
  /**
   * @brief check whether the image needs alignment
   * @param [in] width: input image width
   * @param [in] high: input image high
   * @return IMAGE_NEED_ALIGN: image need align
   *         IMAGE_NOT_NEED_ALIGN: image don't need align
   */
  int CheckImageNeedAlign(int width, int high);

};

} /* namespace utils */
} /* namespace ascend */

#endif /* ASCENDDK_ASCEND_EZDVPP_DVPP_UTILS_H_ */
