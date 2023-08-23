# coding=utf-8
# © 2023 Greg Ritacco

"""
Calls other subs make to this one
Keep this as light as possible.
"""

from opsEntities import PSE
from Subroutines.Patterns import Model
from Subroutines.Patterns import Listeners

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

def activatedCalls():
    """
    Methods called when this subroutine is activated.
    """

    Listeners.removePatternListeners()
    Listeners.addPatternsListeners()

    return

def deactivatedCalls():
    """
    ethods called when this subroutine is deactivated.
    """

    Listeners.removePatternListeners()
    
    PSE.closeOpsWindows('popupFrame')
    PSE.closeOpsWindows('setCarsWindow')

    return

def refreshCalls():
    """
    Methods called when the subroutine needs to be refreshed.
    """

    Model.refreshSubroutine()

    return

def resetCalls():
    """
    Methods called to reset this subroutine.
    """

    Model.resetConfigFileItems()
    
    return

def specificCalls():
    """
    Methods called to run specific tasks.
    """

    return
    