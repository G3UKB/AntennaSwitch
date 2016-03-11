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
TEMPLATE_PATH = 'templatepath'
IMAGE = 'image'
ARDUINO_SETTINGS = 'arduinosettings'
NETWORK = 'network'
WINDOW = 'window'
TEMPLATE = 'template'
RELAYS = 'relays'
MACROS = 'macros'
TT = 0  # Tooltip for macro
RELAY_OFF = 'relayoff'
RELAY_ON = 'relayon'
MAX_RLYS = 8
MAX_MACROS = 6

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
CONFIG_NEW_TEMPLATE = 'confignewtemplate'
CONFIG_SEL_TEMPLATE = 'configseltemplate'
CONFIG_DEL_TEMPLATE = 'configdeltemplate'

# Runtime events
RUNTIME_RELAY_UPDATE = 'runtimereplayupdate'

# Paths to state and configuration files
SETTINGS_PATH = os.path.join('..', 'settings', 'ant_control.cfg')
STATE_PATH = os.path.join('..', 'settings', 'ant_state.cfg')

DEFAULT_SETTINGS = {
    TEMPLATE_PATH: os.path.join('..','templates'), #Path to template files
    ARDUINO_SETTINGS: {
        NETWORK: [
            # ip, port
            None, None
        ]
    },
    RELAY_SETTINGS: {
        # TemplateFile: {
            # Relay 0-N
            # relay-id: {CONFIG_HOTSPOT_TOPLEFT: (x,y), CONFIG_HOTSPOT_BOTTOMRIGHT: (x,y), CONFIG_HOTSPOT_COMMON: (x,y), CONFIG_HOTSPOT_NO: (x,y), CONFIG_HOTSPOT_NC: (x,y)},
            # relay-id: {...}, ...
        # },
        # TemplateFile: {...}
        # 'default.png': {},
    }
}

DEFAULT_STATE = {
            # X, Y, W, H
    WINDOW: [300, 300, 300, 500],
    TEMPLATE: '',
    
    RELAYS: {
        
    #            TemplateFile: {
    #                1: RELAY_STATE,
    #                2: RELAY_STATE,
    #                3: RELAY_STATE,
    #                4: RELAY_STATE,
    #                5: RELAY_STATE,
    #                6: RELAY_STATE,
    #                7: RELAY_STATE,
    #                8: RELAY_STATE,
    #            },
    },
    MACROS: {
    #            TemplateFile: {
    #               1: {
    #                       TT: tooltip,
    #                       1: RELAY_STATE,
    #                       2: RELAY_STATE,
    #                       3: RELAY_STATE,
    #                       4: RELAY_STATE,
    #                       5: RELAY_STATE,
    #                       6: RELAY_STATE,
    #                       7: RELAY_STATE,
    #                       8: RELAY_STATE,
    #               },
    #               2: ...
    #    
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