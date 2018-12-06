#!/usr/bin/python
#-*- coding: UTF-8 -*-

import os
import datetime
import inspect
import sys

THIS_FILE_NAME = __file__

LEVELS = {"DEBUG":1,"INFO":2,"WARNING":3,"ERROR":4}

#打印颜色，’B‘开头的表示背景色，’F‘开关表示前景色
COLOR_B_BLACK = 40
COLOR_B_RED = 41
COLOR_B_GREEN = 42
COLOR_B_YELLOW = 43
COLOR_B_BLUE = 44
COLOR_B_PURPLE = 45
COLOR_B_CYANINE = 46
COLOR_B_WHITE = 47
COLOR_F_BLACK = 30
COLOR_F_RED = 31
COLOR_F_GREEN = 32
COLOR_F_YELLOW = 33
COLOR_F_BLUE = 34
COLOR_F_PURPLE = 35
COLOR_F_CYANINE = 36
COLOR_F_WHITE = 37

def cilog_get_timestamp():
    timestamp_microsecond = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
    return timestamp_microsecond[0:18]
         
def cilog_print_element(cilog_element):
    print("["+cilog_element+"]", end = ' ')
    return
                
def cilog_logmsg(log_level, filename, line_no, funcname, log_msg, *log_paras):
    if LEVELS[log_level] < LEVELS[os.getenv("LOG_LEVEL","DEBUG")]:
        return
    log_timestamp = cilog_get_timestamp()
    
    cilog_print_element(log_timestamp)
    cilog_print_element(log_level)
    cilog_print_element(filename)
    cilog_print_element(str(line_no))
    cilog_print_element(funcname)
        
    print(log_msg % log_paras[0])
    sys.stdout.flush()
    
    return

def cilog_debug(filename, log_msg, *log_paras):
    line_no = inspect.currentframe().f_back.f_lineno
    funcname = inspect.currentframe().f_back.f_code.co_name
    cilog_logmsg("DEBUG", filename, line_no, funcname, log_msg, log_paras)
    return

def cilog_error(filename, log_msg, *log_paras):
    line_no = inspect.currentframe().f_back.f_lineno
    funcname = inspect.currentframe().f_back.f_code.co_name
    cilog_logmsg("ERROR", filename, line_no, funcname, "\x1b[41m"+log_msg+"\x1b[0m", log_paras)
    return
    
def cilog_warning(filename, log_msg, *log_paras):
    line_no = inspect.currentframe().f_back.f_lineno
    funcname = inspect.currentframe().f_back.f_code.co_name
    cilog_logmsg("WARNING", filename, line_no, funcname, "\x1b[43m"+log_msg+"\x1b[0m", log_paras)
    return
    
def cilog_info(filename, log_msg, *log_paras):
    line_no = inspect.currentframe().f_back.f_lineno
    funcname = inspect.currentframe().f_back.f_code.co_name
    cilog_logmsg("INFO", filename, line_no, funcname, log_msg, log_paras)
    return

def cilog_info_color(filename, color, log_msg, *log_paras):
    color_str = "\x1b[%dm"%color
    line_no = inspect.currentframe().f_back.f_lineno
    funcname = inspect.currentframe().f_back.f_code.co_name
    cilog_logmsg("INFO", filename, line_no, funcname, color_str+log_msg+"\x1b[0m", log_paras)
    return

if __name__ == "__main__":
    i = 0
    while i<3:
        cilog_error(THIS_FILE_NAME, "%s say %s %d times", "I", "Hello world", i)
        i+=1