#!/bin/sh
# This shell script will run the census2text2010.py to download data from census bureau site
# Example tables of interest:
#   P1: Total population
#   P12: Population break down by age and sex bins
#   P13: Median Age By Sex

# Geography levels of interest: county, tract, blockgroup

# Make a dir if it doesn't exist yet
mkdir -p data/census/census2010

for g in blockgroup tract county
# for g in tract
do
    for t in P1 P12 P13
    do

        # # Uncomment the states you want to download!

        # python census2text.py --state 'Alaska' --geography $g $t > data/census/census2010/AK_${t}_${g}.txt
        # python census2text.py --state 'Alabama' --geography $g $t > data/census/census2010/AL_${t}_${g}.txt
        # python census2text.py --state 'Arkansas' --geography $g $t > data/census/census2010/AR_${t}_${g}.txt
        # python census2text.py --state 'Arizona' --geography $g $t > data/census/census2010/AZ_${t}_${g}.txt
        # python census2text.py --state 'California' --geography $g $t > data/census/census2010/CA_${t}_${g}.txt
        # python census2text.py --state 'Colorado' --geography $g $t > data/census/census2010/CO_${t}_${g}.txt
        # python census2text.py --state 'Connecticut' --geography $g $t > data/census/census2010/CT_${t}_${g}.txt
        # python census2text.py --state 'District of Columbia' --geography $g $t > data/census/census2010/DC_${t}_${g}.txt
        # python census2text.py --state 'Delaware' --geography $g $t > data/census/census2010/DE_${t}_${g}.txt
        # python census2text.py --state 'Florida' --geography $g $t > data/census/census2010/FL_${t}_${g}.txt
        # python census2text.py --state 'Georgia' --geography $g $t > data/census/census2010/GA_${t}_${g}.txt
        # python census2text.py --state 'Hawaii' --geography $g $t > data/census/census2010/HI_${t}_${g}.txt
        # python census2text.py --state 'Iowa' --geography $g $t > data/census/census2010/IA_${t}_${g}.txt
        # python census2text.py --state 'Idaho' --geography $g $t > data/census/census2010/ID_${t}_${g}.txt
        # python census2text.py --state 'Illinois' --geography $g $t > data/census/census2010/IL_${t}_${g}.txt
        # python census2text.py --state 'Indiana' --geography $g $t > data/census/census2010/IN_${t}_${g}.txt
        # python census2text.py --state 'Kansas' --geography $g $t > data/census/census2010/KS_${t}_${g}.txt
        # python census2text.py --state 'Kentucky' --geography $g $t > data/census/census2010/KY_${t}_${g}.txt
        # python census2text.py --state 'Louisiana' --geography $g $t > data/census/census2010/LA_${t}_${g}.txt
        # python census2text.py --state 'Massachusetts' --geography $g $t > data/census/census2010/MA_${t}_${g}.txt
        # python census2text.py --state 'Maryland' --geography $g $t > data/census/census2010/MD_${t}_${g}.txt
        # python census2text.py --state 'Maine' --geography $g $t > data/census/census2010/ME_${t}_${g}.txt
        # python census2text.py --state 'Michigan' --geography $g $t > data/census/census2010/MI_${t}_${g}.txt
        # python census2text.py --state 'Minnesota' --geography $g $t > data/census/census2010/MN_${t}_${g}.txt
        # python census2text.py --state 'Missouri' --geography $g $t > data/census/census2010/MO_${t}_${g}.txt
        # python census2text.py --state 'Mississippi' --geography $g $t > data/census/census2010/MS_${t}_${g}.txt
        # python census2text.py --state 'Montana' --geography $g $t > data/census/census2010/MT_${t}_${g}.txt
        # python census2text.py --state 'North Carolina' --geography $g $t > data/census/census2010/NC_${t}_${g}.txt
        # python census2text.py --state 'North Dakota' --geography $g $t > data/census/census2010/ND_${t}_${g}.txt
        # python census2text.py --state 'Nebraska' --geography $g $t > data/census/census2010/NE_${t}_${g}.txt
        # python census2text.py --state 'New Hampshire' --geography $g $t > data/census/census2010/NH_${t}_${g}.txt
        # python census2text.py --state 'New Jersey' --geography $g $t > data/census/census2010/NJ_${t}_${g}.txt
        # python census2text.py --state 'New Mexico' --geography $g $t > data/census/census2010/NM_${t}_${g}.txt
        # python census2text.py --state 'Nevada' --geography $g $t > data/census/census2010/NV_${t}_${g}.txt
        # python census2text.py --state 'New York' --geography $g $t > data/census/census2010/NY_${t}_${g}.txt
        # python census2text.py --state 'Ohio' --geography $g $t > data/census/census2010/OH_${t}_${g}.txt
        # python census2text.py --state 'Oklahoma' --geography $g $t > data/census/census2010/OK_${t}_${g}.txt
        # python census2text.py --state 'Oregon' --geography $g $t > data/census/census2010/OR_${t}_${g}.txt
        # python census2text.py --state 'Pennsylvania' --geography $g $t > data/census/census2010/PA_${t}_${g}.txt
        # python census2text.py --state 'Rhode Island' --geography $g $t > data/census/census2010/RI_${t}_${g}.txt
        # python census2text.py --state 'South Carolina' --geography $g $t > data/census/census2010/SC_${t}_${g}.txt
        # python census2text.py --state 'South Dakota' --geography $g $t > data/census/census2010/SD_${t}_${g}.txt
        # python census2text.py --state 'Tennessee' --geography $g $t > data/census/census2010/TN_${t}_${g}.txt
        # python census2text.py --state 'Texas' --geography $g $t > data/census/census2010/TX_${t}_${g}.txt
        # python census2text.py --state 'Utah' --geography $g $t > data/census/census2010/UT_${t}_${g}.txt
        # python census2text.py --state 'Virginia' --geography $g $t > data/census/census2010/VA_${t}_${g}.txt
        # python census2text.py --state 'Vermont' --geography $g $t > data/census/census2010/VT_${t}_${g}.txt
        # python census2text.py --state 'Washington' --geography $g $t > data/census/census2010/WA_${t}_${g}.txt
        # python census2text.py --state 'Wisconsin' --geography $g $t > data/census/census2010/WI_${t}_${g}.txt
        # python census2text.py --state 'West Virginia' --geography $g $t > data/census/census2010/WV_${t}_${g}.txt
        # python census2text.py --state 'Wyoming' --geography $g $t > data/census/census2010/WY_${t}_${g}.txt

    done
done
