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

#include "opencv2/opencv.hpp"

#include "ascenddk/ascend_ezdvpp/dvpp_process.h"
#include "ascenddk/osd/osd_api.h"

namespace ascend {
namespace osd {
/**
 * @brief Verify image parameter, included image format:
 *        image width, image height .etc
 * @param [in] src_img_attr:all required attributes of image
 * @return true:check image param success
 *         false:check image param fail
 */
bool CheckImageParam(const ImageAttribute src_img_attr) {
  // check image format, now only support yuv420sp_nv12
  if (src_img_attr.image_format != kYuv420spnv12) {
    ASC_OSD_LOG_ERROR(
        "Image format is not supported, only support yuv420sp_nv12!");
    return false;
  }

  // check image data size, image data should not be null
  if (src_img_attr.size == 0 || !src_img_attr.data.get()) {
    ASC_OSD_LOG_ERROR("Image data should not be null!");
    return false;
  }

  // check image width and height, now only support even
  if ((src_img_attr.width % 2 != 0) || (src_img_attr.height % 2 != 0)) {
    ASC_OSD_LOG_ERROR("The width and height of the image must only be even!");
    return false;
  }

  // check image width and height, must be 16 ~ 4096
  if (src_img_attr.width > kMaxWidth || src_img_attr.width < kMinWidth
      || src_img_attr.height > kMaxHeight || src_img_attr.height < kMinHeight) {
    ASC_OSD_LOG_ERROR("The width and height must be between 16 and 4096!");
    return false;
  }

  return true;
}

/**
 * @brief Verify drawing parameter, included drawing line type .etc
 * @param [in] line_type:line type of drawing
 * @return true:check drawing param success
 *         false:check drawing param fail
 */
bool CheckDrawingParam(int line_type) {

  // check line type, line type can only be 4 or 8
  if (kConnectLine4 != line_type && kConnectLine8 != line_type) {
    ASC_OSD_LOG_ERROR(
        "Line type is not supported, line type must only be 4 or 8!");
    return false;
  }

  return true;
}

/**
 * @brief Verify drawing parameter, included drawing line type .etc
 * @param [in] font_type:font type of drawing
 * @param [in] thickness:thickness of font line
 * @return true:check drawing param success
 *         false:check drawing param fail
 */
bool CheckFontParam(int font_type, int thinkness) {

  // check line type, line type can only be 4 or 8
  if (font_type < kFontSimplex || font_type > kFontScriptComplex) {
    ASC_OSD_LOG_ERROR("font type is not supported!");
    return false;
  }

  if (thinkness < 0) {
    ASC_OSD_LOG_ERROR("font thickness should not be less than 0!");
    return false;
  }

  return true;
}

/**
 * @brief Image format conversion, call opencv interface to transform the image,
 *        from YUV420SP_NV12 to BGR
 * @param [in] src_img_attr :all required attributes of image
 * @param [out] dst:image after conversion, Mat type
 * @return true: yuv420spnv12 convert to bgr success
 *         false: yuv420spnv12 convert to bgr fail
 */
bool Yuv420spnv12ToBgr(const ImageAttribute &src_img_attr, cv::Mat &dst) {
  // Transforming smart pointer data into Mat type data
  // for calling opencv interface
  cv::Mat src(src_img_attr.height * YUV420SP_SIZE_MOLECULE /
  YUV420SP_SIZE_DENOMINATOR,
              src_img_attr.width, CV_8UC1);

  // Number of characters to copy, the size of yuv image is 1.5 times
  // than width * height;
  int copy_size = src_img_attr.width * src_img_attr.height *
  YUV420SP_SIZE_MOLECULE / YUV420SP_SIZE_DENOMINATOR;

  // Size of the destination buffer
  int destination_size = src.cols * src.rows * src.elemSize();

  // Copy the input image data into the Mat matrix for image conversion.
  int err_ret = memcpy_s(src.data, destination_size, src_img_attr.data.get(),
                         copy_size);
  if (err_ret != EOK) {
    ASC_OSD_LOG_ERROR("Osd failed to copy memory, errRet = %d.", err_ret);
    return false;
  }

  // Call opencv interface to convert image from yuv420sp_nv12 to bgr
  // opencv interface have no return value
  cvtColor(src, dst, CV_YUV2BGR_NV12);

  return true;
}

/**
 * @brief Image format conversion, call DVPP to transform the image,
 *        from BGR to YUV420SP_NV12
 * @param [in] input_image:image data
 * @param [in] width: image width
 * @param [in] height:image height
 * @param [out] output_image: image data after conversion10;2cdstv
 * @return ret
 */
int DvppBgrCovertYuv(char *input_image, int width, int height,
                     std::shared_ptr<uint8_t> &output_image) {
  ascend::utils::DvppToYuvPara dvpp_to_yuv;

  // Dvpp image format, origin imagge is RGB888
  dvpp_to_yuv.image_type = kRgb888Packed;

  // Image arrangement format, destination image is yuv420spnv12
  dvpp_to_yuv.rank = kBgr;

  // Image bit depth
  dvpp_to_yuv.bit_width = kDvppDefaultBitWidth;

  // Image path, default is cvdr
  dvpp_to_yuv.cvdr_or_rdma = kCvdr;

  // Image width
  dvpp_to_yuv.resolution.width = width;

  // Image height
  dvpp_to_yuv.resolution.height = height;

  // The maximum deviation from the origin in horizontal direction. If you
  // don't have to cut it, you need to set it to width - 1
  dvpp_to_yuv.horz_max = width - 1;

  // The minimum deviation from the origin in horizontal direction. If you
  // don't have to cut it, you need to set it to 0
  dvpp_to_yuv.horz_min = kDvppHorzMinDeviation;

  // The maximum deviation from the origin in vertical direction. If you
  // don't have to cut it, you need to set it to width - 1
  dvpp_to_yuv.vert_max = height - 1;

  // The minimum deviation from the origin in vertical direction. If you
  // don't have to cut it, you need to set it to 0
  dvpp_to_yuv.vert_min = kDvppVertMinDeviation;

  // Horizontal magnification. If you don't zoom, set it to 1
  dvpp_to_yuv.horz_inc = kDvppHorzMagnification;

  // Vertical magnification. If you don't zoom, set it to 1
  dvpp_to_yuv.vert_inc = kDvppVertMagnification;

  // 1 pixel in the BGR image occupies 3 bytes,
  // so the application space is 3 times the number of pixels.
  int input_size = width * height * BGR_BUFFER_MULTIPLE;

  ascend::utils::DvppProcess dvpp_process(dvpp_to_yuv);

  ascend::utils::DvppOutput dvpp_output;

  // call dvpp vpc interface to convert image from bgr to yuv420sp_nv12
  int ret = dvpp_process.DvppOperationProc(input_image, input_size,
                                           &dvpp_output);

  // Resets outputImage to output buffer and delete the buffer in dvppOutInfo
  output_image.reset(dvpp_output.buffer, default_delete<uint8_t[]>());

  return ret;
}

int DrawRectangle(const ImageAttribute &src_img_attr,
                  const std::vector<RectangleAttribute> &rect_attrs,
                  std::shared_ptr<uint8_t> &dst_img) {
  // check image param,include image format. image width, image height,
  // image size
  bool image_param_check_ret = CheckImageParam(src_img_attr);

  if (!image_param_check_ret) {
    ASC_OSD_LOG_ERROR("[DrawRectangle] Image parameter check failed!");
    return kDrawFail;
  }

  // if you don't need to draw any rectangles,
  // directly return to the original image without any processing.
  if (rect_attrs.empty()) {
    ASC_OSD_LOG_INFO(
        "[DrawRectangle] rectAttrs is null, return to original image!");
    dst_img = src_img_attr.data;
    return kDrawSuccess;
  }

  cv::Mat dst;

  // convert yuv420sp_nv12 image to bgr image
  bool yuv_to_bgr_is_success = Yuv420spnv12ToBgr(src_img_attr, dst);
  if (!yuv_to_bgr_is_success) {
    ASC_OSD_LOG_ERROR("[DrawRectangle] Yuv420spnv12ToBgr failed!");
    return kDrawFail;
  }

  for (size_t i = 0; i < rect_attrs.size(); ++i) {
    RectangleAttribute rect_attr = rect_attrs[i];

    // check rectangle line type
    bool drawing_param_check_ret = CheckDrawingParam(rect_attr.line_type);

    // If rect drawing params check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR("[DrawRectangle] Rect parameter check failed!");
      return kDrawFail;
    }

    // set rectangle coordinate
    CvPoint rect_left_top, rect_right_bottom;
    rect_left_top.x = rect_attr.position.lt.x;
    rect_left_top.y = rect_attr.position.lt.y;
    rect_right_bottom.x = rect_attr.position.rb.x;
    rect_right_bottom.y = rect_attr.position.rb.y;

    // call opencv interface to drawing rectangle
    rectangle(
        dst,
        rect_left_top,
        rect_right_bottom,
        cv::Scalar(rect_attr.color.blue, rect_attr.color.green,
                   rect_attr.color.red),
        rect_attr.thickness, rect_attr.line_type);
  }

