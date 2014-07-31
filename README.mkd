census-tools
============

These tools help make it easy to extract data from the online zip file of the
2000 and 2010 U.S. Census without having to download them first. You can choose from a
number of different summary levels like state, county, tract, and block, filter
by geographic bounds, select the specific topics you're interested in, and
convert everything to simple tables or GeoJSON data.

census2text2000.py
------------------

Usage: census2text.py [options] [list of table IDs]  
Help: census2text.py --help

Convert remote U.S. Census 2000 data to local tab-separated text files.

Examples:

Housing basics for counties in Rhode Island.

    census2text.py --state 'Rhode Island' H1 H3 H4
    
Age breakdowns for census tracts around Oakland, CA.

    census2text.py --state California --bbox 37.86 -122.35 37.70 -122.10 --geography tract P12
    
Family type and employment state for counties around New England.

    census2text.py --file SF3 --bbox 47.7 -80.7 38.4 -66.4 P44

Complete documentation of Summary File data is dense but helpful:

* http://www.census.gov/prod/cen2000/doc/sf1.pdf

See Chapter 7, page 228 for explanation of column names in output.

Other summary files have similar docs:

* http://www.census.gov/prod/cen2000/doc/sf3.pdf

Available summary files: SF1, SF3.

Available table IDs for each summary file:

* http://census-tools.teczno.com/SF1-p078-82-subject-locator.pdf
* http://census-tools.teczno.com/SF3-p062-84-subject-locator.pdf

Available summary levels: county, state, block, tract.

See also numeric summary levels in:

* http://census-tools.teczno.com/SF1-p083-84-sequence-state.pdf
* http://census-tools.teczno.com/SF1-p087-88-sequence-national.pdf

census2text2010.py
------------------

Usage: census2text2010.py [options] [list of table IDs]

Convert remote U.S. Census 2010 data to local tab-separated text files.

Examples:

    Housing basics for counties in Rhode Island
    census2text.py --state 'Rhode Island' H1 H3 H4
    
    Age breakdowns for census tracts around Oakland, CA
    census2text.py --state California --bbox 37.86 -122.35 37.70 -122.10 --geography tract P12
    
Complete documentation of Summary File data is dense but helpful:
  http://www.census.gov/prod/cen2010/doc/sf1.pdf

Column descriptions are start on page 183.

Available summary files: SF1.

Available summary levels: zip, county, state, place, tract, block.

See also numeric summary levels in the SF1 documentation, page 107.

text2geojson.py
--------------

Accepts text format from census2text.py, and converts it to useful GeoJSON (http://geojson.org).

test.py
-------

Runs census2text2010.py and compares its output to the Census API for all variables aggregated to Knox County, Tennessee.
