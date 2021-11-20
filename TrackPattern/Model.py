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
import TrackPattern.View
import TrackPattern.Controller
import TrackPattern.ModelEntities

psLog = logging.getLogger('PS.Model')

def updateLocations():
    '''Updates the config file with a list of all locations for this profile'''

    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'AL': TrackPattern.ModelEntities.getAllLocations()})
    newConfigFile.update({'TP': subConfigfile})
    MainScriptEntities.writeConfigFile(newConfigFile)
    psLog.info('List of locations for this profile has been updated')

    return

def updatePatternLocation(location):
    '''Updates the config file value PL with the currently selected location'''

    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PL': location})
    newConfigFile.update({'TP': subConfigfile})
    psLog.info('The current location for this profile has been set to ' + location)

    return newConfigFile

def updatePatternTracks(trackList):
    '''Updates the config file value PT with the tracks for the selected location'''

    trackDict = {}
    for track in trackList:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})
    # psLog.info('The track list for location ' + location + ' has been updated')

    return newConfigFile

def getPatternTracks(location):
    '''Updates the config file value PT with the tracks for the selected location'''

    allTracks = TrackPattern.ModelEntities.getTracksByLocation(location, None)
    trackDict = {}
    for track in allTracks:
        trackDict[track] = False
    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PT': trackDict})
    newConfigFile.update({'TP': subConfigfile})
    # psLog.info('The track list for location ' + location + ' has been updated')

    return newConfigFile

def updateCheckBoxStatus(all, ignore):
    '''Updates the config file with the checked status of use all and ignore check boxes'''

    newConfigFile = MainScriptEntities.readConfigFile()
    subConfigfile = newConfigFile['TP']
    subConfigfile.update({'PA': all})
    subConfigfile.update({'PI': ignore})
    newConfigFile.update({'TP': subConfigfile})

    return newConfigFile

def getSetCarsData(location, track):
    '''Creates the data needed for a Set Cars to Track window'''

    trackSchedule = TrackPattern.ModelEntities.isTrackASpur(location, track)
    listForTrack = TrackPattern.ModelEntities.makeYardPattern(location, [track]) # track needs to be send in as a list
    listForTrack.update({'RT': u'Switch List for Track '})

    return listForTrack, trackSchedule

def validateUserInput(controls):
    '''Validates the user submitted locations and returns a track list for a valid location'''

    location = unicode(controls[0].text, MainScriptEntities.setEncoding())
    useAll = None
    if (controls[1].selected):
        useAll = 'Yard'
    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": location})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    trackList = {}
    focusOn.update({"PT": trackList})
    validLoc, validCombo = TrackPattern.ModelEntities.checkYard(location, useAll)
    if (validLoc):
        psLog.info('location ' + location + ' is valid')
        if (validCombo):
            psLog.info('track type verified for ' + location)
            locationTracks = TrackPattern.ModelEntities.getTracksByLocation(location, useAll)
            focusOn.update({"PL": location})
            for track in locationTracks:
                trackList[track] = True
            focusOn.update({"PT": trackList})
        else:
            psLog.warning('location ' + location + ' does not have yard tracks')
    else:
        psLog.warning('location ' + location + ' is not valid')

    return focusOn, validCombo

def updateButtons(controls):
    '''Updates the config file when a button is pressed'''

    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": controls[0].getSelectedItem()})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": TrackPattern.Model.getAllTracks(controls[3])})
    newConfigFile = MainScriptEntities.readConfigFile('all')
    newConfigFile.update({"TP": focusOn})
    MainScriptEntities.writeConfigFile(newConfigFile)

    return controls

def getTracksByType(location, type):
    '''Returns a list of tracks by type for a location'''

    return TrackPattern.ModelEntities.getTracksByLocation(location, type)

def getAllTracks(trackCheckBoxes):
    '''Returns a dictionary of track names and their check box status'''

    dict = {}
    for item in trackCheckBoxes:
        dict[unicode(item.text, MainScriptEntities.setEncoding())] = item.selected

    return dict

def makeTrackPatternDict(trackList):
    '''Make a track pattern as a dictionary'''

    trackPattern = MainScriptEntities.readConfigFile('TP')
    patternDict = TrackPattern.ModelEntities.makeYardPattern(trackPattern['PL'], trackList)
    psLog.info('dictionary for ' + trackPattern['PL'] + ' created')

    return patternDict

def getSelectedTracks():
    '''Makes a list of just the selected tracks'''

    trackPattern = MainScriptEntities.readConfigFile('TP')
    trackList = []
    for track, bool in trackPattern['PT'].items():
        if (bool):
            trackList.append(track)

    return trackList

def writePatternJson(location, trackPatternDict):
    '''Write the track pattern dictionary as a JSON file'''

    jsonCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\jsonManifests\\Track Pattern (' + location + ').json'
    jsonObject = jDumps(trackPatternDict, indent=2, sort_keys=True) #trackPatternDict
    with cOpen(jsonCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as jsonWorkFile:
        jsonWorkFile.write(jsonObject)

    return jsonObject

def writeTextSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a text switch list'''

    textCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\switchLists\\Track Pattern (' + location + ').txt'
    textObject = TrackPattern.ModelEntities.makeSwitchlist(trackPatternDict, True)
    with cOpen(textCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as textWorkFile:
        textWorkFile.write(textObject)

    return textObject

def writeCsvSwitchList(location, trackPatternDict):
    '''Write the track pattern dictionary as a CSV switch list'''

    csvSwitchlistPath = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists'
    if not (oPath.isdir(csvSwitchlistPath)):
        mkdir(csvSwitchlistPath)
    csvCopyTo = jmri.util.FileUtil.getProfilePath() + 'operations\\csvSwitchLists\\Track Pattern (' + location + ').csv'
    csvObject = TrackPattern.ModelEntities.makeCsvSwitchlist(trackPatternDict)
    with cOpen(csvCopyTo, 'wb', encoding=MainScriptEntities.setEncoding()) as csvWorkFile:
        csvWorkFile.write(csvObject)

    return
