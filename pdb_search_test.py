#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""

import argparse
import webbrowser
import pdb_search as pdb

parser = argparse.ArgumentParser(description='Get protein structure info from PDB given UniProt accession numbers.')
parser.add_argument('uniprotIds', nargs='+', help="List of UniProt accession numbers")
group = parser.add_mutually_exclusive_group()
group.add_argument('-x', '--xray', action="store_true", default=False, help="X-Ray crystallography method")
group.add_argument('-n', '--nmr', action="store_true", default=False, help="Solution NMR method")
group.add_argument('-e', '--em', action="store_true", default=False, help="Electon microscopy method")
args = parser.parse_args()

uniprotIds = ",".join(args.uniprotIds) #'P50225'
expMethod = None
if args.xray:
    expMethod = pdb.ExpMethod.XRay
if args.nmr:
    expMethod = pdb.ExpMethod.SolutionNMR
if args.em:
    expMethod = pdb.ExpMethod.ElectronMicroscopy

for u in args.uniprotIds:
    print u, "-", pdb.getUniProtName(u)

if expMethod != None:
    print "Using method:", expMethod
else:
    print "Using any method"
 
pdbs, rcsb_url = pdb.search(uniprotIds, expMethod)

if len(pdbs) == 0:
    print "No structures were found in PDB"
    exit()

print(",".join(pdbs))

ligands = pdb.getLigandNames(pdbs)
print "\nLigands: ", ligands

structureTitles = pdb.getStructureTitles(pdbs)
print "\nStructure titles:"
print "\n".join(structureTitles)

relYears = pdb.getReleaseYears(pdbs)
print "\nRelease years:"
for y in sorted(relYears):
    print y, relYears[y]

citationYears = pdb.getCitationYears(pdbs)
print "\nCitation years:"
for y in sorted(citationYears):
    print y, citationYears[y]

citationTitles = pdb.getCitationTitles(pdbs)
print "Citation titles:"
print "\n".join(citationTitles[:3])

print "Opening", rcsb_url
webbrowser.open(rcsb_url)