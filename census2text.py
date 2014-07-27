#!/usr/bin/env python
""" Convert remote U.S. Census 2000 data to local tab-separated text files.

Run with --help flag for usage instructions.
"""

from sys import stdout, stderr, argv
from os import SEEK_SET, SEEK_CUR, SEEK_END
from re import compile
from time import time
from csv import reader, DictWriter, DictReader
from os.path import basename, dirname, join
from datetime import timedelta
from optparse import OptionParser
from urlparse import urlparse, urljoin
from cStringIO import StringIO
from httplib import HTTPConnection
from urllib import urlopen
from zipfile import ZipFile
from itertools import izip

class RemoteFileObject:
    """ Implement enough of this to be useful:
        http://docs.python.org/release/2.5.2/lib/bltin-file-objects.html
        
        Pull data from a remote URL with HTTP range headers.
    """

    def __init__(self, url, verbose=False, block_size=(16 * 1024)):
        self.verbose = verbose

        # scheme://host/path;parameters?query#fragment
        (scheme, host, path, parameters, query, fragment) = urlparse(url)
        
        self.host = host
        self.rest = path + (query and ('?' + query) or '')

        self.offset = 0
        self.length = self.get_length()
        self.chunks = {}
        
        self.block_size = block_size
        self.start_time = time()

    def get_length(self):
        """
        """
        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers={'Range': '0-1'})
        length = int(conn.getresponse().getheader('content-length'))
        
        if self.verbose:
            print >> stderr, length, 'bytes in', basename(self.rest)

        return length

    def get_range(self, start, end):
        """
        """
        headers = {'Range': 'bytes=%(start)d-%(end)d' % locals()}

        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers=headers)
        return conn.getresponse().read()

    def read(self, count=None):
        """ Read /count/ bytes from the resource at the current offset.
        """
        if count is None:
            # to the end
            count = self.length - self.offset

        out = StringIO()

        while count:
            chunk_offset = self.block_size * (self.offset / self.block_size)
            
            if chunk_offset not in self.chunks:
                range = chunk_offset, min(self.length, self.offset + self.block_size) - 1
                self.chunks[chunk_offset] = StringIO(self.get_range(*range))
                
                if self.verbose:
                    loaded = float(self.block_size) * len(self.chunks) / self.length
                    expect = (time() - self.start_time) / loaded
                    remain = max(0, int(expect * (1 - loaded)))
                    print >> stderr, '%.1f%%' % min(100, 100 * loaded),
                    print >> stderr, 'of', basename(self.rest),
                    print >> stderr, 'with', timedelta(seconds=remain), 'to go'

            chunk = self.chunks[chunk_offset]
            in_chunk_offset = self.offset % self.block_size
            in_chunk_count = min(count, self.block_size - in_chunk_offset)
            
            chunk.seek(in_chunk_offset, SEEK_SET)
            out.write(chunk.read(in_chunk_count))
            
            count -= in_chunk_count
            self.offset += in_chunk_count

        out.seek(0)
        return out.read()

    def seek(self, offset, whence=SEEK_SET):
        """ Seek to the specified offset.
            /whence/ behaves as with other file-like objects:
                http://docs.python.org/lib/bltin-file-objects.html
        """
        if whence == SEEK_SET:
            self.offset = offset
        elif whence == SEEK_CUR:
            self.offset += offset
        elif whence == SEEK_END:
            self.offset = self.length + offset

    def tell(self):
        return self.offset

def file_choice(tables, verbose):
    """
    Choose the right summary file component for the given Census table
    """
    src = open(join(dirname(argv[0]), 'sf1_2010.tsv'))
    
    files = []
    
    for table in tables:
        src.seek(0)
        
        file_name, column_offset = None, 5
        
        for row in DictReader(src, dialect='excel-tab'):
            curr_file, curr_table, cell_count = row.get('File Name'), row.get('Matrix Number'), int(row.get('Cell Count'))
            
            if curr_file != file_name:
                file_name, column_offset = curr_file, 5
        
            if curr_table == table:
                if verbose:
                    print >> stderr, table, '-', row.get('Name'), 'in', row.get('Universe')
    
                files.append((table, file_name, column_offset, cell_count))
                break
            
            column_offset += cell_count
        
    return files

def file_paths(state, files):
    """
    Convert File 3 California into ca000032010.sf1
    """
    return '%sgeo2010.sf1' % states[state].lower(), dict([(f, '%s%05d2010.sf1' % (states[state].lower(), int(f))) for f in files])

