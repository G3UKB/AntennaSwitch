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
    2.  On left click change switch position.

"""

class HotImageWidget(QtGui.QWidget):
    
    def __init__(self, image_path, runtime_callback, config_callback):
        """
        Constructor
        
        Arguments:
            image_path          --  path to the background image
            runtime_callback    --  callback here with runtime events
            config_callback     --  callback here with configuration events
            
        """
        
        super(HotImageWidget, self).__init__()
        
        # Params
        self.__image_path = image_path
        self.__runtime_callback = runtime_callback
        self.__config_callback = config_callback      

        # Class vars
        self.__mode = MODE_UNDEFINED    # config or runtime
        self.__pos1 = None              # switch position start
        self.__pos2 = None              # switch position end
        # {
        #   relay-id: {
        #               CONFIG_HOTSPOT_TOPLEFT: (x,y),
        #               CONFIG_HOTSPOT_BOTTOMRIGHT: (x,y),
        #               CONFIG_HOTSPOT_COMMON: (x,y),
        #               CONFIG_HOTSPOT_NO: (x,y),
        #               CONFIG_HOTSPOT_NC: (x,y)
        #              },
        #   relay-id: {...}, ...
        # }
        self.__hotspots = None
        self.__current_hotspot = None       # set to hotspot when highlight required
        self.__no_draw = False              # don't draw on the image
        self.__ignore_right = True          # ignore the right button
        self.__draw_switch_positions = {}   # switch position drawing params
        
        # Install the filter
        self.installEventFilter(self)
        self.setMouseTracking(True)

# Public Interface
#==========================================================================================    
    def set_mode(self, mode):
        """
        Set the operation mode
        
        Arguments:
            mode          --  MODE_UNDEFINED | MODE_CONFIG | MODE_RUNTIME
            
        """
        
        if mode in (MODE_UNDEFINED, MODE_CONFIG, MODE_RUNTIME):
            self.__mode = mode
            return True
        return False
    
    def config(self, hotspot_list, relay_state):
        """
        Set the list of hotspots and the relay state
        
        Arguments:
            hotspot_list    --  dictionary of id against hotspots
            
        """
        
        self.__hotspots = hotspot_list
        self.__relay_state = relay_state
        # Now we have some hotspots we can draw the switch ID and its NC contact
        if self.__hotspots != None:
            for id, hotspot in self.__hotspots.items():
                # Draw the contact state 
                contact_state = relay_state[id]
                if contact_state == RELAY_OFF:
                    self.__draw_switch_positions[id] = (((hotspot[CONFIG_HOTSPOT_COMMON][X], hotspot[CONFIG_HOTSPOT_COMMON][Y]), (hotspot[CONFIG_HOTSPOT_NC][X], hotspot[CONFIG_HOTSPOT_NC][Y])))
                else:
                    self.__draw_switch_positions[id] = (((hotspot[CONFIG_HOTSPOT_COMMON][X], hotspot[CONFIG_HOTSPOT_COMMON][Y]), (hotspot[CONFIG_HOTSPOT_NO][X], hotspot[CONFIG_HOTSPOT_NO][Y])))
                # Force a repaint
                self.repaint()               

# Private Interface
#==========================================================================================
        
# Drawing Events
#==========================================================================================
    def paintEvent(self, e):
        """
        Paint override
        
        Arguments:
            e    --  event data
            
        """
        
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        """
        Custom drawing over the backgraond image
        
        Arguments:
            qp    --  context
            
        """
        
        # The widget is just the image
        pix = QtGui.QPixmap(self.__image_path)
        # Take the whole allocated area
        qp.drawPixmap(0,0,pix)
        
        # See if we need to draw switch positions           
        for id, position in self.__draw_switch_positions.items():
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0))
            pen.setWidth(2)
            qp.setPen(pen)
            qp.drawLine(position[0][0], position[0][1], position[1][0], position[1][1])               
        # See if we need to highlight a hotspot
        if self.__current_hotspot != None:
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0))
            pen.setWidth(2)
            qp.setPen(pen)
            qp.drawRect(self.__current_hotspot[CONFIG_HOTSPOT_TOPLEFT][X] - 3,
                        self.__current_hotspot[CONFIG_HOTSPOT_TOPLEFT][Y] - 3,
                        self.__current_hotspot[CONFIG_HOTSPOT_BOTTOMRIGHT][X] - self.__current_hotspot[CONFIG_HOTSPOT_TOPLEFT][X] + 6,
                        self.__current_hotspot[CONFIG_HOTSPOT_BOTTOMRIGHT][Y] - self.__current_hotspot[CONFIG_HOTSPOT_TOPLEFT][Y] + 6)

    def eventFilter(self, source, event):
        """
        Custom filter for mouse events over the bitmap
        
        Arguments:
            source  --  event source
            event   --  event data
            
        """
        
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
                        id, hotspot = self.__locate(event.pos())
                        if id != -1:
                            self.__current_hotspot = hotspot
                        self.repaint()
        
        # Action on mouse buttons       
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self.__mode == MODE_CONFIG:
                # Just report the clicked position, left button only
                if event.button() == QtCore.Qt.LeftButton:
                    self.__config_callback(EVNT_LEFT, (event.pos().x(), event.pos().y()))
            elif self.__mode == MODE_RUNTIME:
                if event.button() == QtCore.Qt.LeftButton:
                    # Switch the relay state
                    id, hotspot = self.__locate(event.pos())
                    if id != -1:
                        if self.__relay_state[id] == RELAY_OFF: self.__relay_state[id] = RELAY_ON
                        else: self.__relay_state[id] = RELAY_OFF
                        contact_state = self.__relay_state[id]
                        if contact_state == RELAY_OFF:
                            self.__draw_switch_positions[id] = (((hotspot[CONFIG_HOTSPOT_COMMON][X], hotspot[CONFIG_HOTSPOT_COMMON][Y]), (hotspot[CONFIG_HOTSPOT_NC][X], hotspot[CONFIG_HOTSPOT_NC][Y])))
                        else:
                            self.__draw_switch_positions[id] = (((hotspot[CONFIG_HOTSPOT_COMMON][X], hotspot[CONFIG_HOTSPOT_COMMON][Y]), (hotspot[CONFIG_HOTSPOT_NO][X], hotspot[CONFIG_HOTSPOT_NO][Y])))
                        self.repaint()
                        self.__runtime_callback(RUNTIME_RELAY_UPDATE, (id, contact_state))
                        
        return QtGui.QMainWindow.eventFilter(self, source, event)

# Helpers
#==========================================================================================
    def __locate(self, pos):
        """
        Draw the switch ID
        
        Arguments:
            x       --  top left X
            y       --  top left Y
            label   --  text to write
                
        """
            
        for id, hotspot in self.__hotspots.items():
            if  pos.x() >= hotspot[CONFIG_HOTSPOT_TOPLEFT][X] and\
                pos.y() >= hotspot[CONFIG_HOTSPOT_TOPLEFT][Y] and\
                pos.x() <= hotspot[CONFIG_HOTSPOT_BOTTOMRIGHT][X] and\
                pos.y() <= hotspot[CONFIG_HOTSPOT_BOTTOMRIGHT][Y]:
                
                return id, hotspot
        return -1, None
                                