  // get image data after drawing
  char *input_image = (char *) dst.data;

  // convert bgr image to origin yuv420sp_nv12 image
  bool dvpp_result = (DvppBgrCovertYuv(input_image, src_img_attr.width,
                                       src_img_attr.height, dst_img)
      == kDvppInvokeSuccess);

  // If failed to call dvpp, directly return to DRAW_FAIL
  if (!dvpp_result) {
    ASC_OSD_LOG_ERROR("[DrawRectangle] Call dvpp vpc interface failed!");
    return kDrawFail;
  }

  return kDrawSuccess;
}

int DrawRectangleAndLabel(
    const ImageAttribute &src_img_attr,
    const std::vector<RectangleLabelAttribute> &rect_label_attrs,
    std::shared_ptr<uint8_t> &dst_img) {
  // check image param,include image format. image width, image height,
  // image size
  bool image_param_check_ret = CheckImageParam(src_img_attr);
  if (!image_param_check_ret) {
    ASC_OSD_LOG_ERROR("[DrawRectangleAndLabel] Image parameter check failed!");
    return kDrawFail;
  }

  // if you don't need to draw any rectangles and labels,
  // directly return to the original image without any processing.
  if (rect_label_attrs.empty()) {
    ASC_OSD_LOG_INFO(
        "[DrawRectangleAndLabel] rectLabelAttrs is null," "return to original image!");
    dst_img = src_img_attr.data;
    return kDrawSuccess;
  }

  cv::Mat dst;

  // convert yuv420sp_nv12 image to bgr image
  bool yuv_to_bgr_is_success = Yuv420spnv12ToBgr(src_img_attr, dst);

  if (!yuv_to_bgr_is_success) {
    ASC_OSD_LOG_ERROR("[DrawRectangleAndLabel] Yuv420spnv12ToBgr failed!");
    return kDrawFail;
  }

  for (size_t i = 0; i < rect_label_attrs.size(); ++i) {
    RectangleLabelAttribute rect_label_attr = rect_label_attrs[i];

    // check rectangle line type
    bool drawing_param_check_ret = CheckDrawingParam(
        rect_label_attr.rect_attr.line_type);

    // If text drawing params check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR("[DrawRectangleAndLabel] Rect parameter check failed!");
      return kDrawFail;
    }

    // check text line type
    drawing_param_check_ret = CheckDrawingParam(
        rect_label_attr.text_attr.line_type);

    // If text line type check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR(
          "[DrawRectangleAndLabel] Label line type check failed!");
      return kDrawFail;
    }

    // check text font type and thinckness
    drawing_param_check_ret = CheckFontParam(
        rect_label_attr.text_attr.font_type,
        rect_label_attr.text_attr.thickness);

    // If text font type check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR(
          "[DrawRectangleAndLabel] Label font param check failed!");
      return kDrawFail;
    }

    // set rectangle coordinate
    CvPoint rect_left_top, rect_right_bottom, label_left_bottom;
    rect_left_top.x = rect_label_attr.rect_attr.position.lt.x;
    rect_left_top.y = rect_label_attr.rect_attr.position.lt.y;
    rect_right_bottom.x = rect_label_attr.rect_attr.position.rb.x;
    rect_right_bottom.y = rect_label_attr.rect_attr.position.rb.y;

    // call opencv interface to drawing rectangle
    rectangle(
        dst,
        rect_left_top,
        rect_right_bottom,
        cv::Scalar(rect_label_attr.rect_attr.color.blue,
                   rect_label_attr.rect_attr.color.green,
                   rect_label_attr.rect_attr.color.red),
        rect_label_attr.rect_attr.thickness,
        rect_label_attr.rect_attr.line_type);

    // If the boundaries of the rectangle box are close to the boundaries of
    // the image, then the coordinates of label are shifted downward by 10
    // pixels, and it is possible to avoid label going beyond the boundaries
    if (rect_left_top.y < kLabelPixelMagnification) {
      label_left_bottom.y = rect_label_attr.text_attr.position.y
          + kLabelPixelMagnification;
    }
    // By default, there are 10 pixels between the text and the rectangle
    // to prevent the overlap of the text and rectangle boxes.
    else {
      label_left_bottom.y = rect_label_attr.text_attr.position.y
          - kLabelPixelMagnification;
    }

    label_left_bottom.x = rect_label_attr.text_attr.position.x;

    // set label color
    cv::Scalar color(rect_label_attr.text_attr.color.blue,
                     rect_label_attr.text_attr.color.green,
                     rect_label_attr.text_attr.color.red);

    // call opencv interface to drawing label
    cv::putText(dst, rect_label_attr.text_attr.text, label_left_bottom,
                rect_label_attr.text_attr.font_type,
                rect_label_attr.text_attr.font_scale, color,
                rect_label_attr.text_attr.thickness,
                rect_label_attr.text_attr.line_type);
  }

  // get image data after drawing
  char *input_image = (char *) dst.data;

  // convert bgr image to origin yuv420sp_nv12 image
  bool dvpp_result = (DvppBgrCovertYuv(input_image, src_img_attr.width,
                                       src_img_attr.height, dst_img)
      == kDvppInvokeSuccess);

  // If failed to call dvpp, directly return to DRAW_FAIL
  if (!dvpp_result) {
    ASC_OSD_LOG_ERROR(
        "[DrawRectangleAndLabel] Call dvpp vpc interface failed!");
    return kDrawFail;
  }

  return kDrawSuccess;
}

