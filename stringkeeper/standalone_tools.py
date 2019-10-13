# -*- coding: utf-8 -*-
import os, time, random, smtplib, shutil
from random import *
import inspect
from time import sleep
import random
import codecs
import sys
import unicodedata
import logging
import ftfy
from datetime import date
import calendar

class Tools:

    def get_list_from_file(self, filepath):
        listFromFile = []
        listFromFile.clear()
        working = True
        #with open(path, 'rb') as f:
            #text = f.read()
        with open(str(filepath), 'r', encoding='utf8') as fh:
            while working == True:
                for line in fh:
                    line = ftfy.fix_encoding(str(line))
                    #print('get_list_from_file: ' + str(line.rstrip()))
                    listFromFile.append(line.rstrip())
                working = False
                
        #fh.close()
        return listFromFile
    
    
    def shuffle_list(self, inputlist):
        for i in range(len(inputlist)):
            swap = randint(0,len(inputlist)-1)
            temp = inputlist[swap]
            inputlist[swap] = inputlist[i]
            inputlist[i] = temp
        return inputlist
    
    

    #@pysnooper.snoop('/home/gordon/p3env/alice/alice/spiders/auto_cleared_history/get_list_files_folders_in_path.history', prefix='get_list_files_folders_in_path', depth=1)
    def get_list_files_folders_in_path(self, path):
        self.list_fp = []
        self.list_dp = []
        self.b_fp = False
        self.b_dp = False
        for i in os.scandir(path):
            if i.is_file():
                #print('File: ' + i.path)
                self.list_fp.append(i.path)
                self.b_fp = True
            elif i.is_dir():
                #print('Folder: ' + i.path)
                self.list_dp.append(i.path + '/')
                self.b_dp = True
        return self.b_dp, self.b_fp, self.list_dp, self.list_fp