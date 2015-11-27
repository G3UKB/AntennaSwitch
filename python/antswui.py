#!/usr/bin/env python
#
# antswui.py
#
# UI for the Antenna Switch application
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
import os,sys
import string
from time import sleep
import traceback
from PyQt4 import QtCore, QtGui

# Application imports
from common import *
import graphics
import configurationdialog
import persist

"""
GUI UI for antenna switch
"""
class AntSwUI(QtGui.QMainWindow):
    
    def __init__(self, qt_app):
        """
        Constructor
        
        Arguments:
            qt_app  --  the Qt appplication object
            
        """
        
        super(AntSwUI, self).__init__()
        
        self.__qt_app = qt_app
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(74,108,117,255))
        self.setPalette(palette)
        
        # Class variables
        self.__lastStatus = ''
        self.__statusMessage = ''
        
        # Retrieve settings and state ( see common.py DEFAULTS for strcture)
        self.__settings = persist.getSavedCfg(SETTINGS_PATH)
        if self.__settings == None: self.__settings = DEFAULT_SETTINGS
        self.__state = persist.getSavedCfg(STATE_PATH)
        if self.__state == None: self.__state = DEFAULT_STATE
                
        # Initialise the GUI
        self.initUI()
        
        # Show the GUI
        self.show()
        self.repaint()
        
        # Startup active
        self.__startup = True
        
        # Start idle processing
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
    
    def run(self, ):
        """ Run the application """
        
        # Returns when application exists
        r = self.__qt_app.exec_()
        
        # Terminate threads
        
        
        return r
           
    # UI initialisation and window event handlers =====================================================================
    def initUI(self):
        """ Configure the GUI interface """
        
        #grid = QtGui.QGridLayout()
        
        self.pix = graphics.HotImageWidget('pic.gif', self.__callback)
        #grid.addWidget(self.pix, 0,0)
        self.__qt_app.installEventFilter(self.pix)
        
        self.pix.set_mode(MODE_RUNTIME)
        self.pix.set_hotspots(((10,10,50,50),(100,100,140,140)))
        self.pix.set_context_menu(('item1','item2','item3'))
        
        self.setCentralWidget(self.pix)
        
        self.setGeometry(300, 300, 200, 500)
        self.setWindowTitle('Test widget')
        self.show()
    
    def about(self):
        """ User hit about """
        
        text = """
Antenna Switch Controller

    by Bob Cowdery (G3UKB)
    email:  bob@bobcowdery.plus.com
"""
        QtGui.QMessageBox.about(self, 'About', text)
               
    def quit(self):
        """ User hit quit """
        
        # Save the current settings
        persist.saveCfg(SETTINGS_PATH, self.__settings)
        persist.saveCfg(STATE_PATH, self.__state)
        # Close
        QtCore.QCoreApplication.instance().quit()
    
    def closeEvent(self, event):
        """
        User hit x
        
        Arguments:
            event   -- ui event object
            
        """
        
        # Be polite, ask user
        reply = QtGui.QMessageBox.question(self, 'Quit?',
            "Quit application?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.quit()
        else:
            event.ignore()
    
    def __configEvnt(self, event):
        """
        Run the configurator
        
        Arguments:
            event   -- ui event object
            
        """
        
        self.__settings, r = configurationdialog.ConfigurationDialog.getConfig(self.__settings)
        # If Ok save the new config and update internally
        if r:
            # Settings
            persist.saveCfg(SETTINGS_PATH, self.__settings)
            # Network settings
            self.__api.resetNetworkParams(self.__settings[ARDUINO_SETTINGS][NETWORK][IP], self.__settings[ARDUINO_SETTINGS][NETWORK][PORT])
            # Adjust state
       
                
    # Main event handlers =============================================================================================
   
    
    # Callback handler ===============================================================================================
    def __callback(self, what, message):
        
        """
        Callback for status messages. Note that this is not called
        from the main thread and therefore we just set a status which
        is picked up in the idle loop for display.
        Qt calls MUST be made from the main thread.
        
        Arguments:
            message --  text to drive the status messages
            
        """
        
        print(what, message)
        return
    
        try:
            if 'success' in message:
                # Completed, so reset
                self.__statusMessage = 'Finished'
            elif 'failure' in message:
                # Error, so reset
                _, reason = message.split(':')
                self.__statusMessage = '**Failed - %s**' % (reason)
            else:
                # An info message
                self.__statusMessage = message
        except Exception as e:
            self.__statusMessage = 'Exception getting status!'
            print('Exception %s' % (str(e)))

    # Idle time processing ============================================================================================        
    def __idleProcessing(self):
        
        """
        Idle processing.
        Called every 100ms single shot
        
        """
        
        # Check if we need to clear status message
        if (self.__lastStatus == self.__statusMessage) and len(self.__statusMessage) > 0:
            self.__tickcount += 1
            if self.__tickcount >= TICKS_TO_CLEAR:
                self.__tickcount = 0
                self.__statusMessage = ''
        else:
            self.__tickcount = 0
            self.__lastStatus = self.__statusMessage
        
        # Main idle processing        
        if self.__startup:
            # Startup ====================================================
            self.__startup = False
            # Initialise state if required
            
            # Make sure the status gets cleared
            self.__tickcount = 50
        else:
            # Runtime ====================================================
            # Button state
            
            # Progress bar and status messages
            
            pass
            
        # Set next idle time    
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
    
    # Helpers =========================================================================================================
    def __setButtonState(self, enabled, widgets):
        """
        Set enabled/disabled state
        
        Arguments:
            state   --  True if enabled state else disabled
            widgets --  list of widgets to set state
            
        """
        
        for widget in widgets:
            if enabled:
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)         
        
#======================================================================================================================
# Main code
def main():
    
    try:
        # The one and only QApplication 
        qt_app = QtGui.QApplication(sys.argv)
        # Cretae instance
        ant_sw_ui = AntSwUI(qt_app)
        # Run application loop
        sys.exit(ant_sw_ui.run())
        
    except Exception as e:
        print ('Exception','Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()