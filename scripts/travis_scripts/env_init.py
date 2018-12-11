'''
Created on 2018年12月11日

@author: Administrator
'''

import os
import yaml

import comm.util as util

def main():
    ret = util.execute("git branch")
    
    if ret[0] is False:
        exit(-1)
    
    branch_info = ret[1]
    code_branch = branch_info[0]
    print(code_branch)
    
    file_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../.travis.yml")
    
    try:
        file_stream = open(file_path, 'r')
        travis_dict = yaml.load(file_stream)
        env_varaibles = travis_dict.get("env")
        env_varaibles.append("TRAVIS_BRANCH=" + code_branch)
        
        env_varaibles = list(map(lambda x: "export " + x, env_varaibles))
        
        env_file = os.path.join(os.getenv("HOME"), ".bashrc_rc")
        env_stream = open(env_file, 'w')
        env_stream.write_array(env_varaibles)
        
        bashrc_file = os.path.join(os.getenv("HOME"), ".bashrc")
        bashrc_read_stream = open(bashrc_file, 'r')
        all_lines = []
        while True:
            lines = bashrc_read_stream.readlines(10000)
            if not lines:
                break 
            all_lines.extend(lines)
        if ". ~/.bashrc" not in all_lines:
            bashrc_write_stream = open(bashrc_file, 'a')
            bashrc_write_stream.write(". ~/.bashrc")    
    except OSError as reason:
        print(reason)
    finally:
        if file_stream in locals():
            file_stream.close()
        if env_stream in locals():
            env_stream.close()
        if bashrc_read_stream in locals():
            bashrc_read_stream.close()
        if bashrc_write_stream in locals():
            bashrc_write_stream.close()
if __name__ == '__main__':
    pass