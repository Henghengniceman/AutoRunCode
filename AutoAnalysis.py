# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 12:20:02 2021

@author: Hengheng Zhang

E-Mail: hengheng.zhang@kit.edu

Function： main function 

Version: 0.0

Bug: Cannot do fixed pointed measurement from Oct.-Dec.

"""
import win32api
import win32con
from WorkFlow import auto_analysis
from WorkFlowGUI import auto_analysis_GUI
if __name__ == '__main__':
    result = win32api.MessageBox(None,'Open Graphical User Interface (GUI) ? ','Please Select..',win32con.MB_YESNO)
    if result == win32con.IDYES:
        auto_analysis_GUI()
    else:
        auto_analysis()