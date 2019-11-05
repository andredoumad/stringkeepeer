import inspect
import os.path
import socket
from datetime import datetime
from stringkeeper.standalone_logging import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('standalone logging BASE_DIR: ' + str(BASE_DIR) )
filepath_hostname = str(socket.gethostname())
final_filepath_hostname = ''
for ch in filepath_hostname:
    if ch != '.':
        final_filepath_hostname += str(ch)

log_directory_path = str(BASE_DIR + '/logs/' + str(datetime.today().strftime('%Y-%m-%d')) + '/' + final_filepath_hostname)

if not os.path.exists(log_directory_path):
    os.makedirs(log_directory_path)

def get_list_files_folders_in_path(path):
    list_fp = []
    list_dp = []
    b_fp = False
    b_dp = False
    for i in os.scandir(path):
        if i.is_file():
            #print('File: ' + i.path)
            list_fp.append(i.path)
            b_fp = True
        elif i.is_dir():
            #print('Folder: ' + i.path)
            list_dp.append(i.path + '/')
            b_dp = True
    return b_dp, b_fp, list_dp, list_fp

log_files = []
b_dp, b_fp, list_dp, list_fp = get_list_files_folders_in_path(log_directory_path)

'''
if b_fp == True:
    for filepath in list_fp:
        if filepath.find('_log.txt') != -1:
            with open(filepath, 'w+') as f:
                f.write('')
                f.close()
'''

def eventlog(logstring):
    # get the caller's stack frame and extract its file path
    #frame_info = inspect.stack()[1]
    previous_frame = inspect.currentframe().f_back
    (filename, line_number, 
     function_name, lines, index) = inspect.getframeinfo(previous_frame)
      
    #caller_filepath = frame_info.filename  # in python 3.5+, you can use frame_info.filename
    #caller_linenumber = frame_info.caller_linenumber
    del previous_frame  # drop the reference to the stack frame to avoid reference cycles
    caller_filepath = filename
    # make the path absolute (optional)
    caller_filepath = os.path.abspath(caller_filepath)
    caller_filename = ''
    for ch in caller_filepath:
        if not ch.isalnum():
            caller_filename += str('-')
        else:
            caller_filename += str(ch)
    if len(caller_filename) > 25:
        caller_filename = caller_filename[-25:]
    caller_filename += '_log.txt'
    debug_line_number = line_number
    if line_number < 10:
        debug_line_number = str('0000' + str(line_number))        
    elif line_number < 100:
        debug_line_number = str('000' + str(line_number))
    elif line_number < 1000:
        debug_line_number = str('00' + str(line_number))
    elif line_number < 10000:
        debug_line_number = str('0' + str(line_number))
    print('|eventlog| ' + str(filename)[-25:] + ' | ' + str(debug_line_number) + ' | ' + str(logstring))
    log_filepath = str(str(log_directory_path) + '/' + str(caller_filename))
    #print('log_filepath: ' + str(log_filepath))
    #with open(log_filepath, 'a+') as f:
    #    timestamp = str(datetime.today().strftime('%H:%M:%S'))
    #    f.write(str(timestamp + ' || ' + logstring))
    #    f.write('\n')
    #    f.close()

eventlog('log_directory_path ' + log_directory_path)