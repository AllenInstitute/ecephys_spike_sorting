# -*- coding: utf-8 -*-
import numpy as np

def ParseProbeStr(probe_string):
    
    str_list = probe_string.split(',')
    prb_list = []
    for substr in str_list:
        if (substr.find(':') > 0):
            # split at colon
            subsplit = substr.split(':')
            for i in range( int(subsplit[0]), int(subsplit[1]) + 1):
                prb_list.append(str(i))
        else:
            # just append this string
            prb_list.append(substr)

    return prb_list

def ParseTcatName(tcat_name):
    
    parts_list = tcat_name.split('.')
    baseName = parts_list[0] + '.' + parts_list[1]
    return baseName

def ParseCatGTLog( logPath, run_name, gate_string, prb_list ):
    
    gfix_str = run_name + '_' + gate_string + ' Gfix'
    
    num_probe = len(prb_list)
    gfix_edits = np.zeros(num_probe, dtype='float64' )
    
    gfound = np.zeros(num_probe)
    pfound = list()             #list of strings of probes found
    nfound = 0;
    log_fullpath = logPath.replace('\\','/') + "/CatGT.log"
    
    with open(log_fullpath, 'r') as reader:
        line = reader.readline()
        while line != '' and nfound < num_probe:  # The EOF char is an empty string
            gstart = line.find( gfix_str )
            if gstart  > -1:      
                # parse this line to get probe string and corrections/sec
                line_end = len(line)
                gsub = line[gstart:line_end]
                datArr = gsub.split()       
                pfound.append(datArr[3])
                gfound[nfound] = float(datArr[5])
                nfound = nfound + 1
            line = reader.readline()   
    
    # order the returned gfix_edits matching the probe order specified 
    # in prb_list
    for i in range(0,len(prb_list)):
        gfix_edits[i] = gfound[pfound.index(prb_list[i])]
     
    return gfix_edits    



