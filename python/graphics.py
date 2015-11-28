#!/usr/bin/env python
#
# graphics.py
#
# A hotspot library.
# 
# Copyright (C) 2015 by G3UKB Bob Cowdery
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#    
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#    
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#    
#  The author can be reached by email at:   
#     bob@bobcowdery.plus.com
#

# System imports
import os, sys
import traceback

# Library imports
from PyQt4 import QtCore, QtGui

# Application imports
from common import *

"""

1.  Load the given image file.
2.  Set configuration mode.
    1.  Callback with mouse position.
    2.  Callback with position when left mouse button pressed.
    3.  Caller provides hot spot map.
    4.  Caller provides drop-down list selection.
3.  Set runtime mode.
    1.  On entering a hot spot put red border around area.
    2.  On right mouse button click within a hotspot display the menu.
    3.  Callback with menu selection.
    4.  Draw switch position between given coordinates.

"""

class HotImageWidget(QtGui.QWidget):
    
    def __init__(self, image_path, runtime_callback, config_callback):      
        super(HotImageWidget, self).__init__()
        
        # Params
        self.__image_path = image_path
        self.__runtime_callback = runtime_callback
        self.__config_callback = config_callback      

        # Class vars
        self.__mode = MODE_UNDEFINED    # config or runtime
        self.__pos1 = None              # switch position start
        self.__pos2 = None              # switch position end
        self.__hotspots = None          # ((x,y,x1,y1), (...), ...)
        self.__current_hotspot = None   # set to hotspot when highlight required
        self.__context_menu = None      # (menu_item, menu_item, ...)
        self.__no_draw = False          # don't draw on the image
        self.__ignore_right = True      # ignore the right button
        
        # Install the filter
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.installEventFilter(self)
        self.setMouseTracking(True)
    
    def set_mode(self, mode):
        
        if mode in (MODE_UNDEFINED, MODE_CONFIG, MODE_RUNTIME):
            self.__mode = mode
            return True
        return False
    
    def set_hotspots(self, hotspot_list):
        
        self.__hotspots = hotspot_list
    
    def set_context_menu(self, menu_items):
        
        self.__context_menu = QtGui.QMenu()
        for item in menu_items:
            action = self.__context_menu.addAction(item)
            action.setData(item)
        
    def draw_switch_position(self, x, y, x1, y1):
        
        self.__pos1 = (x,y)
        self.__pos2 = (x1,y1)
        self.repaint()

    def paintEvent(self, e):
      
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        
        # The widget is just the image
        pix = QtGui.QPixmap(self.__image_path)
        # Take the whole allocated area
        qp.drawPixmap(0,0,pix)
        
        if not self.__no_draw:
            # See if we need to highlight a hotspot
            if self.__current_hotspot != None:
                pen = QtGui.QPen(QtGui.QColor(255, 0, 0))
                pen.setWidth(2)
                qp.setPen(pen)
                qp.drawRect(self.__current_hotspot[0] - 3,
                            self.__current_hotspot[1] - 3,
                            self.__current_hotspot[2] - self.__current_hotspot[0] + 3,
                            self.__current_hotspot[3] - self.__current_hotspot[1] + 3)
                
            # See if we need to draw a switch position
            if self.__pos1 != None and self.__pos2 != None:
                qp.drawLine(self.__pos1[0],self.__pos1[1],self.__pos2[0],self.__pos2[1])
                self.__pos1 = None
                self.__pos2 = None
    
    def eventFilter(self, source, event):
        
        # Actions on mouse position
        if event.type() == QtCore.QEvent.MouseMove:
            if self.__mode == MODE_CONFIG:
                # Just report the position
                if event.button() == QtCore.Qt.NoButton:
                    self.__config_callback(EVNT_POS, (event.pos().x(), event.pos().y()))
            elif self.__mode == MODE_RUNTIME:
                # See if we have entered or left a hotspot
                if not self.__no_draw:
                    if self.__hotspots != None:
                        self.__current_hotspot = None
                        for hotspot in self.__hotspots:
                            if  event.pos().x() >= hotspot[0] and\
                                event.pos().y() >= hotspot[1] and\
                                event.pos().x() <= hotspot[2] and\
                                event.pos().y() <= hotspot[3]:
                                self.__current_hotspot = hotspot
                        self.repaint()
        
        # Action on mouse buttons       
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self.__mode == MODE_CONFIG:
                # Just report the clicked position, left button only
                if event.button() == QtCore.Qt.LeftButton:
                    self.__config_callback(EVNT_LEFT, (event.pos().x(), event.pos().y()))
            elif self.__mode == MODE_RUNTIME:
                # Display the context menu, right button only
                if event.button() == QtCore.Qt.RightButton:
                    if self.__ignore_right:
                        self.__ignore_right = False
                    else:
                        self.__no_draw = True   # Don't fiddle with highlights etc
                        my_event = self.__context_menu.exec_(self.mapToGlobal(event.pos()))
                        if my_event != None:
                            my_data = my_event.data()
                            self.__runtime_callback(EVNT_MENU, (my_data,))
                        self.__no_draw = False
                elif event.button() == QtCore.Qt.LeftButton:
                    # Ignore next right button
                    self.__ignore_right = True
    
        return QtGui.QMainWindow.eventFilter(self, source, event)
