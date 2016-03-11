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
import copy
import traceback
from PyQt4 import QtCore, QtGui

# Application imports
from common import *
import graphics
import configurationdialog
import antcontrol
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
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)
        
        # Class variables
        self.__lastStatus = ''
        self.__statusMessage = ''
        self.__temp_settings = None
        
        # Retrieve settings and state ( see common.py DEFAULTS for strcture)
        self.__settings = persist.getSavedCfg(SETTINGS_PATH)
        if self.__settings == None: self.__settings = DEFAULT_SETTINGS
        self.__state = persist.getSavedCfg(STATE_PATH)
        if self.__state == None: self.__state = DEFAULT_STATE
        
        # Create the configuration dialog
        self.__config_dialog = configurationdialog.ConfigurationDialog(self.__settings, self.__state[TEMPLATE], self.__config_callback)
        
        # Create the graphics object
        # We have a runtime callback here and a configuration callback to the configurator
        self.__current_template = self.__config_dialog.get_template()
        if self.__current_template != None and len(self.__current_template) > 0:
            path = os.path.join(self.__settings[TEMPLATE_PATH], self.__current_template)
        else:
            path = None
        self.__image_widget = graphics.HotImageWidget(path, self.__graphics_callback, self.__config_dialog.graphics_callback)
        
        # Create the controller API
        self.__api = antcontrol.AntControl(self.__settings[ARDUINO_SETTINGS][NETWORK], self.__api_callback)
        
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
        return self.__qt_app.exec_()
           
    # UI initialisation and window event handlers =====================================================================
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Antenna Switch Controller')
        self.statusBar().setStyleSheet("QStatusBar {color: rgb(60,60,60);font: bold 12px}")
        self.statusBar().showMessage('')
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        # Arrange window
        self.move(100, 100)
        self.setWindowTitle('Antenna/Rig Flexi-Switch')
        
        # Configure Menu
        aboutAction = QtGui.QAction(QtGui.QIcon('about.png'), '&About', self)        
        aboutAction.setShortcut('Ctrl+A')
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about)
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit application')
        exitAction.triggered.connect(self.quit)
        configAction = QtGui.QAction(QtGui.QIcon('config.png'), '&Configuration', self)        
        configAction.setShortcut('Ctrl+C')
        configAction.setStatusTip('Configure controller')
        configAction.triggered.connect(self.__configEvnt)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        configMenu = menubar.addMenu('&Edit')
        configMenu.addAction(configAction)
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAction)
        
        # Set layout
        w = QtGui.QWidget()
        self.setCentralWidget(w)
        self.__grid = QtGui.QGridLayout()
        w.setLayout(self.__grid)

        # Configure the macro buttons
        macro_grid = QtGui.QGridLayout()
        macro_widget = QtGui.QWidget()
        self.__grid.addWidget(macro_widget, 0, 0)
        macro_widget.setLayout(macro_grid)
        # We want an array of 6 buttons for both set and execute
        # Set and execute button groups
        self.__set_btn_array = [None] * 6
        self.__ex_btn_array = [None] * 6
        # 1
        self.__set_btn_array[0] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[0], 0, 0)
        self.__set_btn_array[0].clicked.connect(self.on_set1btn)
        self.__ex_btn_array[0] = QtGui.QPushButton('1', self)
        macro_grid.addWidget(self.__ex_btn_array[0], 1, 0)
        self.__ex_btn_array[0].clicked.connect(self.on_ex1btn)
        self.__ex_btn_array[0].setEnabled(False)
        # 2
        self.__set_btn_array[1] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[1], 0, 1)
        self.__set_btn_array[1].clicked.connect(self.on_set2btn)
        self.__ex_btn_array[1] = QtGui.QPushButton('2', self)
        macro_grid.addWidget(self.__ex_btn_array[1], 1, 1)
        self.__ex_btn_array[1].clicked.connect(self.on_ex2btn)
        self.__ex_btn_array[1].setEnabled(False)
        # 3
        self.__set_btn_array[2] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[2], 0, 2)
        self.__set_btn_array[2].clicked.connect(self.on_set3btn)
        self.__ex_btn_array[2] = QtGui.QPushButton('3', self)
        macro_grid.addWidget(self.__ex_btn_array[2], 1, 2)
        self.__ex_btn_array[2].clicked.connect(self.on_ex3btn)
        self.__ex_btn_array[2].setEnabled(False)
        # 4
        self.__set_btn_array[3] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[3], 0, 3)
        self.__set_btn_array[3].clicked.connect(self.on_set4btn)
        self.__ex_btn_array[3] = QtGui.QPushButton('4', self)
        macro_grid.addWidget(self.__ex_btn_array[3], 1, 3)
        self.__ex_btn_array[3].clicked.connect(self.on_ex4btn)
        self.__ex_btn_array[3].setEnabled(False)
        # 5
        self.__set_btn_array[4] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[4], 0, 4)
        self.__set_btn_array[4].clicked.connect(self.on_set5btn)
        self.__ex_btn_array[4] = QtGui.QPushButton('5', self)
        macro_grid.addWidget(self.__ex_btn_array[4], 1, 4)
        self.__ex_btn_array[4].clicked.connect(self.on_ex5btn)
        self.__ex_btn_array[4].setEnabled(False)
        # 6
        self.__set_btn_array[5] = QtGui.QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[5], 0, 5)
        self.__set_btn_array[5].clicked.connect(self.on_set6btn)
        self.__ex_btn_array[5] = QtGui.QPushButton('6', self)
        macro_grid.addWidget(self.__ex_btn_array[5], 1, 5)
        self.__ex_btn_array[5].clicked.connect(self.on_ex6btn)
        self.__ex_btn_array[5].setEnabled(False)
        
        # Configure template indicator
        self.templatelabel = QtGui.QLabel('Template: %s' % (self.__current_template))
        self.templatelabel.setStyleSheet("QLabel {color: rgb(60,60,60); font: 16px; qproperty-alignment: AlignCenter}")
        self.__grid.addWidget(self.templatelabel, 1, 0)
        
        # Separator line
        line1 = QtGui.QFrame()
        line1.setFrameShape(QtGui.QFrame.HLine)
        line1.setFrameShadow(QtGui.QFrame.Sunken)
        line1.setStyleSheet("QFrame {background-color: rgb(126,126,126)}")
        self.__grid.addWidget(line1, 2, 0)

        # Configure Graphics Widget
        self.__grid.addWidget(self.__image_widget, 3, 0)
        self.__image_widget.set_mode(MODE_RUNTIME)
        self.__grid.setRowStretch(3, 1)
        self.__grid.setColumnStretch(0, 1)
        
        # Set the startup state if possible
        if self.__current_template != None and len(self.__current_template) > 0:
            self.__image_widget.config(self.__settings[RELAY_SETTINGS][self.__current_template], self.__state[RELAYS][self.__current_template])
        
        # Configure Quit
        line2 = QtGui.QFrame()
        line2.setFrameShape(QtGui.QFrame.HLine)
        line2.setFrameShadow(QtGui.QFrame.Sunken)
        line2.setStyleSheet("QFrame {background-color: rgb(126,126,126)}")
        self.__grid.addWidget(line2, 4, 0)
        self.quitbtn = QtGui.QPushButton('Quit', self)
        self.quitbtn.setToolTip('Quit program')
        self.quitbtn.resize(self.quitbtn.sizeHint())
        self.quitbtn.setMinimumHeight(20)
        self.quitbtn.setEnabled(True)
        self.__grid.addWidget(self.quitbtn, 5, 0)
        self.quitbtn.clicked.connect(self.quit)
        
        # Set macro buttons
        self.__do_config_macro_buttons()
        
        # Finish up
        w.setLayout(self.__grid)        
        self.setGeometry(self.__state[WINDOW][X], self.__state[WINDOW][Y], self.__state[WINDOW][W], self.__state[WINDOW][H])
        self.setFixedSize(self.__state[WINDOW][W], self.__state[WINDOW][H])
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
        self.__state[WINDOW] = [self.x(), self.y(), self.width(), self.height()]
        if self.__current_template == None:
            template = ''
        else:
            template = self.__current_template
        self.__state[TEMPLATE] = template
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
    
    def moveEvent(self, event):
        """ Track the window position """
        
        self.__state[WINDOW][0] = event.pos().x()
        self.__state[WINDOW][1] = event.pos().y()
    
    def __configEvnt(self, event):
        """
        Run the configurator.
        This is run non-modal as we need to be able to configure hot spots on the main window.
        
        Arguments:
            event   -- ui event object
            
        """
        
        # Put the graphics into config mode
        self.__image_widget.set_mode(MODE_CONFIG)
        # Create a temporary setting structure
        self.__temp_settings = copy.deepcopy(self.__settings)
        # Show the dialog. This makes it non-modal
        self.__config_dialog.show()
                
    # Macro event handlers =============================================================================================
    def on_set1btn(self):
        """ Set macro button 1 """
        
        self.__do_setbtn(0)
    
    def on_set2btn(self):
        """ Set macro button 2 """
        
        self.__do_setbtn(1)
    
    def on_set3btn(self):
        """ Set macro button 3 """
        
        self.__do_setbtn(2)
    
    def on_set4btn(self):
        """ Set macro button 4 """
        
        self.__do_setbtn(3)
    
    def on_set5btn(self):
        """ Set macro button 5 """
        
        self.__do_setbtn(4)
    
    def on_set6btn(self):
        """ Set macro button 6 """

        self.__do_setbtn(5)
    
    def on_ex1btn(self):
        """ Execute macro button 1 """

        self.__do_exbtn(0)
        
    def on_ex2btn(self):
        """ Execute macro button 2 """
        
        self.__do_exbtn(1)
        
    def on_ex3btn(self):
        """ Execute macro button 3 """
        
        self.__do_exbtn(2)
        
    def on_ex4btn(self):
        """ Execute macro button 4 """
        
        self.__do_exbtn(3)
        
    def on_ex5btn(self):
        """ Execute macro button 5 """
        
        self.__do_exbtn(4)
        
    def on_ex6btn(self):
        """ Execute macro button 6 """
        
        self.__do_exbtn(5)
       
    # Callback handler ===============================================================================================
    def __config_callback(self, what, data):
        """
        Callback from configurator.
        
        Arguments:
            what    --  callback event type
            data    --  associated data, event specific
            
        """
        
        if what == CONFIG_NETWORK:
            self.__temp_settings[ARDUINO_SETTINGS][NETWORK][IP] = data[IP]
            self.__temp_settings[ARDUINO_SETTINGS][NETWORK][PORT] = data[PORT]            
        elif what == CONFIG_EDIT_ADD_HOTSPOT:
            self.__temp_settings[RELAY_SETTINGS] = data
        elif what == CONFIG_DELETE_HOTSPOT:
            self.__temp_settings[RELAY_SETTINGS] = data
        elif what == CONFIG_ACCEPT:
            self.__settings = copy.deepcopy(self.__temp_settings)
            self.__temp_settings = None
            if self.__settings[ARDUINO_SETTINGS][NETWORK][IP] != None and self.__settings[ARDUINO_SETTINGS][NETWORK][PORT] != None:
                self.__api.resetNetworkParams(self.__settings[ARDUINO_SETTINGS][NETWORK][IP], self.__settings[ARDUINO_SETTINGS][NETWORK][PORT])
            persist.saveCfg(SETTINGS_PATH, self.__settings)
            # Back into runtime with the new settings
            self.__image_widget.set_mode(MODE_RUNTIME)
            self.__image_widget.config(self.__settings[RELAY_SETTINGS][self.__current_template], self.__state[RELAYS][self.__current_template])
        elif what == CONFIG_REJECT:
            # Just forget the changes
            self.__image_widget.set_mode(MODE_RUNTIME)
            self.__temp_settings = None
        elif what == CONFIG_NEW_TEMPLATE:
            current_template, relay_settings = data
            self.__temp_settings[RELAY_SETTINGS] = relay_settings
            for template in relay_settings:
                if template not in self.__state[RELAYS]:
                    self.__state[RELAYS][template] = {1: 'relayoff', 2: 'relayoff', 3: 'relayoff', 4: 'relayoff', 5: 'relayoff', 6: 'relayoff', 7: 'relayoff', 8: 'relayoff'}
        elif what == CONFIG_SEL_TEMPLATE:
            current_template, relay_settings = data
            self.__current_template = current_template
            # Set the new image
            self.__image_widget.set_new_image(os.path.join(self.__settings[TEMPLATE_PATH], current_template))
            # and set the hotspots 
            self.__image_widget.config(relay_settings[current_template], self.__state[RELAYS][current_template])
            # Change the label
            self.templatelabel.setText('Template: %s' % (self.__current_template))
            # Set the macro buttons
            self.__do_config_macro_buttons()
        elif what == CONFIG_DEL_TEMPLATE:
            current_template, relay_settings = data
            self.__temp_settings[RELAY_SETTINGS] = relay_settings
            # Delete the state for this template
            if current_template in self.__state[RELAYS]:
                del self.__state[RELAYS][current_template]
            # Another template should immediately be selected (if there is one)
            self.__current_template = ''
            
    def __graphics_callback(self, what, data):
        """
        Runtime callback from graphics.
        
        Arguments:
            what    --  callback event type
            data    --  associated data, event specific
            
        """
        
        if what == RUNTIME_RELAY_UPDATE:
            self.__api.set_relay(data[0], data[1])
    
    def __api_callback(self, message):
        
        """
        Callback from API. Note that this is not called from
        the main thread and therefore we just set a status which
        is picked up in the idle loop for display.
        Qt calls MUST be made from the main thread.
        
        Arguments:
            message --  text to drive the status messages
            
        """
        
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
            
            # Check startup conditions
            settings = True
            msg = ''
            if self.__settings[ARDUINO_SETTINGS][NETWORK][IP] == None:
                settings = False
                msg = 'Please configure the Arduino network settings.'
            if len(self.__settings[RELAY_SETTINGS]) == 0:
                settings = False
                msg += '\nPlease configure the relay settings.'
            if not settings:
                # We have no settings so user must configure first
                QtGui.QMessageBox.information(self, 'Configuration Required', msg, QtGui.QMessageBox.Ok)
            
            # Make sure the status gets cleared
            self.__tickcount = 50
        else:
            # Runtime ====================================================
            # Button state
            
            # Status bar
            self.statusBar().showMessage(self.__statusMessage)
            
            # Window size
            width, height = self.__image_widget.get_dims()
            if width != None and height != None:
                if width > 0 and height > 0:
                    # We adjust the window size if necessary to accommodate the image size
                    current_width = self.__grid.cellRect(3,0).width()
                    current_height = self.__grid.cellRect(3,0).height()
                    if width != current_width or height != current_height:
                        self.__state[WINDOW][W] = self.width() + (width - current_width)
                        self.__state[WINDOW][H] = self.height() + (height - current_height)
                        self.setGeometry(self.__state[WINDOW][X], self.__state[WINDOW][Y], self.__state[WINDOW][W], self.__state[WINDOW][H])
                        self.setFixedSize(self.__state[WINDOW][W], self.__state[WINDOW][H])
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
    
    def __do_config_macro_buttons(self, ):
        """
        Enable macro buttons if macros are defined for the current template.
        Set the button tooltips.
        
        """
        
        if self.__current_template in self.__state[MACROS]:
            macro_data = self.__state[MACROS][self.__current_template]
            for macro_index in range(MAX_MACROS):
                if macro_index in macro_data:
                    self.__ex_btn_array[macro_index].setEnabled(True)
                    self.__ex_btn_array[macro_index].setToolTip(macro_data[macro_index][TT])
                else:
                    self.__ex_btn_array[macro_index].setEnabled(False)
                    self.__ex_btn_array[macro_index].setToolTip('')
           
    def __do_setbtn(self, macro_index):
        """
        Save the configuration for the given button
        
        Arguments:
            macro_index   --  0-6 index of macro button
            
        """
        
        # We take the current relay state and save them
        # in the state record for this macro id.
        if self.__current_template not in self.__state[MACROS]:
            self.__state[MACROS][self.__current_template] = {}
        # Create/update the macro data
        self.__state[MACROS][self.__current_template][macro_index] = copy.deepcopy(self.__state[RELAYS][self.__current_template])            
        # Set the tooltip
        tooltip, ok = QtGui.QInputDialog.getText(self, "Configure Button", "Tooltip")
        if ok and len(tooltip) > 0:
            self.__ex_btn_array[macro_index].setToolTip(tooltip)
            self.__state[MACROS][self.__current_template][macro_index][TT] = tooltip
        # Enable the execute button
        self.__ex_btn_array[macro_index].setEnabled(True)
        
    def __do_exbtn(self, macro_index):
        """
        Execute the configuration for the given button
        
        Arguments:
            macro_index   --  0-6 index of macro button
            
        """
        
        # Change the relay state to agree with the macro settings
        macro_data = self.__state[MACROS][self.__current_template][macro_index]
        for relay_id in range(MAX_RLYS):
            # Set relay ID n
            if relay_id in macro_data:
                self.__image_widget.set_relay_state(relay_id+1, macro_data[relay_id])
                self.__api.set_relay(relay_id, macro_data[relay_id])        
     
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