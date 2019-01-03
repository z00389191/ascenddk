"""presenter channel manager module"""

# -*- coding: UTF-8 -*-
#
#   =======================================================================
#
# Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1 Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================
#
import time
import logging
import threading
from threading import get_ident
from common.channel_manager import ChannelManager

# thread event timeout, The unit is second.
WEB_EVENT_TIMEOUT = 0.1
# thread event timeout, The unit is second.
IMAGE_EVENT_TIMEOUT = 10

class ThreadEvent():
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self, timeout=None):
        self._events = {}
        self._timeout = timeout

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self._events:
            # this is a new client
            # add an entry for it in the self._events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self._events[ident] = [threading.Event(), time.time()]
        return self._events[ident][0].wait(self._timeout)

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self._events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self._events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self._events[get_ident()][0].clear()

class ChannelHandler():
    """A set of channel handlers, process data received from channel"""
    def __init__(self, channel_name, media_type):
        self._channel_name = channel_name
        self._media_type = media_type
        self._img_data = None
        self._thread = None
        # last time the channel receive data.
        self._heartbeat = time.time()
        self._web_event = ThreadEvent(timeout=WEB_EVENT_TIMEOUT)
        self._image_event = ThreadEvent(timeout=IMAGE_EVENT_TIMEOUT)
        self._frame = None
        self._lock = threading.Lock()
        self._channel_manager = ChannelManager()

        if media_type == "video":
            self._thread_name = "videothread-{}".format(self._channel_name)
            self._create_thread()

    def close_thread(self):
        """close thread if object has created"""
        if self._thread is None:
            return

        self._close_thread_switch = True
        self._image_event.set()
        logging.info("%s set _close_thread_switch True", self._thread_name)

    def setheartbeat(self):
        """record heartbeat"""
        self._heartbeat = time.time()

    def save_image(self, data, width, height):
        """save image receive from socket"""
        self._width = width
        self._height = height

        # compute fps if type is video
        if self._media_type == "video":
            while self._img_data:
                time.sleep(0.01)

            self._time_list.append(self._heartbeat)
            self._image_number += 1
            while self._time_list[0] + 1 < time.time():
                self._time_list.pop(0)
                self._image_number -= 1
                if self._image_number == 0:
                    break

            self._fps = len(self._time_list)
            self._img_data = data
            self._image_event.set()
        else:
            self._img_data = data
            self._channel_manager.save_channel_image(self._channel_name,
                                                     self._img_data)


        self._heartbeat = time.time()

    def get_media_type(self):
        """get media_type, support image or video"""
        return self._media_type

    def get_image(self):
        """get image_data"""
        return self._img_data

    def _create_thread(self):
        """Start the background video thread if it isn't running yet."""
        if self._thread is not None and self._thread.isAlive():
            return

        self._heartbeat = time.time()
        self._close_thread_switch = False
        self._fps = 0
        self._image_number = 0
        self._time_list = []

        # start background frame thread
        self._thread = threading.Thread(target=self._video_thread)
        self._thread.start()

    def get_frame(self):
        """Return the current video frame."""
        # wait util receive a frame  data, and push it to your browser.
        ret = self._web_event.wait()
        self._web_event.clear()
        # True: _web_event return because set()
        # False: _web_event return because timeout
        if ret:
            return (self._frame, self._frame_fps,
                    self._frame_width, self._frame_height)

        return (None, None, None, None)

    def frames(self):
        """a generator generates image"""
        while True:
            self._image_event.wait()
            self._image_event.clear()
            if self._img_data:
                yield (self._img_data, self._fps, self._width, self._height)
                self._img_data = None

            # if set _close_thread_switch, return immediately
            if self._close_thread_switch:
                yield (None, None, None, None)

            # if no frames or heartbeat coming in the last 10 seconds,
            # stop the thread and close socket
            if time.time() - self._heartbeat > IMAGE_EVENT_TIMEOUT:
                self._close_thread_switch = True
                self._img_data = None
                yield (None, None, None, None)

    def _video_thread(self):
        """background thread to process video"""
        logging.info('create %s...', (self._thread_name))
        for frame, fps, width, height in self.frames():
            if frame:
                self._frame = frame
                self._frame_fps = fps
                self._frame_width = width
                self._frame_height = height
                # send signal to clients
                self._web_event.set()

            # exit thread
            if self._close_thread_switch:
                self._channel_manager.clean_channel_resource_by_name(
                    self._channel_name)
                logging.info('Stop thread:%s.', (self._thread_name))
                break
