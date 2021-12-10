# coding=utf-8
# Extended ìÄÅÉî
# Data munipulation for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
from os import path as oPath
from shutil import copy as sCopy
from json import loads as jLoads, dumps as jDumps
from codecs import open as cOpen
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.ModelEntities

scriptRev = 'TrackPattern.Model v20211210'
psLog = logging.getLogger('PS.TP.Model')

def initializeConfigFile():
    '''initialize or reinitialize the track pattern part of the config file on first use, reset, or edit of a location name'''

    psLog.debug('initializeConfigFile')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    allLocations  = TrackPattern.ModelEntities.getAllLocations()
    subConfigfile.update({'AL': allLocations})
    subConfigfile.update({'PT': TrackPattern.ModelEntities.makeInitialTrackList(allLocations[0])})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updateLocations():
    '''Updates the config file with a list of all locations for this profile'''

    psLog.debug('updateLocations')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    allLocations  = TrackPattern.ModelEntities.getAllLocations()
    if not (subConfigfile['AL']): # when this sub is used for the first tims
        subConfigfile.update({'PL': allLocations[0]})
        subConfigfile.update({'PT': TrackPattern.ModelEntities.makeInitialTrackList(allLocations[0])})
    subConfigfile.update({'AL': allLocations})
    newConfigFile.update({'TP': subConfigfile})
    MainScriptEntities.writeConfigFile(newConfigFile)

    return newConfigFile

def updatePatternLocation(location):
    '''Updates the config file value PL with the currently selected location'''

    psLog.debug('updatePatternLocation')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PL': location})
    newConfigFile.update({'TP': subConfigfile})
    psLog.debug('The current location for this profile has been set to ' + location)

    return newConfigFile

def updateTrackCheckBoxes(trackCheckBoxes):
    '''Returns a dictionary of track names and their check box status'''

    psLog.debug('updateTrackCheckBoxes')
    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, MainScriptEntities.setEncoding())] = item.selected

    return dict

def updatePatternTracks(trackList):
    '''Updates list of yard tracks as the yard track only flag is toggled'''

    psLog.debug('updatePatternTracks')
    trackDict = {}
    for track in trackList:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})
    if (trackDict):
        psLog.warning('The track list for this location has changed')
    else:
        psLog.warning('There are no yard tracks for this location')

    return newConfigFile

def makeNewPatternTracks(location):
    '''Makes a new list of all tracks for a location'''

    psLog.debug('makeNewPatternTracks')
    allTracks = TrackPattern.ModelEntities.getTracksByLocation(location, None)
    trackDict = {}
    for track in allTracks:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updateCheckBoxStatus(all, ignore):
    '''Updates the config file with the checked status of Yard Tracks Only and Ignore Track Length check boxes'''

    psLog.debug('updateCheckBoxStatus')
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PA': all})
    subConfigfile.update({'PI': ignore})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def updateConfigFile(controls):
    '''Updates the track pattern part of the config file'''

    psLog.debug('updateConfigFile')
    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": TrackPattern.Model.updateTrackCheckBoxes(controls[3])})
    newConfigFile = MainScriptEntities.readConfigFile('all')
    newConfigFile.update({"TP": focusOn})
    MainScriptEntities.writeConfigFile(newConfigFile)

    return controls

def makeLoadEmptyDesignationsDict():
    '''Stores the custom car load for (empty) by type designations and the default empty designation as global variables'''

    psLog.debug('makeLoadEmptyDesignationsDict')
    defaultLoadEmpty, customEmptyForCarTypes = TrackPattern.ModelEntities.getcustomEmptyForCarType()
    try:
        MainScriptEntities.defaultLoadEmpty = defaultLoadEmpty
        psLog.info('Default empty designation saved')
    except:
        psLog.critical('Default empty designation not saved')
        MainScriptEntities.defaultLoadEmpty = 'E'
    try:
        MainScriptEntities.carTypeByEmptyDict = {}
        MainScriptEntities.carTypeByEmptyDict = customEmptyForCarTypes
        psLog.info('Default custon load (empty) by car type designations saved')
    except:
        psLog.critical('Custom car empty designations not saved')
        MainScriptEntities.carTypeByEmptyDict = {}

    return

def makeListForTrack(location, track):
    '''Creates the switch list data for a Set Cars to Track window'''

    psLog.debug('makeListForTrack')
    listForTrack = TrackPattern.Model.makeYardPattern(location, [track]) # track needs to be send in as a list
    listForTrack.update({'RT': u'Switch List for Track '})

    return listForTrack

def makeTrackList(location, type):
    '''Returns a list of tracks by type for a location'''
    psLog.debug('makeTrackList')

    return TrackPattern.ModelEntities.getTracksByLocation(location, type)

def makeYardPattern(yardLocation, trackList):
    '''Make a dictionary yard pattern
    The car rosters are sorted at this level'''

    psLog.debug('makeYardPattern')
    lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)

    patternList = []
    for i in trackList:
        j = TrackPattern.ModelEntities.getCarObjects(yardLocation, i) # list of car objects for a track
        trackRoster = [] # list of dictionaries
        for car in j:
            carDetail = TrackPattern.ModelEntities.getDetailsForCarAsDict(car)
            trackRoster.append(carDetail)
        roster2 = TrackPattern.ModelEntities.sortCarList(trackRoster)
        trackDict = {}
        trackDict['TN'] = i # track name
        trackDict['TL'] = lm.getLocationByName(yardLocation).getTrackByName(i, None).getLength() # track length
        trackDict['TR'] = roster2 # list of car dictionaries
        patternList.append(trackDict)
    yardPatternDict = {}
    yardPatternDict['RT'] = u'Report Type' # Report Type, value replaced when called
    yardPatternDict['RN'] = unicode(jmri.jmrit.operations.setup.Setup.getRailroadName(), MainScriptEntities.setEncoding())
    yardPatternDict['YL'] = yardLocation
    yardPatternDict['VT'] = unicode(MainScriptEntities.timeStamp(), MainScriptEntities.setEncoding()) # The clock time this script is run in seconds plus the offset
    yardPatternDict['ZZ'] = patternList

    return yardPatternDict

def makeTrackPatternDict(trackList):
    '''Make a track pattern as a dictionary'''

    psLog.debug('makeTrackPatternDict')
    trackPattern = MainScriptEntities.readConfigFile('TP')
    patternDict = TrackPattern.Model.makeYardPattern(trackPattern['PL'], trackList)

    return patternDict

def writePatternJson(location, trackPatternDict):
    '''Write the track pattern dictionary as a JSON file'''

    psLog.debug('writePatternJson')
    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\Track Pattern (' + location + ').json'
    jsonObject = jDumps(trackPatternDict, indent=2, sort_keys=True) #trackPatternDict
    with cOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return# jsonObject

def writeTextSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a text switch list'''

    psLog.debug('writeTextSwitchList')
    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    textObject = TrackPattern.ModelEntities.makeSwitchlist(trackPatternDict, True)
    with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textObject)

    return# textObject

def writeCsvSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a CSV switch list'''

    psLog.debug('writeCsvSwitchList')
    csvSwitchlistPath = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists'
    if not (oPath.isdir(csvSwitchlistPath)):
        mkdir(csvSwitchlistPath)
    csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Track Pattern (' + location + ').csv'
    csvObject = TrackPattern.ModelEntities.makeCsvSwitchlist(trackPatternDict)
    with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
        csvWorkFile.write(csvObject)

    return
