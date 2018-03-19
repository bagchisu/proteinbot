#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""

import pdb_search as pdb

uniprotIds = 'P50225'
expMethod = pdb.ExpMethod.XRay

pdbs = pdb.search(uniprotIds, expMethod)
print(",".join(pdbs))
