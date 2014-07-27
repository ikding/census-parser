# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 12:04:49 2014

@author: pgao
"""

"""
Read the CSV
NOTE: Manually edited csv file twice to match FIELD NAME format

"""
import csv

datareader = csv.DictReader(open("sf1_data_field_descriptors_2010.csv"))
data = []
entry = None
current_table = ""
for line in datareader:
    new_table_number = line['TABLE NUMBER']
    if new_table_number != current_table:
        # save the old one
        if entry != None:
            data.append(entry)

        entry = {}
        current_table = new_table_number
        entry['Matrix Number'] = line['TABLE NUMBER']
        entry['File Name'] = line['SEGMENT']
        next_line = datareader.next()
        entry['Universe'] = (next_line['FIELD NAME'][9:].lstrip())

        entry['Name'] = line['FIELD NAME'][:line['FIELD NAME'].index('[')-1]
        entry['Cell Count'] = 0

    # Increment the cell count iff there's actually data, rather than this being a descriptive row
    if len(line['FIELD CODE']) > 0:
        entry['Cell Count'] += 1

# Write the tsv file
datawriter = csv.DictWriter(open("sf1_2010.tsv", "w"),
                            ['File Name', 'Matrix Number',
                            'Cell Count', 'Name', 'Universe'],
                            dialect = 'excel-tab'
)
datawriter.writeheader()
datawriter.writerows(data)