int DrawCircle(const ImageAttribute &src_img_attr,
               const std::vector<CircleAttribute> &cir_attrs,
               std::shared_ptr<uint8_t> &dst_img) {
  // check image param,include image format. image width, image height,
  // image size
  bool image_param_check_ret = CheckImageParam(src_img_attr);

  // If image params check failed, directly return to DRAW_FAIL
  if (!image_param_check_ret) {
    ASC_OSD_LOG_ERROR("[DrawCircle] Image parameter check failed!");
    return kDrawFail;
  }

  // if you don't need to draw any circles, directly return to the original
  // image without any processing.
  if (cir_attrs.empty()) {
    ASC_OSD_LOG_INFO(
        "[DrawCircle] cirAttrs is null, return to original image!");
    dst_img = src_img_attr.data;
    return kDrawSuccess;
  }

  cv::Mat dst;

  // convert yuv420sp_nv12 image to bgr image
  bool yuv_to_bgr_is_success = Yuv420spnv12ToBgr(src_img_attr, dst);
  if (!yuv_to_bgr_is_success) {
    ASC_OSD_LOG_ERROR("[DrawCircle] Yuv420spnv12ToBgr failed!");
    return kDrawFail;
  }

  for (size_t i = 0; i < cir_attrs.size(); ++i) {
    CircleAttribute cir_attr = cir_attrs[i];

    // check circle line type
    bool drawing_param_check_ret = CheckDrawingParam(cir_attr.line_type);

    // If circle drawing params check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR("[DrawCircle] Circle parameter check failed!");
      return kDrawFail;
    }

    // check circle radius,it should not be less than 0
    if (cir_attr.radius < kMinRadius) {
      ASC_OSD_LOG_ERROR(
          "[DrawCircle] Radius of circle should not be negative!");
      return kDrawFail;
    }

    // set circle center coordinate
    CvPoint cir_center;
    cir_center.x = cir_attr.center.x;
    cir_center.y = cir_attr.center.y;

    // call opencv interface to drawing circle
    cv::circle(
        dst,
        cir_center,
        cir_attr.radius,
        cv::Scalar(cir_attr.color.blue, cir_attr.color.green,
                   cir_attr.color.red),
        cir_attr.thickness, cir_attr.line_type);
  }

  // get image data after drawing
  char *input_image = (char *) dst.data;

  // convert bgr image to origin yuv420sp_nv12 image
  bool dvpp_result = (DvppBgrCovertYuv(input_image, src_img_attr.width,
                                       src_img_attr.height, dst_img)
      == kDvppInvokeSuccess);

  // If failed to call dvpp, directly return to DRAW_FAIL
  if (!dvpp_result) {
    ASC_OSD_LOG_ERROR("[DrawCircle] Call dvpp vpc interface failed!");
    return kDrawFail;
  }

  return kDrawSuccess;
}

