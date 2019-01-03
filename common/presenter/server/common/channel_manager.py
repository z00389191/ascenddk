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
import logging
import threading

# max support 10 channels
MAX_CHANNEL_NUM = 10

# when a channel have receive data,
# the active status will last 3 seconds
ACTIVE_LAST_TIME = 3

class ChannelResource():
    """every channel has a  ChannelResource object, contains a ChannelHandler object
    and a socket fileno. it corresponding to the ChannelFd one by one
    """
    def __init__(self, handler, socket=None):
        self._handler = handler
        self._socket = socket

class ChannelFd():
    """every channel has a  ChannelFd object, contains a ChannelHandler
    object and channel name. It corresponds to the ChannelResource one by one
    """
    def __init__(self, channel_name, handler):
        self._channel_name = channel_name
        self._handler = handler

class Channel():
    """record user register channels
        self._image: if channel type is image, save the image here
    """
    def __init__(self, channel_name):
        self._channel_name = channel_name
        self._image = None

class ChannelManager():
    """manage all the api about channel
    __instance: ensure it is a single instance
    _channel_resources: a dict
        key: channel name
        value: a ChannelResource() object.
    _channel_fds: a dict
        key: socket fileno
        value: a ChannelFd() object.
    _channel_list: a list, member is a Channel() object."""

    __instance = None
    _channel_resources = {}
    _channel_fds = {}
    _channel_list = []
    _channel_resource_lock = threading.Lock()
    _channel_fds_lock = threading.Lock()
    _channel_lock = threading.Lock()
    err_code_ok = 0
    err_code_too_many_channel = 1
    err_code_repeat_channel = 2

    def __init__(self):
        """init func"""

    def __new__(cls, *args, **kwargs):
        """ensure only a single instance created. """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kwargs)
            # default create 2 channels: image and video
            cls._channel_list.append(Channel(channel_name="image"))
            cls._channel_list.append(Channel(channel_name="video"))
        return cls.__instance

    def _register_channel_fd(self, sock_fileno, channel_name):
        """Internal func, create a ChannelFd object"""
        if self._channel_fds.get(sock_fileno):
            del self._channel_fds[sock_fileno]
        handler = self._channel_resources[channel_name]._handler
        self._channel_fds[sock_fileno] = ChannelFd(channel_name, handler)


    def create_channel_resource(self, channel_name,
                                channel_fd,
                                media_type,
                                handler):
        """create a ChannelResource object which contains all the resources
           binding a channel.
        channel_name: channel name.
        channel_fd: socket fileno binding the channel.
        media_type: support image or video.
        handler: an channel handler process image data.
        """
        with self._channel_resource_lock:
            log_info = "create channel resource,"
            log_info += " channel_name:%s, channel_fd:%u, media_type:%s"
            logging.info(log_info, channel_name, channel_fd, media_type)
            self._channel_resources[channel_name] = \
                ChannelResource(handler=handler, socket=channel_fd)
            self._register_channel_fd(channel_fd, channel_name)

    def _clean_channel_resource(self, channel_name):
        """Internal func, clean channel resource by channel name"""
        if self._channel_resources.get(channel_name):
            self._channel_resources[channel_name]._handler.close_thread()
            self._channel_resources[channel_name]._handler._web_event.set()
            self._channel_resources[channel_name]._handler._image_event.set()
            del self._channel_resources[channel_name]
            logging.info("clean channel: %s's resource", channel_name)

    def clean_channel_resource_by_fd(self, sock_fileno):
        """
        clean channel resource by socket fileno
        sock_fileno: socket fileno which binding to an channel
        """
        with self._channel_fds_lock:
            with self._channel_resource_lock:
                if self._channel_fds.get(sock_fileno):
                    self._clean_channel_resource(
                        self._channel_fds[sock_fileno]._channel_name)
                    del self._channel_fds[sock_fileno]

    def clean_channel_resource_by_name(self, channel_name):
        """clean channel resource by channel_name
        channel_name: channel name"""
        if self._channel_resources.get(channel_name):
            self.clean_channel_resource_by_fd(
                self._channel_resources[channel_name]._socket)

    def get_channel_handler_by_fd(self, sock_fileno):
        """get channel handler by socket fileno"""
        with self._channel_fds_lock:
            if self._channel_fds.get(sock_fileno):
                return self._channel_fds[sock_fileno]._handler
            return None

    def is_channel_busy(self, channel_name):
        """check if channel is busy """
        with self._channel_resource_lock:
            if self._channel_resources.get(channel_name):
                return True
            return False

    def close_all_thread(self):
        """if a channel process video type, it will create a thread.
        this func can close the thread.
        """
        with self._channel_resource_lock:
            for channel_name in self._channel_resources:
                self._channel_resources[channel_name]._handler.close_thread()

    def get_channel_handler_by_name(self, channel_name):
        """
        get the channel handlerby channel name
        """
        with self._channel_resource_lock:
            if self._channel_resources.get(channel_name):
                return self._channel_resources[channel_name]._handler
            return None

    def list_channels(self):
        """
        return all the channel name and the status
        status is indicating active state or not
        """
        with self._channel_lock:
            return [{'status': self.is_channel_busy(i._channel_name),
                     'name': i._channel_name} for i in self._channel_list]

    def register_one_channel(self, channel_name):
        """
        register a channel path, user create a channel via browser
        """
        with self._channel_lock:
            if len(self._channel_list) >= MAX_CHANNEL_NUM:
                logging.info("register channel: %s fail, \
                             exceed max number 10.", channel_name)
                return self.err_code_too_many_channel
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    logging.info("register channel: %s fail, \
                                 already exist.", channel_name)
                    return self.err_code_repeat_channel

            self._channel_list.append(Channel(channel_name=channel_name))
            logging.info("register channel: %s", channel_name)
            return self.err_code_ok

    def unregister_one_channel(self, channel_name):
        """
        unregister a channel path, user delete a channel via browser
        """
        with self._channel_lock:
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    self.clean_channel_resource_by_name(channel_name)
                    logging.info("unregister channel: %s", channel_name)
                    del self._channel_list[i]
                    break

    def is_channel_exist(self, channel_name):
        """
        Check if a channel is exist
        True: exist
        False: not exist
        """
        with self._channel_lock:
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    return True
            return False

    def save_channel_image(self, channel_name, image_data):
        """
        when a channel bounding to image type,
        server will permanent hold an image for it.
        this func save a image in memory
        """
        with self._channel_lock:
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    self._channel_list[i]._image = image_data
                    break

    def get_channel_image(self, channel_name):
        """
        when a channel bounding to image type,
        server will permanent hold an image for it.
        this func get the image
        """
        with self._channel_lock:
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    return self._channel_list[i]._image

            # channel not exist
            return None

    def clean_channel_image(self, channel_name):
        """
        when a channel bounding to image type,
        server will permanent hold an image for it.
        this func clean the image
        """
        with self._channel_lock:
            for i in range(len(self._channel_list)):
                if self._channel_list[i]._channel_name == channel_name:
                    self._channel_list[i]._image = None
                    break
