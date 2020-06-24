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

# All imports
from imports import *

"""
GUI UI for antenna switch
"""
class AntSwUI(QMainWindow):
    
    def __init__(self, qt_app):
        """
        Constructor
        
        Arguments:
            qt_app  --  the Qt appplication object
            
        """
        
        super(AntSwUI, self).__init__()
        
        self.__qt_app = qt_app
        
        # Set the back colour
        palette = QPalette()
        palette.setColor(QPalette.Background,QColor(195,195,195,255))
        self.setPalette(palette)
        
        # Class variables
        self.__online = False
        self.__statusMessage = ''
        self.__lastStatus = ''
        self.__temp_settings = None
        self.__temp_state = None
        # Nominally 50 ticks == 5s
        self.__tickcount = TICKS_TO_CLEAR
        self.__pollcount = POLL_TICKS
        # External command
        self.__doMacro = None
        
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
        if len(self.__current_template) > 0:
            relay_state = self.__state[RELAYS][self.__current_template]
        else:
            relay_state = None
        self.__api = antcontrol.AntControl(self.__settings[ARDUINO_SETTINGS][NETWORK], relay_state, self.__api_callback, self.__get_relay_state)
        
        # Create the external command thread
        self.__extCmd = ExtCmdThrd(self.__extCmdCallback)
        self.__extCmd.start()
        
        # Initialise the GUI
        self.initUI()
        
        # Show the GUI
        self.show()
        self.repaint()
        
        # Startup active
        self.__startup = True
        
        # Start idle processing
        QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
    
    def run(self, ):
        """ Run the application """
        
        # Returns when application exists
        return self.__qt_app.exec_()
    
    def __get_relay_state(self):
        # Returne current relay state
        return self.__state[RELAYS][self.__current_template]
    
    # UI initialisation and window event handlers =====================================================================
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Antenna Switch Controller')
        
        # Create a status bar with 2 fields
        self.statusbar = QStatusBar()
        self.statusmon = QLabel('')
        self.statusbar.addPermanentWidget(self.statusmon)
        self.statusmsg = QLabel('')
        self.statusbar.addPermanentWidget(self.statusmsg, stretch=1)
        self.setStatusBar(self.statusbar)
        
        # Set the tooltip font
        QToolTip.setFont(QFont('SansSerif', 10))
        
        # Arrange window
        self.move(100, 100)
        self.setWindowTitle('Antenna/Rig Flexi-Switch')
        
        # Configure Menu
        aboutAction = QAction(QIcon('about.png'), '&About', self)        
        aboutAction.setShortcut('Ctrl+A')
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about)
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit application')
        exitAction.triggered.connect(self.quit)
        configAction = QAction(QIcon('config.png'), '&Configuration', self)        
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
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)

        # Configure the macro buttons
        macro_grid = QGridLayout()
        macro_widget = QWidget()
        self.__grid.addWidget(macro_widget, 0, 0)
        macro_widget.setLayout(macro_grid)
        # We want an array of 6 buttons for both set and execute
        # Set and execute button groups
        self.__set_btn_array = [None] * 6
        self.__ex_btn_array = [None] * 6
        # 1
        self.__set_btn_array[0] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[0], 0, 0)
        self.__set_btn_array[0].clicked.connect(self.on_set1btn)
        self.__ex_btn_array[0] = QPushButton('1', self)
        macro_grid.addWidget(self.__ex_btn_array[0], 1, 0)
        self.__ex_btn_array[0].clicked.connect(self.on_ex1btn)
        self.__ex_btn_array[0].setEnabled(False)
        # 2
        self.__set_btn_array[1] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[1], 0, 1)
        self.__set_btn_array[1].clicked.connect(self.on_set2btn)
        self.__ex_btn_array[1] = QPushButton('2', self)
        macro_grid.addWidget(self.__ex_btn_array[1], 1, 1)
        self.__ex_btn_array[1].clicked.connect(self.on_ex2btn)
        self.__ex_btn_array[1].setEnabled(False)
        # 3
        self.__set_btn_array[2] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[2], 0, 2)
        self.__set_btn_array[2].clicked.connect(self.on_set3btn)
        self.__ex_btn_array[2] = QPushButton('3', self)
        macro_grid.addWidget(self.__ex_btn_array[2], 1, 2)
        self.__ex_btn_array[2].clicked.connect(self.on_ex3btn)
        self.__ex_btn_array[2].setEnabled(False)
        # 4
        self.__set_btn_array[3] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[3], 0, 3)
        self.__set_btn_array[3].clicked.connect(self.on_set4btn)
        self.__ex_btn_array[3] = QPushButton('4', self)
        macro_grid.addWidget(self.__ex_btn_array[3], 1, 3)
        self.__ex_btn_array[3].clicked.connect(self.on_ex4btn)
        self.__ex_btn_array[3].setEnabled(False)
        # 5
        self.__set_btn_array[4] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[4], 0, 4)
        self.__set_btn_array[4].clicked.connect(self.on_set5btn)
        self.__ex_btn_array[4] = QPushButton('5', self)
        macro_grid.addWidget(self.__ex_btn_array[4], 1, 4)
        self.__ex_btn_array[4].clicked.connect(self.on_ex5btn)
        self.__ex_btn_array[4].setEnabled(False)
        # 6
        self.__set_btn_array[5] = QPushButton('Set', self)
        macro_grid.addWidget(self.__set_btn_array[5], 0, 5)
        self.__set_btn_array[5].clicked.connect(self.on_set6btn)
        self.__ex_btn_array[5] = QPushButton('6', self)
        macro_grid.addWidget(self.__ex_btn_array[5], 1, 5)
        self.__ex_btn_array[5].clicked.connect(self.on_ex6btn)
        self.__ex_btn_array[5].setEnabled(False)
        # Set default background
        for button_id in range(len(self.__ex_btn_array)):
            self.__ex_btn_array[button_id].setStyleSheet("QPushButton {background-color: rgb(177,177,177)}")
        
        # Configure template indicator
        self.templatelabel = QLabel('Template: %s' % (self.__current_template))
        self.templatelabel.setStyleSheet("QLabel {color: rgb(60,60,60); font: 16px; qproperty-alignment: AlignCenter}")
        self.__grid.addWidget(self.templatelabel, 1, 0)
        
        # Separator line
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
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
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("QFrame {background-color: rgb(126,126,126)}")
        self.__grid.addWidget(line2, 4, 0)
        self.quitbtn = QPushButton('Quit', self)
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
        self.resize(self.__state[WINDOW][W], self.__state[WINDOW][H])
        self.move(self.__state[WINDOW][X], self.__state[WINDOW][Y])
        self.setFixedSize(self.__state[WINDOW][W], self.__state[WINDOW][H])
        self.show()
    
    def about(self):
        """ User hit about """
        
        text = """
Antenna Switch Controller

    by Bob Cowdery (G3UKB)
    email:  bob@bobcowdery.plus.com
"""
        QMessageBox.about(self, 'About', text)
               
    def quit(self):
        """ User hit quit """
        
        # Close external thread
        self.__extCmd.terminate()
        self.__extCmd.join()
        
        # Close API
        self.__api.terminate()
        
        # Save the current settings
        persist.saveCfg(SETTINGS_PATH, self.__settings)
        self.__state[WINDOW] = [self.x(), self.y(), self.width(), self.height()]
        if self.__current_template == None:
            template = ''
        else:
            template = self.__current_template
        self.__state[TEMPLATE] = template
        persist.saveCfg(STATE_PATH, self.__state)
        # Turn relays off
        #Probably not a great idea as it could remove an antenna while TXing
        # self.__api.reset_relays()
        # Close
        QCoreApplication.instance().quit()
    
    def closeEvent(self, event):
        """
        User hit x
        
        Arguments:
            event   -- ui event object
            
        """
        
        # Be polite, ask user
        reply = QMessageBox.question(self, 'Quit?',
            "Quit application?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
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
        self.__temp_state = copy.deepcopy(self.__state)
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
       
    # Callback handlers ===============================================================================================
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
            self.__state = copy.deepcopy(self.__temp_state)
            self.__temp_settings = None
            self.__temp_state = None
            if self.__settings[ARDUINO_SETTINGS][NETWORK][IP] != None and self.__settings[ARDUINO_SETTINGS][NETWORK][PORT] != None:
                self.__api.resetParams(self.__settings[ARDUINO_SETTINGS][NETWORK][IP], self.__settings[ARDUINO_SETTINGS][NETWORK][PORT])
            persist.saveCfg(SETTINGS_PATH, self.__settings)
            # Back into runtime with the new settings
            self.__image_widget.set_mode(MODE_RUNTIME)
            self.__image_widget.config(self.__settings[RELAY_SETTINGS][self.__current_template], self.__state[RELAYS][self.__current_template])
        elif what == CONFIG_REJECT:
            # Just forget the changes
            self.__image_widget.set_mode(MODE_RUNTIME)
            self.__temp_settings = None
            self.__temp_state = None
        elif what == CONFIG_NEW_TEMPLATE:
            current_template, relay_settings = data
            self.__temp_settings[RELAY_SETTINGS] = relay_settings
            for template in relay_settings:
                if template not in self.__temp_state[RELAYS]:
                    self.__temp_state[RELAYS][template] = {1: 'relayoff', 2: 'relayoff', 3: 'relayoff', 4: 'relayoff', 5: 'relayoff', 6: 'relayoff', 7: 'relayoff', 8: 'relayoff', 9: 'relayoff', 10: 'relayoff', 11: 'relayoff', 12: 'relayoff', 13: 'relayoff', 14: 'relayoff', 15: 'relayoff', 16: 'relayoff'}
        elif what == CONFIG_SEL_TEMPLATE:
            current_template, relay_settings = data
            self.__current_template = current_template
            # Set the new image
            self.__image_widget.set_new_image(os.path.join(self.__settings[TEMPLATE_PATH], current_template))
            # and set the hotspots 
            self.__image_widget.config(relay_settings[current_template], self.__temp_state[RELAYS][current_template])
            # Change the label
            self.templatelabel.setText('Template: %s' % (self.__current_template))
            # Set the macro buttons
            self.__do_config_macro_buttons()
        elif what == CONFIG_DEL_TEMPLATE:
            current_template, relay_settings = data
            self.__temp_settings[RELAY_SETTINGS] = relay_settings
            # Delete the state for this template
            if current_template in self.__temp_state[RELAYS]:
                del self.__temp_state[RELAYS][current_template]
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
            # Set the relay
            self.__api.set_relay(data[0], data[1])
            # Remove macro button highlight
            # Set default background
            for button_id in range(len(self.__ex_btn_array)):
                self.__ex_btn_array[button_id].setStyleSheet("QPushButton {background-color: rgb(177,177,177)}")
            
    def __api_callback(self, online, message):
        
        """
        Callback from API. Note that this is not called from
        the main thread and therefore we just set a status which
        is picked up in the idle loop for display.
        Qt calls MUST be made from the main thread.
        
        Arguments:
            online  --  true if connected
            message --  text to drive the status messages
            
        """
    
        if online:
            self.__online = True
        else:
            self.__online = False
        
        if len(message) > 0:
            self.__statusMessage = message

    def __extCmdCallback(self, macroId):
        
        """
        Callback from the external command thread.
        We have been asked to execute a macro switch command.
        
        Arguments:
            macroId --  id of the macro to execute
            
        """
        
        self.__doMacro = macroId
        
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
                QMessageBox.information(self, 'Configuration Required', msg, QMessageBox.Ok)
            
            # Make sure the status gets cleared and we poll straight away
            self.__tickcount = TICKS_TO_CLEAR
            self.__pollcount = POLL_TICKS
        else:
            # Runtime ====================================================
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
                        
            # Update online state
            # Status bar
            self.statusmsg.setText(self.__statusMessage)
            if self.__online:
                self.statusmon.setText('Connected')
                self.statusmon.setStyleSheet("QLabel {color: green;font: bold 12px}")
            else:
                self.statusmon.setText('Disconnected')
                self.statusmon.setStyleSheet("QLabel {color: red;font: bold 12px}")
                
            # Check for macro execution
            if self.__doMacro != None:
                self.__do_exbtn(self.__doMacro)
                self.__doMacro = None
            
        # Set next idle time    
        QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
    
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
        else:
            for macro_index in range(MAX_MACROS):
                self.__ex_btn_array[macro_index].setEnabled(False)
                self.__ex_btn_array[macro_index].setToolTip('')
           
    def __do_setbtn(self, macro_index):
        """
        Save the configuration for the given button
        
        Arguments:
            macro_index   --  0-6 index of macro button
            
        """
        
        # We take the current relay states and save them
        # in the state record for this macro id.
        if self.__current_template not in self.__state[MACROS]:
            self.__state[MACROS][self.__current_template] = {}
        # Create/update the macro data
        self.__state[MACROS][self.__current_template][macro_index] = copy.deepcopy(self.__state[RELAYS][self.__current_template])            
        # Set the tooltip
        tooltip, ok = QInputDialog.getText(self, "Configure Button", "Description ")
        if ok and len(tooltip) > 0:
            self.__ex_btn_array[macro_index].setToolTip(tooltip)
            self.__state[MACROS][self.__current_template][macro_index][TT] = tooltip
        else:
            self.__ex_btn_array[macro_index].setToolTip('')
            self.__state[MACROS][self.__current_template][macro_index][TT] = ''
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
        for relay_id in range(1, MAX_RLYS-1):
            # Set relay ID n
            if relay_id in macro_data:
                self.__image_widget.set_relay_state(relay_id, macro_data[relay_id])
                self.__api.set_relay(relay_id, macro_data[relay_id])
                self.__state[RELAYS][self.__current_template][relay_id] = macro_data[relay_id]
                sleep(0.3)
        # Adjust button background
        for button_id in range(len(self.__ex_btn_array)):
            if button_id == macro_index:
                # Set background to selected
                self.__ex_btn_array[button_id].setStyleSheet("QPushButton {background-color: rgb(240,78,0)}")
            else:
                self.__ex_btn_array[button_id].setStyleSheet("QPushButton {background-color: rgb(177,177,177)}")
        

"""

External command thread.
Receive switch commands from an external program.

"""
class ExtCmdThrd (threading.Thread):
    
    def __init__(self, callback):
        """
        Constructor
        
        Arguments
            callback    -- callback here for macro execution
        """

        super(ExtCmdThrd, self).__init__()
        
        self.__callback = callback
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((EXT_UDP_IP, EXT_UDP_PORT))
        self.__sock.settimeout(3)
        
        self.__terminate = False
    
    def terminate(self):
        """ Terminate thread """
        
        self.__terminate = True
        
    def run(self):
        # We listen on UDP for switch commands
        while not self.__terminate:
            try:
                data, addr = self.__sock.recvfrom(1024) # buffer size is 1024 bytes
            except socket.timeout:
                continue
            asciidata = data.decode(encoding='UTF-8')
            try:
                if 'switch' in asciidata:
                    _, macroId = asciidata.split(':')
                    # The call is zero based but the UI is 1 based
                    macroId = int(macroId) - 1
                    self.__callback(macroId)
            except Exception as e:
                self.__statusMessage = 'Ext cmd failed: {0}'.format(e)   

#======================================================================================================================
# Main code
def main():
    
    try:
        # The one and only QApplication 
        qt_app = QApplication(sys.argv)
        # Cretae instance
        ant_sw_ui = AntSwUI(qt_app)
        # Run application loop
        sys.exit(ant_sw_ui.run())
        
    except Exception as e:
        print ('Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()