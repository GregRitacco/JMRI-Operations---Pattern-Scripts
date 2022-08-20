# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ViewEntities

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.View'
SCRIPT_REV = 20220101

class ManageGui:

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.View')

        return

    def makeSubroutineFrame(self):
        """Make the frame that all the Track Pattern controls are added to"""

        subroutineFrame = PatternScriptEntities.JAVX_SWING.JPanel() # the Track Pattern panel
        subroutineFrame.setLayout(PatternScriptEntities.JAVX_SWING.BoxLayout(
                subroutineFrame, PatternScriptEntities.JAVX_SWING.BoxLayout.Y_AXIS))
        subroutineFrame.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createTitledBorder( \
                PatternScriptEntities.BUNDLE['Track Pattern Subroutine'] \
                )

        return subroutineFrame

    def makeSubroutinePanel(self):
        """Make the Track Pattern controls"""

        self.psLog.debug('View.makeSubroutinePanel')

        trackPatternPanel = ViewEntities.TrackPatternPanel()
        subroutinesPanel = trackPatternPanel.makeTrackPatternPanel()
        subroutinePanelWidgets = trackPatternPanel.getPanelWidgets()

        return subroutinesPanel, subroutinePanelWidgets

    print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
