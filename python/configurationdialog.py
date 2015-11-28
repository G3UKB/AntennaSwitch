#!/usr/bin/env python
#
# configurationdialog.py
#
# Configuration for the Antenna Switch application

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
import glob
import copy
from PyQt4 import QtCore, QtGui
from time import sleep
import traceback

# Library imports


# Application imports
from common import *

"""
Configuration dialog
"""
class ConfigurationDialog(QtGui.QDialog):
    
    def __init__(self, settings, config_callback, parent = None):
        """
        Constructor
        
        Arguments:
            settings        --  see common.py DEFAULT_SETTINGS for structure
            config_callback --  callback with configuration data and state
            parent          --  parent window
        """
        
        super(ConfigurationDialog, self).__init__(parent)
        
        # Make as full copy of the settings so we can dit with immunity
        self.__settings = copy.deepcopy(settings)
        # Retain original settings incase we cancel
        self.__orig_settings = copy.deepcopy(settings)
        self.__config_callback = config_callback
        
        # Create the UI interface elements
        self.__initUI()
        
        # Create the API
        # Note that we have our own API instance to use here. As we use UDP there
        # are no connections to worry about and the dialog is modal so no fiddling
        # with the main UI which could cause a conflict.
        #self.__api = antcontrol.ControllerAPI(self.__settings[ARDUINO_SETTINGS][NETWORK], self.__callback)
        
        # Class vars
        
        # Start the idle timer
        QtCore.QTimer.singleShot(100, self.__idleProcessing)

    # UI initialisation ===============================================================================================
    def __initUI(self):
        """ Configure the GUI interface """
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(74,108,117,255))
        self.setPalette(palette)

        self.setWindowTitle('Configuration')
        
        # Set up the tabs
        self.top_tab_widget = QtGui.QTabWidget()
        arduinotab = QtGui.QWidget()
        looptab = QtGui.QWidget()
        sertpointtab = QtGui.QWidget()
        cattab = QtGui.QWidget()
        
        self.top_tab_widget.addTab(arduinotab, "Arduino")
        self.top_tab_widget.addTab(looptab, "Hotspots")
        self.top_tab_widget.currentChanged.connect(self.onTab)        
        
        # Add the top layout to the dialog
        top_layout = QtGui.QGridLayout(self)
        top_layout.addWidget(self.top_tab_widget, 0, 0)
        self.setLayout(top_layout)

        # Set layouts for top tab
        arduinogrid = QtGui.QGridLayout()
        arduinotab.setLayout(arduinogrid)        
        
        # Add the arduino layout to the dialog
        self.__populateArduino(arduinogrid)
        
        # Add common buttons
        self.__populateCommon(top_layout, 1, 0, 1, 1)
 
    def __populateArduino(self, grid):
        """
        Populate the Arduino parameters tab
        
        Arguments
            grid    --  grid to populate
            
        """
        
        # Add instructions
        usagelabel = QtGui.QLabel('Usage:')
        usagelabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(usagelabel, 0, 0)
        instlabel = QtGui.QLabel()
        instructions = """
Set the IP address and port to the listening IP/port of the Arduino.
        """
        instlabel.setText(instructions)
        instlabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(instlabel, 0, 1, 1, 2)
        
        # Add control items
        # IP selection
        iplabel = QtGui.QLabel('Arduino IP')
        grid.addWidget(iplabel, 1, 0)
        self.iptxt = QtGui.QLineEdit()
        self.iptxt.setToolTip('Listening IP of Arduino')
        self.iptxt.setInputMask('000.000.000.000;_')
        self.iptxt.setMaximumWidth(100)
        grid.addWidget(self.iptxt, 1, 1)
        self.iptxt.editingFinished.connect(self.ipChanged)
        if len(self.__settings[ARDUINO_SETTINGS][NETWORK]) > 0:
            self.iptxt.setText(self.__settings[ARDUINO_SETTINGS][NETWORK][IP])
        
        # Port selection
        portlabel = QtGui.QLabel('Arduino Port')
        grid.addWidget(portlabel, 2, 0)
        self.porttxt = QtGui.QLineEdit()
        self.porttxt.setToolTip('Listening port of Arduino')
        self.porttxt.setInputMask('00000;_')
        self.porttxt.setMaximumWidth(100)
        grid.addWidget(self.porttxt, 2, 1)
        self.porttxt.editingFinished.connect(self.portChanged)
        if len(self.__settings[ARDUINO_SETTINGS][NETWORK]) > 0:
            self.porttxt.setText(self.__settings[ARDUINO_SETTINGS][NETWORK][PORT])
        
        nulllabel = QtGui.QLabel('')
        grid.addWidget(nulllabel, 3, 0, 1, 2)
        nulllabel1 = QtGui.QLabel('')
        grid.addWidget(nulllabel1, 0, 2)
        grid.setRowStretch(3, 1)
        grid.setColumnStretch(2, 1)
        
    def __populateCommon(self, grid, x, y, cols, rows):
    
        """
        Populate the common buttons
        
        Arguments
            grid    --  grid to populate
            x       --  grid x
            y       --  grid y
            cols    --  no of cols to occupy
            rows    --  no of rows to occupy
            
        """
        
        # OK and Cancel buttons in a buttonbox
        self.buttonbox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        grid.addWidget(self.buttonbox, x, y, cols, rows)
        self.buttonbox.accepted.connect(self.__accept)
        self.buttonbox.rejected.connect(self.__reject)
    
    # Dialog Management
    #================================================================================================
    def __accept(self):
        """ User accepted changes """
        
        self.__config_callback(CONFIG_ACCEPT, None)
        self.hide()
        
    def __reject(self):
        """ User rejected changes """
        
        self.__config_callback(CONFIG_REJECT, None)
        self.hide()
    
    # Callback
    #================================================================================================
    def graphics_callback(self, what, data):
        """
        Callback from graphics widget
        
        Arguments:
            what    --  event type
            data    --  event data
        """
        
        print('__graphics_callback ', what, data)  
    
    # Event handlers
    #================================================================================================
    # Tab event handler
    def onTab(self, tab):
        """
        User changed tabs
        
        Arguments:
            tab --  new tab index
            
        """
        
        pass
    
    # Arduino event handlers
    def ipChanged(self, ):
        """ User edited IP address """
        
        self.__config_callback(CONFIG_NETWORK, (self.iptxt.text, self.porttxt.text))
        
    def portChanged(self, ):
        """ User edited port address """
        
        self.__config_callback(CONFIG_NETWORK, (self.iptxt.text, self.porttxt.text))
        
                    
    # Idle time processing ============================================================================================        
    def __idleProcessing(self):
        
        """
        Idle processing.
        Called every 100ms single shot
        
        """
    
    # Helpers =========================================================================================================
    