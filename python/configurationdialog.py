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

# All imports
from imports import *

"""
Configuration dialog
"""
class ConfigurationDialog(QDialog):
    
    def __init__(self, settings, current_template, config_callback, parent = None):
        """
        Constructor
        
        Arguments:
            settings            --  see common.py DEFAULT_SETTINGS for structure
            current_template    --  current template from last session
            config_callback     --  callback with configuration data and state
            parent              --  parent window
        """
        
        super(ConfigurationDialog, self).__init__(parent)
        
        self.__settings = settings
        self.__config_callback = config_callback
        self.__current_template = current_template
        
        # Class vars
        self.__relay_settings = copy.deepcopy(self.__settings[RELAY_SETTINGS])
        
        # Create the UI interface elements
        self.__initUI()
                
        # Start the idle timer
        QTimer.singleShot(100, self.__idleProcessing)
    
    # UI initialisation ===============================================================================================
    def __initUI(self):
        """ Configure the GUI interface """
        
        # Set the back colour
        palette = QPalette()
        palette.setColor(QPalette.Background,QColor(195,195,195,255))
        self.setPalette(palette)

        self.setWindowTitle('Configuration')
        
        # Set up the tabs
        self.top_tab_widget = QTabWidget()
        arduinotab = QWidget()
        relaytab = QWidget()
        
        self.top_tab_widget.addTab(arduinotab, "Arduino")
        self.top_tab_widget.addTab(relaytab, "Relays")
        self.top_tab_widget.currentChanged.connect(self.onTab)        
        
        # Add the top layout to the dialog
        top_layout = QGridLayout(self)
        top_layout.addWidget(self.top_tab_widget, 0, 0)
        self.setLayout(top_layout)

        # Set layouts for top tab
        arduinogrid = QGridLayout()
        arduinotab.setLayout(arduinogrid)
        relaygrid = QGridLayout()
        relaytab.setLayout(relaygrid)  
        
        # Add the arduino layout to the dialog
        self.__populateArduino(arduinogrid)
        
        # Add the hotspot to the dialog
        self.__populateRelays(relaygrid)
        
        # Add common buttons
        self.__populateCommon(top_layout, 1, 0, 1, 1)
        
        self.__status_bar = QStatusBar()
        top_layout.addWidget(self.__status_bar, 2,0)
        self.__status_bar.setStyleSheet("QStatusBar {color: rgb(60,60,60);font: bold 12px}")
        self.__status_bar.showMessage('')
 
    def __populateArduino(self, grid):
        """
        Populate the Arduino parameters tab
        
        Arguments
            grid    --  grid to populate
            
        """
        
        # Add instructions
        usagelabel = QLabel('Usage:')
        usagelabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(usagelabel, 0, 0)
        instlabel = QLabel()
        instructions = """
Set the IP address and port to the listening IP/port of the Arduino.
        """
        instlabel.setText(instructions)
        instlabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(instlabel, 0, 1, 1, 2)
        
        # Add control items
        # IP selection
        iplabel = QLabel('Arduino IP')
        grid.addWidget(iplabel, 1, 0)
        self.iptxt = QLineEdit()
        self.iptxt.setToolTip('Listening IP of Arduino')
        self.iptxt.setInputMask('000.000.000.000;_')
        self.iptxt.setMaximumWidth(100)
        grid.addWidget(self.iptxt, 1, 1)
        self.iptxt.editingFinished.connect(self.ipChanged)
        if len(self.__settings[ARDUINO_SETTINGS][NETWORK]) > 0:
            self.iptxt.setText(self.__settings[ARDUINO_SETTINGS][NETWORK][IP])
        
        # Port selection
        portlabel = QLabel('Arduino Port')
        grid.addWidget(portlabel, 2, 0)
        self.porttxt = QLineEdit()
        self.porttxt.setToolTip('Listening port of Arduino')
        self.porttxt.setInputMask('00000;_')
        self.porttxt.setMaximumWidth(100)
        grid.addWidget(self.porttxt, 2, 1)
        self.porttxt.editingFinished.connect(self.portChanged)
        if len(self.__settings[ARDUINO_SETTINGS][NETWORK]) > 0:
            self.porttxt.setText(self.__settings[ARDUINO_SETTINGS][NETWORK][PORT])
        
        nulllabel = QLabel('')
        grid.addWidget(nulllabel, 3, 0, 1, 2)
        nulllabel1 = QLabel('')
        grid.addWidget(nulllabel1, 0, 2)
        grid.setRowStretch(3, 1)
        grid.setColumnStretch(2, 1)
    
    def __populateRelays(self, grid):
        """
        Populate the Relays tab
        
        Arguments
            grid    --  grid to populate
            
        """
        
        # Add instructions
        usagelabel = QLabel('Usage:')
        usagelabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(usagelabel, 0, 0)
        instlabel = QLabel()
        instructions = """
Configure template and switch area hot spot
and the Common/NO/NC switch contacts.
        """
        instlabel.setText(instructions)
        instlabel.setStyleSheet("QLabel {color: rgb(0,64,128); font: 11px}")
        grid.addWidget(instlabel, 0, 1, 1, 2)
        
        # Template select
        templatelabel = QLabel('Templates')
        grid.addWidget(templatelabel, 1, 0)
        self.templatecombo = QComboBox()
        self.__templates = sorted(self.__settings[RELAY_SETTINGS].keys())
        if len(self.__templates) > 0:
            for template in self.__templates:
                self.templatecombo.addItem(str(template))
            # Select the current item
            index = self.templatecombo.findText(self.__current_template, Qt.MatchFixedString)
            if index >= 0:
                 self.templatecombo.setCurrentIndex(index)            
        grid.addWidget(self.templatecombo, 1, 1, 1, 2)
        self.templatecombo.activated.connect(self.__on_template)
        # Template add
        self.addtemplatebtn = QPushButton('Add', self)
        self.addtemplatebtn.setToolTip('Add a new template')
        self.addtemplatebtn.resize(self.addtemplatebtn .sizeHint())
        self.addtemplatebtn.setMinimumHeight(20)
        self.addtemplatebtn.setMinimumWidth(100)
        self.addtemplatebtn.setEnabled(True)
        grid.addWidget(self.addtemplatebtn, 2, 1)
        self.addtemplatebtn.clicked.connect(self.__add_template)
        # Template delete
        self.deletetemplatebtn = QPushButton('Delete', self)
        self.deletetemplatebtn.setToolTip('Delete selected template')
        self.deletetemplatebtn.resize(self.deletetemplatebtn .sizeHint())
        self.deletetemplatebtn.setMinimumHeight(20)
        self.deletetemplatebtn.setMinimumWidth(100)
        self.deletetemplatebtn.setEnabled(True)
        grid.addWidget(self.deletetemplatebtn, 2, 2)
        self.deletetemplatebtn.clicked.connect(self.__delete_template)  
        
        # Separator line
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("QFrame {background-color: rgb(126,126,126)}")
        grid.addWidget(line1, 3, 0, 1, 3)
        
        # Relay select
        relaylabel = QLabel('Relays')
        grid.addWidget(relaylabel, 4, 0)
        self.relaycombo = QComboBox()
        if len(self.__settings[RELAY_SETTINGS]) > 0:
            for key in sorted(self.__settings[RELAY_SETTINGS][self.__templates[0]].keys()):
                self.relaycombo.addItem(str(key))
        grid.addWidget(self.relaycombo, 4, 1)
        self.relaycombo.activated.connect(self.__on_relay)
        
        # Relay ID
        idlabel = QLabel('Relay ID')
        grid.addWidget(idlabel, 5, 0)
        self.idsb = QSpinBox(self)
        self.idsb.setRange(1, 16)
        self.idsb.setValue(1)
        grid.addWidget(self.idsb, 5, 1)
        self.idsb.valueChanged.connect(self.__on_id)
        
        # Radio buttons to select the current field for edit
        self.rbgroup = QButtonGroup()
        self.toplrb = QRadioButton('Top Left')
        self.botrrb = QRadioButton('Bottom Right')
        self.commrb = QRadioButton('Common')
        self.norb = QRadioButton('Normally Open')
        self.ncrb = QRadioButton('Normally Closed')
        self.rbgroup.addButton(self.toplrb)
        self.rbgroup.addButton(self.botrrb)
        self.rbgroup.addButton(self.commrb)
        self.rbgroup.addButton(self.norb)
        self.rbgroup.addButton(self.ncrb)
        grid.addWidget(self.toplrb, 6, 0)
        grid.addWidget(self.botrrb, 7, 0)
        grid.addWidget(self.commrb, 8, 0)
        grid.addWidget(self.norb, 9, 0)
        grid.addWidget(self.ncrb, 10, 0)
        
        # Field values
        self.__topllabel = QLabel('')
        self.__topllabel.setFrameShape(QFrame.Box)
        self.__topllabel.setStyleSheet("QLabel {color: rgb(255,128,64);font: bold 12px}")
        grid.addWidget(self.__topllabel, 6, 1)        
        self.__botrlabel = QLabel('')
        self.__botrlabel.setFrameShape(QFrame.Box)
        self.__botrlabel.setStyleSheet("QLabel {color: rgb(255,128,64);font: bold 12px}")
        grid.addWidget(self.__botrlabel, 7, 1)        
        self.__commlabel = QLabel('')
        self.__commlabel.setFrameShape(QFrame.Box)
        self.__commlabel.setStyleSheet("QLabel {color: rgb(255,128,64);font: bold 12px}")
        grid.addWidget(self.__commlabel, 8, 1)       
        self.__nolabel = QLabel('')
        self.__nolabel.setFrameShape(QFrame.Box)
        self.__nolabel.setStyleSheet("QLabel {color: rgb(255,128,64);font: bold 12px}")
        grid.addWidget(self.__nolabel, 9, 1)        
        self.__nclabel = QLabel('')
        self.__nclabel.setFrameShape(QFrame.Box)
        self.__nclabel.setStyleSheet("QLabel {color: rgb(255,128,64);font: bold 12px}")
        grid.addWidget(self.__nclabel, 10, 1)
        
        # Populate the coordinates
        try:
            if self.relaycombo.currentIndex() != -1:
                id = int(self.relaycombo.itemText(self.relaycombo.currentIndex()))
                coords = self.__relay_settings[self.__current_template][id]
                self.__set_coordinates(coords)
        except:
            # Forget for now, improper coord map
            pass
        
        # Actions, add/edit, delete
        self.addbtn = QPushButton('Edit/Add', self)
        self.addbtn.setToolTip('Edit/Add to list')
        self.addbtn.resize(self.addbtn.sizeHint())
        self.addbtn.setMinimumHeight(20)
        self.addbtn.setMinimumWidth(100)
        self.addbtn.setEnabled(True)
        grid.addWidget(self.addbtn, 11, 1)
        self.addbtn.clicked.connect(self.__editadd)
        
        self.delbtn = QPushButton('Delete', self)
        self.delbtn.setToolTip('Delete from list')
        self.delbtn.resize(self.addbtn.sizeHint())
        self.delbtn.setMinimumHeight(20)
        self.delbtn.setMinimumWidth(100)
        self.delbtn.setEnabled(True)
        grid.addWidget(self.delbtn, 11, 2)
        self.delbtn.clicked.connect(self.__delete)       
            
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
        self.buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
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
        
        if what == EVNT_POS:
            # Report cursor position
            if self.top_tab_widget.currentIndex() == 1:
                self.__status_bar.showMessage('x:%d, y:%d' % (data[0], data[1]))
            else:
                self.__status_bar.showMessage('')
        elif what == EVNT_LEFT:
            # Some marker point
            if self.idsb.value() not in self.__relay_settings[self.__current_template]:
                self.__relay_settings[self.__current_template][self.idsb.value()] = {}
            if self.toplrb.isChecked():
                self.__relay_settings[self.__current_template][self.idsb.value()][CONFIG_HOTSPOT_TOPLEFT] = (data[0], data[1])
            elif self.botrrb.isChecked():
                self.__relay_settings[self.__current_template][self.idsb.value()][CONFIG_HOTSPOT_BOTTOMRIGHT] = (data[0], data[1])
            elif self.commrb.isChecked():
                self.__relay_settings[self.__current_template][self.idsb.value()][CONFIG_HOTSPOT_COMMON] = (data[0], data[1])
            elif self.norb.isChecked():
                self.__relay_settings[self.__current_template][self.idsb.value()][CONFIG_HOTSPOT_NO] = (data[0], data[1])
            elif self.ncrb.isChecked():
                self.__relay_settings[self.__current_template][self.idsb.value()][CONFIG_HOTSPOT_NC] = (data[0], data[1])
            # Set user text
            coords = self.__relay_settings[self.__current_template][self.idsb.value()]
            self.__set_coordinates(coords)
    
    # PUBLIC
    #================================================================================================
    def get_template(self, ):
        """ Return the template in use """
        
        return self.__current_template
    
    # Event handlers
    #================================================================================================
    # Tab event handler
    def onTab(self, tab):
        """
        User changed tabs
        
        Arguments:
            tab --  new tab index
            
        """
        
        self.__status_bar.showMessage('')
    
    # Arduino event handlers
    def ipChanged(self, ):
        """ User edited IP address """
        
        self.__config_callback(CONFIG_NETWORK, (self.iptxt.text(), self.porttxt.text()))
        
    def portChanged(self, ):
        """ User edited port address """
        
        self.__config_callback(CONFIG_NETWORK, (self.iptxt.text(), self.porttxt.text()))
        
    # Relay event handlers
    def __on_template(self, ):
        """ Set the selected template """
        
        self.__current_template = self.templatecombo.itemText(self.templatecombo.currentIndex())
        # Copy in the hotspot settings
        self.idsb.setValue(1)   # Set back to first relay
        self.relaycombo.clear()
        self.relaycombo.setCurrentIndex(-1)
        for relay in self.__relay_settings[self.__current_template]:
            if  self.__relay_settings[self.__current_template][relay][CONFIG_HOTSPOT_TOPLEFT] != (None,None) and\
                self.__relay_settings[self.__current_template][relay][CONFIG_HOTSPOT_BOTTOMRIGHT] != (None,None) and\
                self.__relay_settings[self.__current_template][relay][CONFIG_HOTSPOT_COMMON] != (None,None) and\
                self.__relay_settings[self.__current_template][relay][CONFIG_HOTSPOT_NO] != (None,None) and\
                self.__relay_settings[self.__current_template][relay][CONFIG_HOTSPOT_NC] != (None,None):
                # We have a configured relay so add the details
                self.relaycombo.addItem(str(relay))
                coords = self.__relay_settings[self.__current_template][relay]
                self.__set_coordinates(coords)
        if self.relaycombo.count() > 0:
            self.relaycombo.setCurrentIndex(0)
        else:
            # No settings for selected relay
            self.relaycombo.setCurrentIndex(-1)            
            self.relaycombo.clear()
            self.relaycombo.setCurrentIndex(-1)
            self.__topllabel.setText('')
            self.__botrlabel.setText('')
            self.__commlabel.setText('')
            self.__nolabel.setText('')
            self.__nclabel.setText('')
            
        # Callback to UI to make the changes
        self.__config_callback(CONFIG_SEL_TEMPLATE, [self.__current_template, self.__relay_settings])
        
    def __add_template(self, ):
        """ Add a template file """
        
        # Get a list of template files
        # We only accept .png files
        template_path = self.__settings[TEMPLATE_PATH]
        files = [f for f in listdir(template_path) if (isfile(join(template_path, f)) and os.path.splitext(f)[1] == '.png' and f not in self.__templates)]
        if len(files) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)        
            msg.setText('There are no new templates!')
            msg.setWindowTitle('Add Template')
            msg.setDetailedText("To add a new template:\n  1. Create a .png image file of the layout.\n  2. Add the file to the templates directory.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            item, ok = QInputDialog.getItem(self, "Select Template", "Template", files, 0, False)
            if ok:
                # Add new template to the combo
                self.templatecombo.addItem(item)
                # Add an empty dict for this template
                self.__relay_settings[item] = {}
                # Update the template list
                self.__templates = sorted(self.__relay_settings.keys())
                # Callback to UI to make the changes
                self.__config_callback(CONFIG_NEW_TEMPLATE, [self.__current_template, self.__relay_settings])
                if len(self.__relay_settings) == 1:
                    #First template so make it active
                    self.__on_template()
    
    def __delete_template(self):
        """ Delete the selected template """
        
        # Be polite, ask user
        reply = QMessageBox.question(self, 'Delete',
            "Are you sure you want to delete template %s and all its state?\nNote this will not remove the template file itself." % (self.__current_template), QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Remove from the relay structure
            if self.__current_template in self.__relay_settings:
                del self.__relay_settings[self.__current_template]
            # Remove from the template list
            index = self.templatecombo.findText(self.__current_template)
            if index != -1:
                self.templatecombo.removeItem(index)
            # Update the template list
            self.__templates = sorted(self.__relay_settings.keys()) 
            # Callback to UI to make the changes
            self.__config_callback(CONFIG_DEL_TEMPLATE, [self.__current_template, self.__relay_settings])
            # Make the now selected template active
            self.__on_template()
                    
    def __on_relay(self, ):
        """
        User selected a new relay from the relay combo.
        These are actual configured relays.
        """
        
        # Populate the details
        id = int(self.relaycombo.itemText(self.relaycombo.currentIndex()))
        # Set the ID
        self.idsb.setValue(id)
        # Populate the coordinates
        coords = self.__relay_settings[self.__current_template][id]
        self.__set_coordinates(coords)
        # Create/edit temporary structure
        self.__relay_settings[self.__current_template][id] = {
            CONFIG_HOTSPOT_TOPLEFT: (coords[CONFIG_HOTSPOT_TOPLEFT][0], coords[CONFIG_HOTSPOT_TOPLEFT][1]),
            CONFIG_HOTSPOT_BOTTOMRIGHT: (coords[CONFIG_HOTSPOT_BOTTOMRIGHT][0], coords[CONFIG_HOTSPOT_BOTTOMRIGHT][1]),
            CONFIG_HOTSPOT_COMMON: (coords[CONFIG_HOTSPOT_COMMON][0], coords[CONFIG_HOTSPOT_COMMON][1]),
            CONFIG_HOTSPOT_NO: (coords[CONFIG_HOTSPOT_NO][0], coords[CONFIG_HOTSPOT_NO][1]),
            CONFIG_HOTSPOT_NC: (coords[CONFIG_HOTSPOT_NC][0], coords[CONFIG_HOTSPOT_NC][1])
        }
    
    def __on_id(self, ):
        """
        User selected a new relay from the spinbox.
        These are relay selections which may or may not be configured.
        """
        
        # Populate the details
        combo_id_selected = -1
        if self.relaycombo.currentIndex() != -1:
            combo_id_selected = int(self.relaycombo.itemText(self.relaycombo.currentIndex()))
        spinbox_id_selected = self.idsb.value()
        if combo_id_selected != spinbox_id_selected:
            # We have a new spinbox selection that was not the previous combo selection
            # Does this id exist in the configured relays
            index = self.relaycombo.findText(str(spinbox_id_selected))
            if index != -1:
                # Yes, we have already configured this relay so display the details
                self.relaycombo.setCurrentIndex(index)
                coords = self.__relay_settings[self.__current_template][spinbox_id_selected]
                self.__set_coordinates(coords)
            else:
                # Not configured, so user wants to configure a new relay
                self.relaycombo.setCurrentIndex(-1)
                self.__topllabel.setText('')
                self.__botrlabel.setText('')
                self.__commlabel.setText('')
                self.__nolabel.setText('')
                self.__nclabel.setText('')
                self.__relay_settings[self.__current_template][spinbox_id_selected] = {
                    CONFIG_HOTSPOT_TOPLEFT: (None, None),
                    CONFIG_HOTSPOT_BOTTOMRIGHT: (None, None),
                    CONFIG_HOTSPOT_COMMON: (None, None),
                    CONFIG_HOTSPOT_NO: (None, None),
                    CONFIG_HOTSPOT_NC: (None, None)
                }
    
    def __editadd(self, ):
        """ User wants to add/edit the current contents """
        
        index = self.relaycombo.findText(str(self.idsb.value()))
        if index == -1:
            self.relaycombo.addItem(str(self.idsb.value()))
        self.relaycombo.setCurrentIndex(self.relaycombo.findText(str(self.idsb.value())))
        self.__config_callback(CONFIG_EDIT_ADD_HOTSPOT, self.__relay_settings)
    
    def __delete(self, ):
        """ User wants to delete the selected relay and data """
        
        del self.__relay_settings[self.__current_template][self.idsb.value()]
        self.relaycombo.removeItem(self.relaycombo.currentIndex())
        self.relaycombo.setCurrentIndex(-1)
        self.__topllabel.setText('')
        self.__botrlabel.setText('')
        self.__commlabel.setText('')
        self.__nolabel.setText('')
        self.__nclabel.setText('')
        self.__config_callback(CONFIG_DELETE_HOTSPOT, self.__relay_settings)

    # Idle time processing ============================================================================================        
    def __idleProcessing(self):
        
        """
        Idle processing.
        Called every 100ms single shot
        
        """
    
        # Adjust buttons
        if  len(self.__topllabel.text()) > 0 and\
            len(self.__botrlabel.text()) > 0 and\
            len(self.__commlabel.text()) > 0 and\
            len(self.__nolabel.text()) > 0 and\
            len(self.__nclabel.text()) > 0:
            self.addbtn.setEnabled(True)
        else:
            self.addbtn.setEnabled(False)
            
        if self.relaycombo.currentIndex() != -1:
            self.delbtn.setEnabled(True)
        else:
            self.delbtn.setEnabled(False)
        
        if self.__current_template != None and len(self.__current_template) > 0:
            self.deletetemplatebtn.setEnabled(True)
        else:
            self.deletetemplatebtn.setEnabled(False)
            
        QTimer.singleShot(100, self.__idleProcessing)
        
    # Helpers =========================================================================================================
    
    def __set_coordinates(self, coords):
        """
        Set the user information coordinate data
        
        Arguments:
            coords --  current relay_settings element
            
        """
        
        if CONFIG_HOTSPOT_TOPLEFT in coords and coords[CONFIG_HOTSPOT_TOPLEFT] != (None, None):
            self.__topllabel.setText('X:%3d Y:%3d' % (coords[CONFIG_HOTSPOT_TOPLEFT][0], coords[CONFIG_HOTSPOT_TOPLEFT][1]))
        else:
            self.__topllabel.setText('')
        if CONFIG_HOTSPOT_BOTTOMRIGHT in coords and coords[CONFIG_HOTSPOT_BOTTOMRIGHT] != (None, None):
            self.__botrlabel.setText('X:%3d Y:%3d' % (coords[CONFIG_HOTSPOT_BOTTOMRIGHT][0], coords[CONFIG_HOTSPOT_BOTTOMRIGHT][1]))
        else:
            self.__botrlabel.setText('')
        if CONFIG_HOTSPOT_COMMON in coords and coords[CONFIG_HOTSPOT_COMMON] != (None, None):
            self.__commlabel.setText('X:%3d Y:%3d' % (coords[CONFIG_HOTSPOT_COMMON][0], coords[CONFIG_HOTSPOT_COMMON][1]))
        else:
            self.__commlabel.setText('')
        if CONFIG_HOTSPOT_NO in coords and coords[CONFIG_HOTSPOT_NO] != (None, None):
            self.__nolabel.setText('X:%3d Y:%3d' % (coords[CONFIG_HOTSPOT_NO][0], coords[CONFIG_HOTSPOT_NO][1]))
        else:
            self.__nolabel.setText('')
        if CONFIG_HOTSPOT_NC in coords and coords[CONFIG_HOTSPOT_NC] != (None, None):
            self.__nclabel.setText('X:%3d Y:%3d' % (coords[CONFIG_HOTSPOT_NC][0], coords[CONFIG_HOTSPOT_NC][1]))
        else:
            self.__nclabel.setText('')
    