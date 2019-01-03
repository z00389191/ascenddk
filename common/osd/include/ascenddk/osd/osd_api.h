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

#ifndef ASCENDDK_OSD_OSD_API_H_
#define ASCENDDK_OSD_OSD_API_H_

#include <vector>
#include "toolchain/slog.h"

#include "osd_data_type.h"

#define MODULE_ID_OSD ASCENDDK
#define ASC_OSD_LOG_ERROR(fmt, ...) \
dlog_error(MODULE_ID_OSD, "[%s:%d]" fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

#define ASC_OSD_LOG_INFO(fmt, ...) \
dlog_info(MODULE_ID_OSD, "[%s:%d]" fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)

namespace ascend {
namespace osd {

/**
 * @brief Draw one or more rectangles on the original image
 * @param [in] src_img_attr: all required attributes of image
 * @param [in] rect_attrs: all required attributes of rectangles
 * @param [out] dst_img: image data after draw rectangles
 * @return DRAW_SUCCESS:draw rectangle success
 *         DRAW_FAIL:draw rectangle fail
 */
int DrawRectangle(const ImageAttribute &src_img_attr,
                  const std::vector<RectangleAttribute> &rect_attrs,
                  std::shared_ptr<uint8_t> &dst_img);

/**
 * @brief Draw one or more rectangles and labels on the original image
 * @param [in] src_img_attr: all required attributes of image
 * @param [in] rect_label_attrs: all required attributes of rectangles
 *             and labels
 * @param [out] dst_img: image data after draw rectangles and labels
 * @return DRAW_SUCCESS:draw rectangle and label success
 *         DRAW_FAIL:draw rectangle and label fail
 */
int DrawRectangleAndLabel(
    const ImageAttribute &src_img_attr,
    const std::vector<RectangleLabelAttribute> &rect_label_attrs,
    std::shared_ptr<uint8_t> &dst_img);

/**
 * @brief Draw one or more circles on the original image
 * @param [in] src_img_attr: all required attributes of image
 * @param [in] cir_attrs: all required attributes of circles
 * @param [out] dst_img: image data after draw circles
 * @return DRAW_SUCCESS:draw circle success
 *         DRAW_FAIL:draw circle fail
 */
int DrawCircle(const ImageAttribute &src_img_attr,
               const std::vector<CircleAttribute> &cir_attrs,
               std::shared_ptr<uint8_t> &dst_img);

/**
 * @brief Draw one or more text on the original image
 * @param [in] src_img_attr: all required attributes of image
 * @param [in] text_Attrs: all required attributes of text
 * @param [out] dst_img: image data after draw text
 * @return DRAW_SUCCESS:draw text success
 *         DRAW_FAIL:draw text fail
 */
int PutText(const ImageAttribute &src_img_attr,
            const std::vector<TextAttribute> &text_Attrs,
            std::shared_ptr<uint8_t> &dst_img);
}
}

#endif /* ASCENDDK_OSD_OSD_API_H_ */
