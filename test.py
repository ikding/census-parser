#!/usr/bin/python

"""
Test census2text2010.py by pulling down data for Knox County, TN and cross checking with API results
usage: test.py

Assumes that census2text2010 can be found in the current working directory and that a census API key is in the CENSUS_API_KEY environment variable.
"""

from os import environ
import json
from urllib2 import urlopen
import re
from sys import argv
from csv import DictReader
import pickle
from time import sleep
import os
import csv

state = 'Tennessee'
stfips = '47'
county = '093' # Knox county

# get all variables
vars = json.load(urlopen('http://api.census.gov/data/2010/sf1/variables.json'))

# get all matrices
varNames = vars['variables'].keys()
varNames.remove('SUBMDCC') # these variable crashes the Census servers for some reason
varNames.remove('P0240006')
matrices = []
for v in varNames:
    mo = re.match('([A-Z]+)([0-9]{3})([A-Z]?)', v)
    if mo != None:
        mx = mo.group(1) + str(int(mo.group(2))) + mo.group(3)
        if mx not in matrices:
            matrices.append(mx)


try:
    data = pickle.load(open('apidat.pickle'))
    print "Using saved census data"
except:
    # get data from the census bureau API
    data = dict()
    for i in range(0, len(varNames), 50):
        varSubset = varNames[i:i+50]
        url = 'http://api.census.gov/data/2010/sf1?key={key}&get={get}&for=county:{county}&in=state:{stfips}'\
                                    .format(key=environ['CENSUS_API_KEY'], stfips=stfips, county=county, get=','.join(varSubset))
        rawData = json.load(urlopen(url))

        data.update(dict(zip(rawData[0], rawData[1])))
        print 'Got %s columns' % (i + 50)
        sleep(0.5)

    pickle.dump(data, open('apidat.pickle', 'w'))

# get Knox County data through the raw files
cmd = './census2text2010.py --state {state} --county {county} --geography county {matrices}'\
                   .format(state=state, county=county, matrices=' '.join(matrices))
print cmd
raw = os.popen(cmd)

inp = csv.DictReader(raw, dialect='excel-tab')

sf1data = inp.next()

mismatches = 0
notInApi = 0

for key in sf1data.keys():
    try:
        # The first condition matches most things, but misses e.g. '2.5' == '2.50'
        # The second condition would crash on None and anything else that couldn't be coerced to a float
        # (e.g. names) but won't get hit for those (we hope).
        if sf1data[key] != data[key] and abs(float(sf1data[key]) - float(data[key])) > 0.0000001:
            print 'Mismatch between API and raw data for var %s: raw data %s, API %s' % (key, sf1data[key], data[key])
            mismatches += 1
    except KeyError:
        print '%s not in API' % key
        notInApi += 1

print '%s mismatches and %s columns not found in API' % (mismatches, notInApi)
print 'Total columns in raw data %s, total columns in API %s' % (len(sf1data.keys()), len(data.keys()))
