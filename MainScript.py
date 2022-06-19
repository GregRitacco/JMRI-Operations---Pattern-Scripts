# © 2021, 2022 Greg Ritacco

"""Pattern Scripts plugin for JMRI Operations Pro"""

import jmri
import java.awt
import javax.swing
from sys import path as sysPath

from java.beans import PropertyChangeListener
from apps import Apps, FileLocationPane
import time

SCRIPT_DIR = 'OperationsPatternScripts'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b1'
# SCRIPT_DIR = 'OperationsPatternScripts-2.0.0.b2'

PLUGIN_ROOT = jmri.util.FileUtil.getPreferencesPath() + SCRIPT_DIR

sysPath.append(PLUGIN_ROOT)
from psEntities import PatternScriptEntities
from psBundle import Bundle
from TrainPlayerSubroutine import BuiltTrainExport

SCRIPT_NAME = 'OperationsPatternScripts.MainScript'
SCRIPT_REV = 20220101

PatternScriptEntities.JMRI = jmri
PatternScriptEntities.JAVA_AWT = java.awt
PatternScriptEntities.JAVX_SWING = javax.swing

PatternScriptEntities.PLUGIN_ROOT = PLUGIN_ROOT
PatternScriptEntities.ENCODING = PatternScriptEntities.readConfigFile('CP')['SE']
PatternScriptEntities.BUNDLE = Bundle.getBundleForLocale()


class TrainsTableListener(PatternScriptEntities.JAVX_SWING.event.TableModelListener):
    """Catches user add or remove train while TrainPlayer support is enabled"""

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener)
            # Does not throw error if there is no listener to remove :)
            train.addPropertyChangeListener(self.builtTrainListener)

        return

class BuiltTrainListener(java.beans.PropertyChangeListener):
    """Starts TrainPlayer manifest export on trainBuilt"""

    def propertyChange(self, TRAIN_BUILT):

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue \
                and PatternScriptEntities.CheckTpDestination().directoryExists():

            tpManifest = BuiltTrainExport.ManifestForTrainPlayer()
            tpManifest.passInTrain(TRAIN_BUILT.getSource())
            tpManifest.start()

        return

