#!/usr/bin/env python
#
# common.py
#
# Common definitions for Antenna Switch application
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

# Application imports

# ======================================================================================
# SETTINGS and STATE

# Constants for settings
PATHS = 'paths'
IMAGE = 'image'
ARDUINO_SETTINGS = 'arduinosettings'
NETWORK = 'network'
WINDOW = 'window'
RELAYS = 'relays'
RELAY_OFF = 'relayoff'
RELAY_ON = 'relayon'

# Index into comms parameters
IP = 0
PORT = 1

# Index into coordinates & window
X = 0
Y = 1
W = 2
H = 3

# Config events
CONFIG_NETWORK = 'confignetwork'
RELAY_SETTINGS = 'relaysettings'
CONFIG_HOTSPOT_TOPLEFT = 'confighotspottopleft'
CONFIG_HOTSPOT_BOTTOMRIGHT = 'confighotspotbottomright'
CONFIG_HOTSPOT_COMMON = 'confighotspotcommon'
CONFIG_HOTSPOT_NO = 'confighotspotno'
CONFIG_HOTSPOT_NC = 'confighotspotnc'
CONFIG_EDIT_ADD_HOTSPOT = 'configeditaddhotspot'
CONFIG_DELETE_HOTSPOT = 'configdeletehotspot'
CONFIG_ACCEPT = 'configaccept'
CONFIG_REJECT = 'configreject'

# Paths to state and configuration files
SETTINGS_PATH = os.path.join('..', 'settings', 'ant_control.cfg')
STATE_PATH = os.path.join('..', 'settings', 'ant_state.cfg')

DEFAULT_SETTINGS = {
    PATHS: {
        IMAGE: 'default.gif'
    },
    ARDUINO_SETTINGS: {
        NETWORK: [
            # ip, port
            None, None
        ]
    },
    RELAY_SETTINGS: {
        # Relay 0-N
        #relay-id: {CONFIG_HOTSPOT_TOPLEFT: (x,y), CONFIG_HOTSPOT_BOTTOMRIGHT: (x,y), CONFIG_HOTSPOT_COMMON: (x,y), CONFIG_HOTSPOT_NO: (x,y), CONFIG_HOTSPOT_NC: (x,y)}, relay-id: {...}, ...
    }
}

DEFAULT_STATE = {
            # X, Y, W, H
    WINDOW: [300, 300, 300, 500],
    RELAYS: {
                1: RELAY_OFF,
                2: RELAY_OFF,
                3: RELAY_OFF,
                4: RELAY_OFF,
                5: RELAY_OFF,
                6: RELAY_OFF,
                7: RELAY_OFF,
                8: RELAY_OFF,
            }
}

# ======================================================================================
# GUI

# Index for tabs
I_TAB_ARDUINO = 0

# Status messsages
TICKS_TO_CLEAR = 50

# Idle ticker
IDLE_TICKER = 100 # ms

# ======================================================================================
# GRAPHICS

# Modes
MODE_UNDEFINED = 'modeunderined'
MODE_CONFIG = 'modeconfig'
MODE_RUNTIME = 'moderuntime'

# Events
EVNT_POS = 'evntpos'
EVNT_LEFT = 'evntleft'
EVNT_MENU = 'evntmenu'