int PutText(const ImageAttribute &src_img_attr,
            const std::vector<TextAttribute> &text_attrs,
            std::shared_ptr<uint8_t> &dst_img) {
  // check image param,include image format. image width, image height,
  // image size
  bool image_param_check_ret = CheckImageParam(src_img_attr);

  // If image params check failed, directly return to DRAW_FAIL
  if (!image_param_check_ret) {
    ASC_OSD_LOG_ERROR("[PutText] Image parameter check failed!");
    return kDrawFail;
  }

  // if you don't need to draw any texts, directly return to the original
  // image without any processing.
  if (text_attrs.empty()) {
    ASC_OSD_LOG_INFO("[PutText] textAttrs is null, return to original image!");
    dst_img = src_img_attr.data;
    return kDrawSuccess;
  }

  cv::Mat dst;

  // convert yuv420sp_nv12 image to bgr image
  bool yuv_to_bgr_is_success = Yuv420spnv12ToBgr(src_img_attr, dst);
  if (!yuv_to_bgr_is_success) {
    ASC_OSD_LOG_ERROR("[DrawCircle] Yuv420spnv12ToBgr failed!");
    return kDrawFail;
  }

  for (size_t i = 0; i < text_attrs.size(); ++i) {
    TextAttribute text_attr = text_attrs[i];

    // check text line type
    bool drawing_param_check_ret = CheckDrawingParam(text_attr.line_type);

    // If text drawing params check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR("[PutText] Text parameter check failed!");
      return kDrawFail;
    }

    // check text font type and thinckness
    drawing_param_check_ret = CheckFontParam(text_attr.font_type,
                                             text_attr.thickness);

    // If text font params check failed, directly return to DRAW_FAIL
    if (!drawing_param_check_ret) {
      ASC_OSD_LOG_ERROR("[PutText] Text font parameter check failed!");
      return kDrawFail;
    }

    // set text coordinate
    CvPoint text_left_bottom;
    text_left_bottom.x = text_attr.position.x;
    text_left_bottom.y = text_attr.position.y;

    // set text color
    cv::Scalar color(text_attr.color.blue, text_attr.color.green,
                     text_attr.color.red);

    // call opencv interface to drawing text
    cv::putText(dst, text_attr.text, text_left_bottom, text_attr.font_type,
                text_attr.font_scale, color, text_attr.thickness,
                text_attr.line_type);
  }

  // get image data after drawing
  char *input_image = (char *) dst.data;

  // convert bgr image to origin yuv420sp_nv12 image
  bool dvpp_result = (DvppBgrCovertYuv(input_image, src_img_attr.width,
                                       src_img_attr.height, dst_img)
      == kDvppInvokeSuccess);

  // If failed to call dvpp, directly return to DRAW_FAIL
  if (!dvpp_result) {
    ASC_OSD_LOG_ERROR("[PutText] Call dvpp vpc interface failed!");
    return kDrawFail;
  }

  return kDrawSuccess;
}
}
}
