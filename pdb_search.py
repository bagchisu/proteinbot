#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""

import requests

URL = 'https://www.rcsb.org/pdb/rest/search/'

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

class ExpMethod:
    XRay = 'X-RAY'
    SolutionNMR = 'SOLUTION NMR'
    ElectronMicroscopy = 'ELECTRON MICROSCOPY'

def search(uniprotIds, expMethod=None):
    
    if (expMethod is None):
        response = requests.post(URL, data=QUERY.format(uniprotIds=uniprotIds), headers=HEADERS)
    else:
        response = requests.post(URL, data=COMP_QUERY.format(uniprotIds=uniprotIds, expMethod=expMethod), headers=HEADERS)
    
    if response.status_code == 200:
        pdb_ids = response.text.split()
        return pdb_ids
    else:
        print response.status_code
