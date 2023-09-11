# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from Subroutines.jPlus import Listeners

def startupCalls():
    """
    Called when the plugin is started.
    """
    
    Listeners.addSubroutineListeners()

    return

def shutdownCalls():
    """
    Called when the plugin is shut down.
    """

    Listeners.removeSubroutineListeners()
    
    return
