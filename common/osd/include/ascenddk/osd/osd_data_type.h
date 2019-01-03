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

#ifndef ASCENDDK_OSD_OSD_DATA_TYPE_H_
#define ASCENDDK_OSD_OSD_DATA_TYPE_H_

#include <memory>
#include <string>
#include <cstdint>

// The memory size of the BGR image is 3 times that of width*height.
#define BGR_BUFFER_MULTIPLE 3

// The memory size of the YUV image is 1.5 times that of width*height.
#define YUV420SP_SIZE_MOLECULE    3
#define YUV420SP_SIZE_DENOMINATOR 2

namespace ascend {
namespace osd {
// Minimum width of image
const int kMinWidth = 16;

// Maximum width of image
const int kMaxWidth = 4096;

// Minimum height of image
const int kMinHeight = 16;

// Maximum height of image
const int kMaxHeight = 4096;

// Line connection mode: 4-connected line
const int kConnectLine4 = 4;

// Line connection mode: 8-connected line
const int kConnectLine8 = 8;

// Default depth of image in dvpp
const int kDvppDefaultBitWidth = 8;

// The minimum  deviation from the origin in horizontal direction.
const int kDvppHorzMinDeviation = 0;

// The minimum deviation from the origin in the vertical direction.
const int kDvppVertMinDeviation = 0;

// Image vertical magnification
const int kDvppVertMagnification = 1;

// Image horizontal magnification
const int kDvppHorzMagnification = 1;

// The number of pixels that text deviating from rectangle.
const int kLabelPixelMagnification = 10;

// Call dvpp interface success
const int kDvppInvokeSuccess = 0;

// Minimum radius of circle
const int kMinRadius = 0;

// The result code returned by osd
enum ResultCode {
  kDrawSuccess,
  kDrawFail,
};

// Image format supported by dvpp
enum DvppImageFormat {
  kYuv420SemiPlannar = 0,
  kYuv422SemiPlannar,
  kYuv444SemiPlannar,
  kYuv422Packed,
  kYuv444Packed,
  kRgb888Packed,
  kXrgb8888Packed,
  kYuv400SemiPlannar,
  kInvalidImageType,
};

// Image arrangement method supported by dvpp
enum DvppImageRankType {
  kNv12 = 0,
  kNv21,
  kYuyv,
  kYvyu,
  kUyvy,
  kYuv,
  kRgb,
  kBgr,
  kRgba,
  kBgra,
  kArgb,
  kAbgr,
  kInvalidImageRankType,
};

// Channel for input image
enum DvppChannelType {
  kRdma = 0,
  kCvdr,
};

// Font type supported by OSD
enum FontType {
  kFontSimplex,
  kFontPlain,
  kFontDuplex,
  kFontComplex,
  kFontTriplex,
  kFontComplexSmall,
  kFontScriptSimplex,
  kFontScriptComplex,
  kFontInvalid,
};

// Image format supported by osd
enum OsdImageFormat {
  kYuv420spnv12, // NV12
  kImageInvalid,
};

// Color of drawing
struct Color {
  uint8_t red;
  uint8_t green;
  uint8_t blue;
};

// Coordinate points of drawing graphics
struct Coordinate {
  int32_t x;
  int32_t y;
};

// Rectangle point
struct RectanglePosition {
  Coordinate lt; // leftTop
  Coordinate rb; // rightBottom
};

// Image attribute
struct ImageAttribute {
  OsdImageFormat image_format;
  uint32_t width;
  uint32_t height;
  uint32_t size = 0;
  std::shared_ptr<uint8_t> data;
};

// Rectangle attribute
struct RectangleAttribute {
  RectanglePosition position;
  Color color = { 255, 255, 0 }; // default color: yellow
  int thickness = 1;
  int line_type = kConnectLine8;
};

// Circle attribute
struct CircleAttribute {
  Coordinate center;
  int radius;
  Color color = { 255, 255, 0 }; // default color: yellow
  int thickness = 1;
  int line_type = kConnectLine8;
};

// Text attribute
struct TextAttribute {
  std::string text;
  Coordinate position;
  FontType font_type = kFontComplex;
  Color color = { 255, 190, 0 }; // default color: deep yellow
  double font_scale = 0.5;
  int thickness = 1;
  int line_type = kConnectLine8;
};

// Rectangle and label attribute
struct RectangleLabelAttribute {
  RectangleAttribute rect_attr;
  TextAttribute text_attr;
};
}
}
#endif /* ASCENDDK_OSD_OSD_DATA_TYPE_H_ */
