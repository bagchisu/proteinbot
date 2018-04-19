#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""

import requests
import xml.etree.ElementTree as ET
from sets import Set

SEARCH_URL = 'https://www.rcsb.org/pdb/rest/search/?req=browser'

BROWSER_URL = 'http://www.rcsb.org/pdb/results/results.do?qrid='

COMP_QUERY = """
<orgPdbCompositeQuery version=\"1.0\">

<queryRefinement>
<queryRefinementLevel>0</queryRefinementLevel>
<orgPdbQuery>
<queryType>org.pdb.query.simple.UpAccessionIdQuery</queryType>
<accessionIdList>{uniprotIds}</accessionIdList>
</orgPdbQuery>
</queryRefinement>

<queryRefinement>
<queryRefinementLevel>1</queryRefinementLevel>
<conjunctionType>and</conjunctionType>
<orgPdbQuery>
<queryType>org.pdb.query.simple.ExpTypeQuery</queryType>
<mvStructure.expMethod.value>{expMethod}</mvStructure.expMethod.value>
</orgPdbQuery>
</queryRefinement>

</orgPdbCompositeQuery>
"""

QUERY = """
<orgPdbQuery>
<queryType>org.pdb.query.simple.UpAccessionIdQuery</queryType>
<accessionIdList>${uniprotIds}</accessionIdList>
</orgPdbQuery>
"""

HEADERS= {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

CUSTOM_REPORT_URL = 'http://www.rcsb.org/pdb/rest/customReport'

class ExpMethod:
    XRay = 'X-RAY'
    SolutionNMR = 'SOLUTION NMR'
    ElectronMicroscopy = 'ELECTRON MICROSCOPY'

_uniprotNamesDict = dict()
for line in open('uniprot_names.txt', 'r'):
    up_data = line.split('\t')
    _uniprotNamesDict[up_data[0]] = up_data[1].strip()

def getUniProtName(uniprotId):
    return _uniprotNamesDict[uniprotId]

def search(uniprotIds, expMethod=None):
    
    if (expMethod is None):
        response = requests.post(SEARCH_URL, data=QUERY.format(uniprotIds=uniprotIds), headers=HEADERS)
    else:
        response = requests.post(SEARCH_URL, data=COMP_QUERY.format(uniprotIds=uniprotIds, expMethod=expMethod), headers=HEADERS)

    if response.status_code == 200:
        pdbChainIds = response.text.split()
        lastIndex = len(pdbChainIds)-1
        pdbIds = []
        for p in pdbChainIds[0:lastIndex]:
            pdbIds.append(p.split(':')[0])
        return pdbIds, BROWSER_URL+pdbChainIds[lastIndex]
    else:
        print response.status_code

def runCustomReport(pdbIds, fieldNames):
    query = '?pdbids=' + ','.join(pdbIds) + '&customReportColumns=' + ','.join(fieldNames)
    url = CUSTOM_REPORT_URL + query
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print "failure with url:", url
        print response.status_code

def runStandardReport(pdbIds, reportName):
    query = '?pdbids=' + ','.join(pdbIds) + '&reportName=' + reportName
    url = CUSTOM_REPORT_URL + query
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print "failure with url:", url
        print response.status_code
   

def getInfo(pdbIds, fieldName, elementName):
    xmlStr = runCustomReport(pdbIds, [fieldName])
    root = ET.fromstring(xmlStr)
    elementTexts = Set()
    for element in root.iter(elementName):
        elementTexts.add(element.text)
    return list(filter(lambda e: e != 'null', elementTexts))

def getLigandNames(pdbIds):
    return getInfo(pdbIds, 'ligandName', 'dimEntity.ligandName')

def getStructureTitles(pdbIds):
    return getInfo(pdbIds, 'structureTitle', 'dimStructure.structureTitle')

def getCitations(pdbIds):
    return getInfo(pdbIds, '', '')

def getReleaseYears(pdbIds):
    relDates = getInfo(pdbIds, 'releaseDate', 'dimStructure.releaseDate')
    dateDict = dict()
    for relDate in relDates:
        y = relDate.split('-')[0]
        dateDict[y] = dateDict.get(y, 0) + 1
    return dateDict

def getCitationYears(pdbIds):
    xmlStr = runStandardReport(pdbIds, 'Citation')
    root = ET.fromstring(xmlStr)
    dateDict = dict()
    for element in root.iter('VCitation.publicationYear'):
        dateDict[element.text] = dateDict.get(element.text, 0) + 1
    return dateDict

def getCitationTitles(pdbIds):
    xmlStr = runStandardReport(pdbIds, 'Citation')
    root = ET.fromstring(xmlStr)
    pub_titles = Set()
    for element in root.iter('VCitation.title'):
        pub_titles.add(element.text)
    return list(pub_titles)
