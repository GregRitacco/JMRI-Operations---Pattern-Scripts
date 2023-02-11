# coding=utf-8
# © 2023 Greg Ritacco

"""
Throwback
"""

from opsEntities import PSE
from Subroutines.Throwback import ViewEntities

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.TB.View')

class ManageGui:

    def __init__(self):

        self.configFile = PSE.readConfigFile('Throwback')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the throwback controls are added to"""

        subroutineFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        subroutineFrame.setName(__package__)
        subroutineFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE['Throwback Subroutine'])

        return subroutineFrame

    def makeSubroutineGui(self):
        """Make the throwback GUI."""

        _psLog.debug('ThrowbackSubroutine.View.makeSubroutineGui')

        subroutineGui = ViewEntities.subroutineGui()
        gui = subroutineGui.guiMaker()
        widgets = subroutineGui.guiWidgetGetter()

        return gui, widgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
