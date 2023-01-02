# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""
Template to serve as scaffolding for additional subroutines.
"""

from opsEntities import PSE
from TemplateSubroutine import Model
from TemplateSubroutine import View

SCRIPT_NAME = 'OperationsPatternScripts.TemplateSubroutine.Controller'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.xxx.Controller')


def startDaemons():
    """Methods called when this subroutine is initialized by the Main Script.
        These calls are not turned off.
        """

    return

def activatedCalls():
    """Methods called when this subroutine is activated."""

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    return
    
def setDropDownText():
    """Pattern Scripts/Tools/itemMethod - Set the drop down text per the config file PatternTracksSubroutine Include flag ['CP'][<subroutine name>]"""

    patternConfig = PSE.readConfigFile('CP')

    if patternConfig['TemplateSubroutine']:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    return menuText, 'xxxItemSelected'


class StartUp:
    """Start the xxx subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('xxxSubroutine makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        return
        
    def activateWidgets(self):
        """The widget.getName() value is the name of the action for the widget.
            IE 'button'
            """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def button(self, EVENT):
        """Whatever it is this button does."""

        _psLog.debug(EVENT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
