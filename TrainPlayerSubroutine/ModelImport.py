# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Use the TP inventory, locations and industries text files to generate the tpRailroadData.json file"""

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelImport'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelImport')

class TrainPlayerImporter:

    def __init__(self):

        self.tpLocationsFile = 'TrainPlayer Report - Locations.txt'
        self.tpIndustriesFile = 'TrainPlayer Report - Industries.txt'
        self.tpInventoryFile = 'TrainPlayer Report - Inventory.txt'

        self.tpLocations = []
        self.tpIndustries = []
        self.tpInventory = []
        self.okCounter = 0

        self.rrFile = PatternScriptEntities.PROFILE_PATH + 'operations\\tpRailroadData.json'
        self.rr = {}

        return

    def getTpReportFiles(self):
        """Needs to do more if the files don't check"""

        try:
            self.tpLocations = ModelEntities.getTpExport(self.tpLocationsFile)
            _psLog.info('TrainPlayer Locations file OK')
            self.okCounter += 1
        except:
            _psLog.warning('TrainPlayer Locations file not found')
            print('Not found: ' + self.tpLocationsFile)

        try:
            self.tpIndustries = ModelEntities.getTpExport(self.tpIndustriesFile)
            _psLog.info('TrainPlayer Industries file OK')
            self.okCounter += 1
        except:
            _psLog.warning('TrainPlayer Locations file not found')
            print('Not found: ' + self.tpIndustriesFile)

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpInventoryFile)
            _psLog.info('TrainPlayer Inventory file OK')
            self.okCounter += 1
        except:
            _psLog.warning('TrainPlayer Inventory file not found')
            print('Not found: ' + self.tpInventoryFile)

        return

    def processFileHeaders(self):
        """Process the header info from the TP report files"""

        _psLog.debug('processFileHeaders')

        self.rr[u'trainplayerDate'] = self.tpLocations.pop(0)
        self.rr[u'railroadName'] = self.tpLocations.pop(0)
        self.rr[u'railroadDescription'] = self.tpLocations.pop(0)
        self.rr[u'date'] = PatternScriptEntities.timeStamp()
        self.tpLocations.pop(0) # Remove key

        self.tpIndustries.pop(0) # Remove date
        self.tpIndustries.pop(0) # Remove key

        self.tpInventory.pop(0) # Remove date
        self.tpInventory.pop(0) # Remove key

        return


    def getRrLocations(self):
        """self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
            Makes a list of just the locations.
            """
        _psLog.debug('getRrLocations')

        locationList = [u'Unknown']
        rrLocations = {}

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            locationList.append(splitLine[1])

        self.rr['locations'] = list(set(locationList))

        return

    def getRrLocales(self):
        """self.tpLocations format: TP ID; JMRI Location Name; JMRI Track Name; TP Label; TP Type; TP Spaces.
            Makes a list of tuples of the locales and their data.
            locale format: (location, {ID, Capacity, Type, Track})
            """
        _psLog.debug('getRrLocales')

        localeList = []
        seed = ('Unknown', {u'ID': '00', u'track': '~', u'type': 'Yard', u'capacity': '100'})
        localeList.append(seed)



        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            x = (splitLine[1], {u'ID': splitLine[0], u'track': splitLine[2], u'type': self.getTrackType(splitLine[4]), u'capacity': splitLine[5]})
            localeList.append(x)

        self.rr['locales'] = localeList

        return

    def getTrackType(self, tpType):
        """Convert TP track types into JMRI track types."""

        rubric = {'industry': u'Spur', u'interchange': 'Interchange', u'staging': 'Staging', u'class yard': 'Yard'}

        return rubric[tpType]

    def getAllTpIndustry(self):
        """self.tpIndustryList format: ID, JMRI Location Name, JMRI Track Name, Industry, AAR, S/R, Load, Staging, ViaIn
            Makes a list of tuples of the industries and their data.
            industry format: (JMRI Location Name, {ID, JMRI Track Name, Industry, AAR, S/R, Load, Staging, ViaIn})
            """

        _psLog.debug('getAllTpIndustry')

        industryList = []
        for lineItem in self.tpIndustries:
            splitLine = lineItem.split(';')
            x = (splitLine[1], {u'ID': splitLine[0], u'track': splitLine[2], u'label': splitLine[3], u'type': splitLine[4], u's/r': splitLine[5], u'load': splitLine[6], u'staging': splitLine[7], u'viain': splitLine[8]})
            industryList.append(x)

        self.rr['industries'] = industryList

        return

    def getAllTpRoads(self):

        _psLog.debug('getAllTpRoads')

        roadList = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            roadList.append(road)

        self.rr['roads'] = list(set(roadList))

        return

    def getAllTpCarAar(self):

        _psLog.debug('getAllTpCarAar')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                allItems.append(splitItem[2])

        self.rr['carAAR'] = list(set(allItems))

        return

    def getAllTpCarLoads(self):

        _psLog.debug('getAllTpCarLoads')

        carLoads = {}
        xList = []
        for lineItem in self.tpIndustries:
            splitLine = lineItem.split(';')
            xList.append((splitLine[4], splitLine[6]))

        for aar in self.rr['carAAR']:
            loadList = []
            for item in xList:
                if item[0] == aar:
                    loadList.append(item[1])
            carLoads[aar] = list(set(loadList))

        self.rr['carLoads'] = carLoads

        return

    def getAllTpCarKernels(self):

        _psLog.debug('getAllTpCarKernels')

        allItems = []

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                allItems.append(splitItem[6])

        self.rr['carKernel'] = list(set(allItems))

        return

    def getAllTpLocoTypes(self):
        """Don't include tenders"""

        _psLog.debug('getAllTpLocoTypes')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append(splitItem[2])

        self.rr['locoTypes'] = list(set(allItems))

        return

    def getAllTpLocoModels(self):
        """character length fromOperations.xml\<max_len_string_attibute length="10" />
            List of tuples: (JMRI model, JMRI type)
            Don't include tenders
            """
        _psLog.debug('getAllTpLocoModels')

        allItems = []

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append((splitItem[1][0:11], splitItem[2]))

        self.rr['locoModels'] = list(set(allItems))

        return

    def getAllTpLocoConsists(self):

        _psLog.debug('getAllTpLocoConsists')

        allItems = []
        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('ET'):
                continue
            if splitItem[2].startswith('E'):
                allItems.append(splitItem[6])

        self.rr['locoConsists'] = list(set(allItems))

        return

    def writeTPLayoutData(self):

        _psLog.debug('writeTPLayoutData')

        formattedRrFile = PatternScriptEntities.dumpJson(self.rr)
        PatternScriptEntities.genericWriteReport(self.rrFile, formattedRrFile)

        return