def column_names(wide):
    """
    Column names for geographic header file
    """
    if wide is True:
        return ['Summary Level', 'Geographic Component', 'State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block', 'Name', 'Latitude', 'Longitude', 'Land Area', 'Water Area', 'Population', 'Housing Units']
    elif wide is False:
        return ['State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block']
    else:
        return ['Summary Level', 'Geographic Component', 'State FIPS', 'Place FIPS', 'County FIPS', 'Tract', 'Zip', 'Block', 'Name', 'Latitude', 'Longitude']

def key_names(wide):
    """
    Key names for geographic header file
    """
    if wide is True:
        return ('SUMLEV', 'GEOCOMP', 'STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK', 'NAME', 'LATITUDE', 'LONGITUDE', 'AREALAND', 'AREAWATER', 'POP100', 'HU100')
    elif wide is False:
        return ('STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK')
    else:
        return ('SUMLEV', 'GEOCOMP', 'STATE', 'PLACE', 'COUNTY', 'TRACT', 'ZCTA5', 'BLOCK', 'NAME', 'LATITUDE', 'LONGITUDE')

def get_file_in_zipfile(url, fname, verbose):
    """
    Return a file-like object for a file in a remote zipfile
    """
    f = RemoteFileObject(url, verbose, 256 * 1024)
    z = ZipFile(f)
    
    assert fname in z.namelist(), 'Filename %s not found in ZIP %s' % (fname, url)
    
    return z.open(fname)

def geo_lines(url, fname, verbose):
    """
    Get the appropriate geographic header
    """

    # make sure it is a geographic header
    assert fname[2:] == 'geo2010.sf1', 'Not a geographic header file: %s' % fname

    inp = get_file_in_zipfile(url, fname, verbose)

    # The column offsets and widths are recorded here for the 2010 geographic header
    # Offsets here are one-based to match the documentation on page 19 of the SF1 documentation
    # Note that AREAWATER is called AREAWATR in the docs; despite dropping penultimate e's being
    # all the rage in cool web 2.0 apps (e.g. Flickr), we're going to restore it.
    cols = [('LATITUDE', 337, 11), ('LONGITUDE', 348, 12),
            ('LOGRECNO', 19, 7), ('SUMLEV', 9, 3), ('GEOCOMP', 12, 2),
            ('STATE', 28, 2), ('PLACE', 46, 5), ('COUNTY', 30, 3), ('TRACT', 55, 6),
            ('BLOCK', 62, 4), ('NAME', 227, 90), ('ZCTA5', 172, 5),
            ('AREALAND', 199, 14), ('AREAWATER', 213, 14),
            ('POP100', 319, 9), ('HU100', 328, 9)]

    for line in inp:
        data = dict( [(key, line[s-1:s-1+l].strip()) for (key, s, l) in cols] )
        
        # Census Bureau represents positive latitude and longitude as +number, get rid of the plus
        # There is positive longitude in the US, check out Attu Station CDP, Alaska
        for key in ('LATITUDE', 'LONGITUDE'):
            data[key] = data[key].lstrip('+')
        
        yield data

def data_lines(url, fname, verbose):
    """
    Get all the lines in data file fname from zip file path
    """
    data = get_file_in_zipfile(url, fname, verbose)

    for row in reader(data):
        yield row

# Updated for 2010 census
summary_levels = {'state': '040', 'county': '050', 'tract': '080', 'zip': '871', 'block': '101', 'place': '160'}