class PatternScriptsWindowListener(PatternScriptEntities.JAVA_AWT.event.WindowListener):
    """Listener to respond to the plugin window operations.
    A bit verbose because of intended expansion in v3.
    """

    def __init__(self):

        return

    def closeSetCarsWindows(self):
        """Close all the Set Cars windows when the Pattern Scripts window is closed"""

        for frameName in PatternScriptEntities.JMRI.util.JmriJFrame.getFrameList():
            frame = PatternScriptEntities.JMRI.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'setCarsWindow':
                frame.setVisible(False)
                frame.dispose()

        return

    def windowClosed(self, WINDOW_CLOSED):

        self.closeSetCarsWindows()
        WINDOW_CLOSED.getSource().dispose()

        return

    def windowClosing(self, WINDOW_CLOSING):

        updateWindowParams(WINDOW_CLOSING.getSource())

        return

    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowOpened(self, WINDOW_OPENED):
        return
    def windowActivated(self, WINDOW_ACTIVATED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return

def updateWindowParams(window):

    configPanel = PatternScriptEntities.readConfigFile()
    configPanel['CP'].update({'PH': window.getHeight()})
    configPanel['CP'].update({'PW': window.getWidth()})
    configPanel['CP'].update({'PX': window.getX()})
    configPanel['CP'].update({'PY': window.getY()})
    PatternScriptEntities.writeConfigFile(configPanel)

    return

class Model:

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.Model')

        return

    def validatePatternConfig(self):
        """To be reworked in v3"""

        if not PatternScriptEntities.validateConfigFileVersion():
            PatternScriptEntities.mergeConfigFiles()
            self.psLog.info('Previous PatternConfig.json merged with new')
            PatternScriptEntities.writeNewConfigFile()
            self.psLog.warning('New PatternConfig.json file created for this profile')

        return

    def makePatternScriptsPanel(self, pluginPanel):

        for subroutine in self.makeSubroutineList():
            pluginPanel.add(PatternScriptEntities.JAVX_SWING.Box.createRigidArea(PatternScriptEntities.JAVA_AWT.Dimension(0,10)))
            pluginPanel.add(subroutine)
        return pluginPanel

    def makeSubroutineList(self):

        subroutineList = []
        controlPanelConfig = PatternScriptEntities.readConfigFile('CP')
        for subroutineIncludes, isIncluded in controlPanelConfig['SI'].items():
            if (isIncluded):
                xModule = __import__(subroutineIncludes, fromlist=['Controller'])
                startUp = xModule.Controller.StartUp()
                subroutineFrame = startUp.makeSubroutineFrame()
                subroutineList.append(subroutineFrame)
                self.psLog.info(subroutineIncludes + ' subroutine added to control panel')

        return subroutineList

class View:

    def __init__(self, scrollPanel):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.View')

        self.controlPanel = scrollPanel
        self.psPluginMenuItems = []

        return

    def makePsButton(self):

        psButton = PatternScriptEntities.JAVX_SWING.JButton(name='psButton')
        psButton.setText(PatternScriptEntities.BUNDLE['Pattern Scripts'])

        return psButton

    def makePluginPanel(self):

        # pluginPanel = PatternScriptEntities.JAVX_SWING.JPanel()
        pluginPanel = PatternScriptEntities.JAVX_SWING.Box(PatternScriptEntities.JAVX_SWING.BoxLayout.PAGE_AXIS)

        return pluginPanel

    def makeScrollPanel(self, pluginPanel):

        scrollPanel = PatternScriptEntities.JAVX_SWING.JScrollPane(pluginPanel)
        scrollPanel.border = PatternScriptEntities.JAVX_SWING.BorderFactory.createLineBorder(PatternScriptEntities.JAVA_AWT.Color.GRAY)

        return scrollPanel

    def getPsPluginMenuItems(self):

        return self.psPluginMenuItems

    def makePatternScriptsWindow(self):

        uniqueWindow = PatternScriptEntities.JMRI.util.JmriJFrame()

        asMenuItem = self.makeMenuItem(self.setAsDropDownText())
        tpMenuItem = self.makeMenuItem(self.setTiDropDownText())
        ptMenuItem = self.makeMenuItem(self.setPtDropDownText())
        helpMenuItem = self.makeMenuItem(self.setHmDropDownText())
        gitHubMenuItem = self.makeMenuItem(self.setGhDropDownText())
        opsFolderMenuItem = self.makeMenuItem(self.setOfDropDownText())
        logMenuItem = self.makeMenuItem(self.setLmDropDownText())
        editConfigMenuItem = self.makeMenuItem(self.setEcDropDownText())

        toolsMenu = PatternScriptEntities.JAVX_SWING.JMenu(PatternScriptEntities.BUNDLE['Tools'])
        toolsMenu.add(PatternScriptEntities.JMRI.jmrit.operations.setup.OptionAction())
        toolsMenu.add(PatternScriptEntities.JMRI.jmrit.operations.setup.PrintOptionAction())
        toolsMenu.add(PatternScriptEntities.JMRI.jmrit.operations.setup.BuildReportOptionAction())
        toolsMenu.add(asMenuItem)
        toolsMenu.add(tpMenuItem)
        toolsMenu.add(editConfigMenuItem)
        toolsMenu.add(ptMenuItem)

        helpMenu = PatternScriptEntities.JAVX_SWING.JMenu(PatternScriptEntities.BUNDLE['Help'])
        helpMenu.add(helpMenuItem)
        helpMenu.add(gitHubMenuItem)
        helpMenu.add(opsFolderMenuItem)
        helpMenu.add(logMenuItem)

        psMenuBar = PatternScriptEntities.JAVX_SWING.JMenuBar()
        psMenuBar.add(toolsMenu)
        psMenuBar.add(PatternScriptEntities.JMRI.jmrit.operations.OperationsMenu())
        psMenuBar.add(PatternScriptEntities.JMRI.util.WindowMenu(uniqueWindow))
        psMenuBar.add(helpMenu)

        uniqueWindow.setName('patternScriptsWindow')
        uniqueWindow.setTitle(PatternScriptEntities.BUNDLE['Pattern Scripts'])
        uniqueWindow.addWindowListener(PatternScriptsWindowListener())
        uniqueWindow.setJMenuBar(psMenuBar)
        uniqueWindow.add(self.controlPanel)
        uniqueWindow.pack()
        configPanel = PatternScriptEntities.readConfigFile('CP')
        uniqueWindow.setSize(configPanel['PW'], configPanel['PH'])
        uniqueWindow.setLocation(configPanel['PX'], configPanel['PY'])
        uniqueWindow.setVisible(True)

        return

    def makeMenuItem(self, itemMethod):

        itemText, itemName = itemMethod

        menuItem = PatternScriptEntities.JAVX_SWING.JMenuItem(itemText)
        menuItem.setName(itemName)
        self.psPluginMenuItems.append(menuItem)

        return menuItem

    def setAsDropDownText(self):
        """itemMethod - Set the drop down text per the Apply Schedule flag"""

        patternConfig = PatternScriptEntities.readConfigFile('PT')
        if patternConfig['AS']:
            menuText = PatternScriptEntities.BUNDLE['Do Not Apply Schedule']
        else:
            menuText = PatternScriptEntities.BUNDLE['Apply Schedule']

        return menuText, 'asItemSelected'

    def setTiDropDownText(self):
        """itemMethod - Set the drop down text per the TrainPlayer Include flag"""

        patternConfig = PatternScriptEntities.readConfigFile('PT')
        if patternConfig['TI']:
            menuText = PatternScriptEntities.BUNDLE['Disable TrainPlayer']
        else:
            menuText = PatternScriptEntities.BUNDLE['Enable TrainPlayer']

        return menuText, 'tpItemSelected'

    def setPtDropDownText(self):
        """itemMethod - Set the drop down text for the Translate Plugin item"""

        menuText = PatternScriptEntities.BUNDLE['Translate Plugin']

        return menuText, 'ptItemSelected'

    def setHmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item"""

        menuText = PatternScriptEntities.BUNDLE['Window Help...']

        return menuText, 'helpItemSelected'

    def setLmDropDownText(self):
        """itemMethod - Set the drop down text for the Log menu item"""

        menuText = PatternScriptEntities.BUNDLE['View Log File']

        return menuText, 'logItemSelected'

    def setGhDropDownText(self):
        """itemMethod - Set the drop down text for the gitHub page item"""

        menuText = PatternScriptEntities.BUNDLE['GitHub Web Page']

        return menuText, 'ghItemSelected'

    def setEcDropDownText(self):
        """itemMethod - Set the drop down text for the edit config file item"""

        menuText = PatternScriptEntities.BUNDLE['Edit Config File']

        return menuText, 'ecItemSelected'

    def setOfDropDownText(self):
        """itemMethod - Set the drop down text for the edit config file item"""

        menuText = PatternScriptEntities.BUNDLE['Operations Folder']

        return menuText, 'ofItemSelected'

class Controller(PatternScriptEntities.JMRI.jmrit.automat.AbstractAutomaton):

    def init(self):

        logPath = PatternScriptEntities.PROFILE_PATH  + 'operations\\buildstatus\\PatternScriptsLog.txt'
        self.logger = PatternScriptEntities.Logger(logPath)
        self.logger.startLogger('PS')

        self.model = Model()

        self.trainsTableModel = PatternScriptEntities.JMRI.jmrit.operations.trains.TrainsTableModel()
        self.builtTrainListener = BuiltTrainListener()
        self.trainsTableListener = TrainsTableListener(self.builtTrainListener)

        self.menuItemList = []

        return

    def addPatternScriptsButton(self):
        """The Pattern Scripts button on the PanelPro frame"""

        self.patternScriptsButton = View(None).makePsButton()
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonAction
        Apps.buttonSpace().add(self.patternScriptsButton)
        Apps.buttonSpace().revalidate()

        return

    def addTrainsTableListener(self):

        self.trainsTableModel.addTableModelListener(self.trainsTableListener)

        return

    def removeTrainsTableListener(self):

        self.trainsTableModel.removeTableModelListener(self.trainsTableListener)

        return

    def addBuiltTrainListener(self):

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.addPropertyChangeListener(self.builtTrainListener)

        return

    def removeBuiltTrainListener(self):

        trainList = PatternScriptEntities.TM.getTrainsByIdList()
        for train in trainList:
            train.removePropertyChangeListener(self.builtTrainListener)

        return

    def patternScriptsButtonAction(self, MOUSE_CLICKED):

        self.patternScriptsButton.setText(PatternScriptEntities.BUNDLE['Restart with default settings'])
        self.patternScriptsButton.actionPerformed = self.patternScriptsButtonRestartAction
        self.buildThePlugin()

        return

    def patternScriptsButtonRestartAction(self, MOUSE_CLICKED):

        PatternScriptEntities.deleteConfigFile()
        PatternScriptEntities.BUNDLE = Bundle.getBundleForLocale()
        self.patternScriptsButton.setText(PatternScriptEntities.BUNDLE['Restart with default settings'])

        self.removeTrainsTableListener()
        self.removeBuiltTrainListener()

        self.closePsWindow()
        self.logger.stopLogger('PS')

        self.logger.startLogger('PS')
        self.buildThePlugin()

        self.psLog.info('Pattern Scripts plugin restarted')

        return

    def closePsWindow(self):

        for frameName in PatternScriptEntities.JMRI.util.JmriJFrame.getFrameList():
            frame = PatternScriptEntities.JMRI.util.JmriJFrame.getFrame(frameName)
            if frame.getName() == 'patternScriptsWindow':
                updateWindowParams(frame)
                frame.setVisible(False)
                frame.dispose()

        return

    def buildThePlugin(self):

        PatternScriptEntities.BUNDLE = Bundle.getBundleForLocale()

        view = View(None)
        emptyPluginPanel = view.makePluginPanel()
        populatedPluginPanel = self.model.makePatternScriptsPanel(emptyPluginPanel)

        scrollPanel = view.makeScrollPanel(populatedPluginPanel)
        patternScriptsWindow = View(scrollPanel)
        patternScriptsWindow.makePatternScriptsWindow()
        self.menuItemList = patternScriptsWindow.getPsPluginMenuItems()

        self.addMenuItemListeners()

        return

    def addTrainPlayerListeners(self):

        if PatternScriptEntities.readConfigFile('PT')['TI']:
            self.addTrainsTableListener()
            self.addBuiltTrainListener()

        return

    def addMenuItemListeners(self):
        """Use the pull down item names as the attribute to set the
        listener: asItemSelected, tpItemSelected, logItemSelected, helpItemSelected
        """

        for menuItem in self.menuItemList:
            menuItem.addActionListener(getattr(self, menuItem.getName()))

        return

    def asItemSelected(self, AS_ACTIVATE_EVENT):
        """menu item-Tools/Apply Schedule"""

        self.psLog.debug(AS_ACTIVATE_EVENT)
        patternConfig = PatternScriptEntities.readConfigFile()

        if patternConfig['PT']['AS']:
            patternConfig['PT'].update({'AS': False})
            AS_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Apply Schedule"])
            self.psLog.info('Apply Schedule turned off')
            print('Apply Schedule turned off')
        else:
            patternConfig['PT'].update({'AS': True})
            AS_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Do Not Apply Schedule"])
            self.psLog.info('Apply Schedule turned on')
            print('Apply Schedule turned on')

        PatternScriptEntities.writeConfigFile(patternConfig)

        return

    def tpItemSelected(self, TP_ACTIVATE_EVENT):
        """menu item-Tools/Enable Trainplayer"""

        self.psLog.debug(TP_ACTIVATE_EVENT)
        patternConfig = PatternScriptEntities.readConfigFile()

        if patternConfig['PT']['TI']: # If enabled, turn it off
            patternConfig['PT'].update({'TI': False})
            TP_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Enable TrainPlayer"])

            self.trainsTableModel.removeTableModelListener(self.trainsTableListener)
            self.removeBuiltTrainListener()

            self.psLog.info('TrainPlayer support deactivated')
            print('TrainPlayer support deactivated')
        else:
            patternConfig['PT'].update({'TI': True})
            TP_ACTIVATE_EVENT.getSource().setText(PatternScriptEntities.BUNDLE["Disable TrainPlayer"])

            self.trainsTableModel.addTableModelListener(self.trainsTableListener)
            self.addBuiltTrainListener()

            self.psLog.info('TrainPlayer support activated')
            print('TrainPlayer support activated')

        PatternScriptEntities.writeConfigFile(patternConfig)

        return

    def ptItemSelected(self, TRANSLATE_PLUGIN_EVENT):
        """menu item-Tools/Translate Plugin"""

        self.psLog.debug(TRANSLATE_PLUGIN_EVENT)

        Bundle.createBundleForLocale()
        # Bundle.createBundleForHelpPage()

        return

    def helpItemSelected(self, OPEN_HELP_EVENT):
        """menu item-Help/Window help..."""

        self.psLog.debug(OPEN_HELP_EVENT)

        stubPath = PatternScriptEntities.JMRI.util.FileUtil.getPreferencesPath() + 'jmrihelp/psStub.html'
        stubUri = PatternScriptEntities.JAVA_IO.File(stubPath).toURI()
        if PatternScriptEntities.JAVA_IO.File(stubUri).isFile():
            PatternScriptEntities.JAVA_AWT.Desktop.getDesktop().browse(stubUri)
        else:
            self.psLog.warning('Help file not found')

        return

    def logItemSelected(self, OPEN_LOG_EVENT):
        """menu item-Help/View Log"""

        self.psLog.debug(OPEN_LOG_EVENT)

        logFileName, patternLog = PatternScriptEntities.makePatternLog()
        logFilePath = PatternScriptEntities.PROFILE_PATH + 'operations\\buildstatus\\' + logFileName + '.txt'
        PatternScriptEntities.genericWriteReport(logFilePath, patternLog)

        fileToOpen = PatternScriptEntities.JAVA_IO.File(logFilePath)
        if fileToOpen.isFile():
            PatternScriptEntities.genericDisplayReport(fileToOpen)
        else:
            self.psLog.warning('Not found: ' + logFilePath)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def ghItemSelected(self, OPEN_GH_EVENT):
        """menu item-Help/GitHub Page"""

        self.psLog.debug(OPEN_GH_EVENT)

        ghPagePath = 'https://github.com//GregRitacco//OperationsPatternScripts'
        PatternScriptEntities.JMRI.util.HelpUtil.openWebPage(ghPagePath)

        return

    def ecItemSelected(self, OPEN_EC_EVENT):
        """menu item-Help/Edit Config File"""

        self.psLog.debug(OPEN_EC_EVENT)

        configPath = PatternScriptEntities.PROFILE_PATH + 'operations\\PatternConfig.json'
        fileToOpen = PatternScriptEntities.JAVA_IO.File(configPath)
        if fileToOpen.isFile():
            apps.SystemConsole.getConsole().setVisible(True)
            PatternScriptEntities.genericDisplayReport(fileToOpen)
        else:
            self.psLog.warning('Not found: ' + configPath)

        return

    def ofItemSelected(self, OPEN_OF_EVENT):
        """menu item-Help/Operations Folder"""

        self.psLog.debug(OPEN_OF_EVENT)

        opsFolderPath = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        opsFolder = PatternScriptEntities.JAVA_IO.File(opsFolderPath)
        if opsFolder.exists():
            PatternScriptEntities.JAVA_AWT.Desktop.getDesktop().open(opsFolder)
        else:
            self.psLog.warning('Not found: ' + opsFolderPath)

        return

    def handle(self):

        # Bundle.translateItems()

        yTimeNow = time.time()
        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.Controller')
        self.logger.initialLogMessage(self.psLog)

        self.model.validatePatternConfig()
        PatternScriptEntities.validateFileDestinationDirestories()
        PatternScriptEntities.validateStubFile().isStubFile()
        self.addTrainPlayerListeners()
        if PatternScriptEntities.readConfigFile()['CP']['AP']:
            self.addPatternScriptsButton()

        self.psLog.info('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        self.psLog.info('Main script run time (sec): ' + ('%s' % (time.time() - yTimeNow))[:6])
        print('Current Pattern Scripts directory: ' + PLUGIN_ROOT)
        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return False

Controller().start()
