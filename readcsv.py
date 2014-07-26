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
datareader = csv.DictReader(open("C:/Users/pgao/Documents/DATA_FIELD_DESCRIPTORS.csv"))
data = []
entry = {}
current_table = ""
for line in datareader:
    new_table_number = line['TABLE NUMBER']
    if new_table_number != current_table:
        entry = {}
        current_table = new_table_number
        entry['Matrix Number'] = line['TABLE NUMBER']
        entry['File Name'] = line['SEGMENT']
        next_line = datareader.next()
        entry['Universe'] = (next_line['FIELD NAME'][9:].lstrip())
        try:
            entry['Name'] = line['FIELD NAME'][:line['FIELD NAME'].index('[')-1]
            entry['Cell Count'] = line['FIELD NAME'][line['FIELD NAME'].index('[')+1]
        except ValueError: 
            print line
        data.append(entry)

#Write the tsv file
datawriter = csv.DictWriter(open("C:/Users/pgao/Documents/SF1.tsv", "w"),
                            ['File Name', 'Matrix Number',
                            'Cell Count', 'Name', 'Universe'],
                            delimiter = '\t',
                            lineterminator='\n')
datawriter.writeheader()
datawriter.writerows(data)