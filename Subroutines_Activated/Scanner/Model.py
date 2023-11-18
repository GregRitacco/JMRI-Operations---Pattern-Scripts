# coding=utf-8
# © 2023 Greg Ritacco

"""
Scanner subroutine.
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.SC.Model')


""" Routines called by the plugin listeners """


def resetConfigFileItems():

    return

def initializeSubroutine():

    scannerComboUpdater()
    
    return

def resetSubroutine():

    return

def refreshSubroutine():

    scannerComboUpdater()

    return

def addSubroutineListeners():
    """
    Add any listeners specific to this subroutine.
    """

    return

def removeSubroutineListeners():
    """
    Removes any listeners specific to this subroutine.
    """

    return


""" Routines specific to this subroutine """


def increaseSequenceNumber(locationName):
    """
    For every car at every track for the given location, increase the sequence number by 1000.
    """

    if not locationName:
        return
    
    for track in PSE.LM.getLocationByName(locationName).getTracksList():
        for car in PSE.CM.getList(track):
            increaseValue = int(car.getValue()) + 1000
            car.setValue(str(increaseValue))

    PSE.CMX.save()

    return

def resequenceCarsAtLocation(locationName=None):
    """
    Cars are ordered by existing sequence number,
    then given a new 600* sequence number.
    """

    if not locationName:
        locationName = PSE.readConfigFile('Patterns')['PL']

    for track in PSE.LM.getLocationByName(locationName).getTracksList():
        carSeqList = []
        for car in PSE.CM.getList(track):
            carSeqList.append((car.getValue(), car))

        carSeqList.sort(key=lambda row: row[0])
        reSequence = 6001
        for item in carSeqList:
            item[1].setValue(str(reSequence))
            reSequence += 1

    PSE.CMX.save()

    _psLog.debug('resequenceCarsAtLocation')

    return

def applyRfidData():
    """
    Not the real function that goes here.
    This one just imports a TrainPlayer file.
    """

    _psLog.debug('applyRfidData')

    fileName = 'TrainPlayer Report - rfidRoster.txt'
    targetPath = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports', fileName)
    if PSE.JAVA_IO.File(targetPath).isFile():
        rfidData = PSE.genericReadReport(targetPath).split('\n')
        rfidData = rfidData[:-1]
    else:
        print('Not found: TrainPlayer Report - rfidRoster.txt')
        return

    for data in rfidData:
        splitLine = data.split(',')
        rsName = splitLine[0].split(' ')
        rfid = splitLine[1]
        
        try:
            rs = PSE.EM.getByRoadAndNumber(rsName[0], rsName[1])
            rs.setValue('6000')
            rs.setRfid(rfid)
        except:
            rs = PSE.CM.getByRoadAndNumber(rsName[0], rsName[1])
            rs.setValue('6000')
            rs.setRfid(rfid)

    PSE.EMX.save()
    PSE.CMX.save()

    return

def scannerComboUpdater():
    """
    Updates the contents of the scanners combo box.
    """

    _psLog.debug('scannerComboUpdater')

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'sScanner')

    selectedItem = component.getSelectedItem()

    component.removeAllItems()
    pulldownList = _updateScannerList()
    for scanName in pulldownList:
        component.addItem(scanName)

    component.setSelectedItem(selectedItem)
    
    return

def _updateScannerList():
    """
    Gets the file names in the designated scanner path.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']
    dirContents = PSE.JAVA_IO.File(scannerPath).list()

    pulldownList = []
    for file in dirContents:
        pulldownList.append(file.split('.')[0])

    return pulldownList

def getScannerReportPath():
    """
    Writes the name of the selected scanner report to the config file.
    """

    configFile = PSE.readConfigFile()
    scannerPath = configFile['Scanner']['US']['SP']

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
    component = PSE.getComponentByName(frame, 'sScanner')

    itemSelected = component.getSelectedItem()
    try:
        itemSelected = itemSelected + '.txt'
        scannerReportPath = PSE.OS_PATH.join(scannerPath, itemSelected)
    except:
        scannerReportPath = None

    return scannerReportPath

def validateScanReport(scannerReportPath=None):

    _psLog.debug('validateScanReport')

    return True

def applyScanReport(scannerReportPath):
    """
    Assign a sequence number to the RS in the selected scan report.
    """

    _psLog.debug('applyScanReport')

    locoSequence = 6001
    carSequence = 6001

    scannerReport = PSE.genericReadReport(scannerReportPath)
    scannerReport = scannerReport.split('\n')
    scannerName = scannerReport.pop(0)
    scanDirection = scannerReport.pop(0)

    if scanDirection == 'W':
        scannerReport.reverse()

    e = 0
    c = 0
    for item in scannerReport:
        rs = PSE.EM.getByRfid('ID' + item)
        if rs:
            rs.setValue(str(locoSequence))
            locoSequence += 1
            e += 1
        rs = PSE.CM.getByRfid('ID' + item)
        if rs:
            rs.setValue(str(carSequence))
            carSequence += 1
            c += 1

    PSE.EMX.save()
    PSE.CMX.save()

    _psLog.info('applyScanReport for scanner: {}'.format(scannerName))
    _psLog.info('Number of engines sequenced: {}'.format(e))
    _psLog.info('Number of cars sequenced: {}'.format(c))
    print('applyScanReport for scanner: {}'.format(scannerName))
    print('Number of engines sequenced: {}'.format(e))
    print('Number of cars sequenced: {}'.format(c))

    return

def recordSelection(comboBox):
    """
    Write the combo box selected item to the configfile.
    """

    configFile = PSE.readConfigFile()
    configFile['Scanner'].update({'SI':comboBox.getSelectedItem()})
    PSE.writeConfigFile(configFile)

    return

def extendSwitchListJson():

    _psLog.debug('extendSwitchListJson')

    reportName = 'ops-Switch List.json'
    _modifyAction(reportName)

    return

def modifyManifest(propertySource):
    """
    Extends the JMRI created json manifest.
    """

    _psLog.debug(__name__ + '.modifyManifest')

    PSE.extendManifest(propertySource)
    reportName = u'train-{}.json'.format(propertySource.toString())
    _modifyAction(reportName)

    return

def _modifyAction(reportName):
    """
    Add the Scanner contribution to any manifest.
    """

    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))
    manifest = _addSequenceToManifest(report)

    PSE.genericWriteReport(reportPath, PSE.dumpJson(manifest))

    return

def _addSequenceToManifest(manifest):
    """
    Add a sequence attribute to a JMRI train manifest json.
    """

    for location in manifest['locations']:
        for car in location['cars']['add']:
            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            try:
                sequence = carObj.getValue()
            except:
                sequence = 6000
            car['sequence'] = sequence

        for car in location['cars']['remove']:
            carObj = PSE.CM.getByRoadAndNumber(car['road'], car['number'])            
            try:
                sequence = carObj.getValue()
            except:
                sequence = 6000
            car['sequence'] = sequence

    return manifest

def resequenceManifestJson(jsonFileName):
    """
    Resequences an existing json manifest by its sequence value.
    Only sequences cars at this time.
    """

    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', jsonFileName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])
        cars.sort(key=lambda row: row['location']['track']['userName'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return