states = {'Alabama': 'AL', 'Alaska': 'AK', 'American Samoa': 'AS', 'Arizona': 'AZ',
    'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
    'Louisiana': 'LA', 'Maine': 'ME', 'Marshall Islands': 'MH', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Puerto Rico': 'PR', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}

parser = OptionParser(usage="""%%prog [options] [list of table IDs]

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

Available summary levels: %s.

See also numeric summary levels in the SF1 documentation, page 107.
""".rstrip() % ', '.join(summary_levels.keys()))

parser.set_defaults(summary_level='county', table='P1', verbose=None, wide=None)

parser.add_option('-s', '--state', dest='state',
                  help='State, e.g. "Alaska", "District of Columbia." Required.',
                  type='choice', choices=states.keys())

parser.add_option('-o', '--output', dest='output',
                  help='Optional output filename, stdout if omitted.')

parser.add_option('-g', '--geography', dest='summary_level',
                  help='Geographic summary level, e.g. "state", "040". Some available summary levels are %s.' % ', '.join(summary_levels.keys()),
                  type='choice', choices=summary_levels.keys() + summary_levels.values())

parser.add_option('-c', '--county', dest='county',
                  help='County FIPS code (3 digits). e.g. --state California --county 083 would yield data for Santa Barbara County, CA',
                  type='string')

parser.add_option('-b', '--bbox', dest='bbox',
                  help='Optional geographic bounds: north west south east.',
                  type='float', nargs=4)

parser.add_option('-n', '--narrow', dest='wide',
                  help='Output fewer columns than normal',
                  action='store_false')

parser.add_option('-w', '--wide', dest='wide',
                  help='Output more columns than normal',
                  action='store_true')

parser.add_option('-q', '--quiet', dest='verbose',
                  help='Be quieter than normal',
                  action='store_false')

parser.add_option('-v', '--verbose', dest='verbose',
                  help='Be louder than normal',
                  action='store_true')

if __name__ == '__main__':

    options, tables = parser.parse_args()

    if options.state == None:
        parser.error('Please specify a state; the 2010 Census no longer provides nation-level files')
    
    if options.summary_level in summary_levels:
        options.summary_level = summary_levels[options.summary_level]

    # There may be multiple summary levels; if not, fix up
    if type(options.summary_level) is not tuple:
        options.summary_level = (options.summary_level, )
    
    # Figure out what files we need to fetch
    files = file_choice(tables, options.verbose is not False)
    
    # set up the path to the zipfile
    src_file = 'http://www2.census.gov/census_2010/04-Summary_File_1/%s/%s2010.sf1.zip' % (options.state.replace(' ', '_'), states[options.state].lower())

    if options.verbose is not False:
        print >> stderr, 'Fetching from %s' % src_file
        print >> stderr, ', '.join(options.summary_level), options.state, '-',
        print >> stderr, ', '.join( ['%s: file %s (%d @%d)' % (tbl, fn, cc, co) for (tbl, fn, co, cc) in files] )
        print >> stderr, '-' * 32
    
    file_names = set( [file_name for (tbl, file_name, co, cc) in files] )
    geo_path, data_paths = file_paths(options.state, file_names)

    # Be forgiving about the bounding box
    if options.bbox is not None:
        north = max(options.bbox[0], options.bbox[2])
        south = min(options.bbox[0], options.bbox[2])
        east = max(options.bbox[1], options.bbox[3])
        west = min(options.bbox[1], options.bbox[3])
            
    # Get the header for the geo columns
    row = column_names(options.wide)
    pat = compile(r'^([A-Z]+)(\d+)([A-Z]*)$')
    
    # Write the header for the data columns
    for (table, fn, co, cell_count) in files:
        row += ['%s%03d%s%04d' % (pat.sub(r'\1', table), int(pat.sub(r'\2', table)), pat.sub(r'\3', table), cell)
                for cell in range(1, cell_count + 1)]
    
    out = options.output and open(options.output, 'w') or stdout
    out = DictWriter(out, dialect='excel-tab', fieldnames = row)
    out.writeheader()
    
    # Get iterables for all of the files
    file_iters = {}
    
    for (tbl, file_name, co, cc) in files:
        if file_name not in file_iters:
            file_iters[file_name] = data_lines(src_file, data_paths[file_name], options.verbose)
    
    file_names = sorted(file_iters.keys())

    # get rows from geographic header
    geo_iter = geo_lines(src_file, geo_path, options.verbose)
    
    for geo in geo_iter:
        
        if geo['SUMLEV'] not in options.summary_level:
            # This is not the summary level you're looking for.
            continue

        if geo['GEOCOMP'] != '00':
            # Geographic Component "00" means the whole thing,
            # not e.g. "01" for urban or "43" for rural parts.
            continue

        if options.county != None and geo['COUNTY'] != options.county:
            # This is not the county you're looking for
            continue

        if options.bbox is not None:
            lat, lon = float(geo['LATITUDE']), float(geo['LONGITUDE'])
            
            if lat < south or north < lat or lon < west or east < lon:
                # This geography is outside the bounding box
                continue
    
        vals = [geo[key] for key in key_names(options.wide)]
        # name the columns appropriately
        row = dict(zip(column_names(options.wide), vals))
        
        # Iterate over every line in each of the necessary files
        # It is possible that there won't be an entry for some variable in some file,
        # so we can't iterate over them all at once as was done in the 2000 version of this script

        for fname in file_iters.keys():
            for line in file_iters[fname]:
                if line[4] == geo['LOGRECNO']:
                   # We found a match, grab every matrix in this file at once
                   # matrix is in the form (matrix/table name, file, offset, cell count)
                   for matrix in [i for i in files if i[1] == fname]:
                       names = ['%s%03d%s%04d' % (pat.sub(r'\1', matrix[0]), int(pat.sub(r'\2', matrix[0])), pat.sub(r'\3', matrix[0]), cell)
                                for cell in range(1, matrix[3] + 1)]
                       values = line[matrix[2]:matrix[2]+matrix[3]]
                       row.update(zip(names, values))
                   # done
                   break
        
        out.writerow(row)
        stdout.flush()
