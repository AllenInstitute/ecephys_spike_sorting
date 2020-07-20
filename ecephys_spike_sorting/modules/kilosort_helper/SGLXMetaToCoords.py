# -*- coding: utf-8 -*-
"""
Requires python 3

The main() function at the bottom of this file can run from an
interpreter, or, the helper functions can be imported into a
new module or Jupyter notebook (an example is included).

Standalone program to generate a coordinate file from a SpikeGLX
metadata file for 3A, NP1.0, or NP2 single shank or multishank probes.

The output is set by the outType parameter:
                  0 for text coordinate file; 
                  1 for Kilosort or Kilosort2 channel map file;
                  2 for strings to paste into JRClust .prm file 
                


@author: Jennifer Colonell, Janelia Research Campus

"""

import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import Tk
from tkinter import filedialog


# Parse ini file returning a dictionary whose keys are the metadata
# left-hand-side-tags, and values are string versions of the right-hand-side
# metadata values. We remove any leading '~' characters in the tags to match
# the MATLAB version of readMeta.
#
# The string values are converted to numbers using the "int" and "float"
# fucntions. Note that python 3 has no size limit for integers.
#
def readMeta(metaPath):
    metaDict = {}
    if metaPath.exists():
        # print("meta file present")
        with metaPath.open() as f:
            mdatList = f.read().splitlines()
            # convert the list entries into key value pairs
            for m in mdatList:
                csList = m.split(sep='=')
                if csList[0][0] == '~':
                    currKey = csList[0][1:len(csList[0])]
                else:
                    currKey = csList[0]
                metaDict.update({currKey: csList[1]})
    else:
        print("no meta file")
    return(metaDict)
    
# Return array of original channel IDs. As an example, suppose we want the
# imec gain for the ith channel stored in the binary data. A gain array
# can be obtained using ChanGainsIM(), but we need an original channel
# index to do the lookup. Because you can selectively save channels, the
# ith channel in the file isn't necessarily the ith acquired channel.
# Use this function to convert from ith stored to original index.
# Note that the SpikeGLX channels are 0 based.
#
def OriginalChans(meta):
    if meta['snsSaveChanSubset'] == 'all':
        # output = int32, 0 to nSavedChans - 1
        chans = np.arange(0, int(meta['nSavedChans']))
    else:
        # parse the snsSaveChanSubset string
        # split at commas
        chStrList = meta['snsSaveChanSubset'].split(sep=',')
        chans = np.arange(0, 0)  # creates an empty array of int32
        for sL in chStrList:
            currList = sL.split(sep=':')
            if len(currList) > 1:
                # each set of contiguous channels specified by
                # chan1:chan2 inclusive
                newChans = np.arange(int(currList[0]), int(currList[1])+1)
            else:
                newChans = np.arange(int(currList[0]), int(currList[0])+1)
            chans = np.append(chans, newChans)
    return(chans)

    
# Return counts of each imec channel type that composes the timepoints
# stored in the binary files.
#
def ChannelCountsIM(meta):
    chanCountList = meta['snsApLfSy'].split(sep=',')
    AP = int(chanCountList[0])
    LF = int(chanCountList[1])
    SY = int(chanCountList[2])
    return(AP, LF, SY)


# Read shank map for any probe type and return list
# of channels that are disabled. This will include the 
# reference channels
#
# Note that first entry in the shankMap is the header
def findDisabled(meta):     
    # read in the shank map   
    shankMap = meta['snsShankMap'].split(sep=')')

    # There's an entry in the shank map for each saved channel.
    # Get the array of saved channels:
    chan = OriginalChans(meta)
    # Find out how many are AP chans
    [AP, LF, SY] = ChannelCountsIM(meta)
    exChan = list();
    for i in range(0,AP):
        # get enabled flag from this entry, skipping first header entry
        currList = shankMap[i+1].split(':')
        if currList[3] == '0':          
            exChan.append(chan[i])
    
    return(exChan)


# Return shank and electrode number for NP1.0 or 3A
# Index into these with original (acquired) channel IDs.
#
def NP10_ElecInd(meta):
    # Works for 3A and 3B data
    # First number in each imro entry = channel index
    # Second number = bank index
    # The 3B imro table has an additional field for the
    # high pass filter enabled/disabled, but this does
    # not affect Python parsing by splitting the fields
    # first entry in imroTbl is the header
    imroList = meta['imroTbl'].split(sep=')')
    nChan = len(imroList) - 2   # first entry is header; last is trailing ')'
    chan = np.zeros(nChan, dtype='int')
    bank = np.zeros(nChan, dtype='int')
    connected = np.ones(nChan, dtype='int')

    for i in range(0, nChan):
        currList = imroList[i+1]
        currList = currList[1:len(currList)]
        currList = currList.split(' ')
        chan[i] = int(currList[0])
        bank[i] = int(currList[1])

    elecInd = bank*384 + chan

    exChan = findDisabled(meta)

    for i in range(0, len(exChan)):
        ind = np.argwhere(chan == exChan[i])
        if ind.size > 0:
            connected[ind] = 0

    return elecInd, connected


# Return x y coords for electrode index for NP1.0 or 3A
#
def XYCoord10(meta, elecInd, showPlot):
    nElec = 960;    # per shank; pattern repeats for the four shanks
    vSep = 20;      # in um
    hSep = 32;

    elecPos = np.zeros((nElec,2), dtype='float')
    
    # fill in x values
    ind = np.arange(0, nElec, step=4, dtype='int')
    elecPos[ind,0] = hSep/2             # sites 0,4,8...
    ind = np.arange(1, nElec, step=4, dtype='int')
    elecPos[ind,0] =  (3/2)*hSep        # sites 1,5,9...
    ind = np.arange(2, nElec, step=4, dtype='int')
    elecPos[ind,0] = 0                  # sites 2,6,10...
    ind = np.arange(3, nElec, step=4, dtype='int')
    elecPos[ind,0] =  hSep;             # sites 3,7,11...
    elecPos[:,0] = elecPos[:,0] + 11;       #x offset on the shank
    
    # fill in y values        
    viHalf = np.arange(0,(nElec/2), dtype='int')         # row numbers
    ind0 = np.arange(0, nElec, step=2, dtype ='int')
    elecPos[ind0,1] = viHalf * vSep       # sites 0,2,4...
    ind1 = np.arange(1, nElec, step=2, dtype ='int')
    elecPos[ind1,1] = elecPos[ind0,1];    # sites 1,3,5...

    xCoord = elecPos[elecInd, 0]
    yCoord = elecPos[elecInd, 1]

    if showPlot:
        # single shank probe. Plot only lowest selected electrode
        
        fig = plt.figure(figsize=(2,12))
        
        # plot all positions   
        marker_style = dict(c='w', edgecolor = 'k', linestyle='None', marker='s', s=20)                 
        plt.scatter(elecPos[:,0], elecPos[:,1], **marker_style)

        # plot selected position
        marker_style = dict(c='b', edgecolor='b', linestyle='None', marker='s', s=15)
        plt.scatter(xCoord, yCoord, **marker_style)

        plt.show()

    return(xCoord, yCoord)


# Return x y coords for electrode index for NP1.0 or 3A
#
def XYCoordUHD(meta, elecInd, showPlot):
    nElec = 384;    # per shank; pattern repeats for the four shanks
    vSep = 6;      # in um
    hSep = 6;

    elecPos = np.zeros((nElec,2), dtype='float')
    
    # fill in x and y values
    for i in range(0, 8):
        ind = np.arange(i, nElec, step=8, dtype='int')
        elecPos[ind,0] = i*hSep             # i = 0 for site 0,8,16..., i = 1 for sites 1,9,17...
        rowind = ind/8;
        rowind = rowind.astype('int')
        elecPos[ind,1] = rowind*vSep
    

    xCoord = elecPos[elecInd, 0]
    yCoord = elecPos[elecInd, 1]

    if showPlot:
        # single shank probe. Plot only lowest selected electrode
        
        fig = plt.figure(figsize=(2,12))
        
        # plot all positions   
        marker_style = dict(c='w', edgecolor = 'k', linestyle='None', marker='s', s=20)                 
        plt.scatter(elecPos[:,0], elecPos[:,1], **marker_style)

        # plot selected position
        marker_style = dict(c='b', edgecolor='b', linestyle='None', marker='s', s=15)
        plt.scatter(xCoord, yCoord, **marker_style)

        plt.show()

    return(xCoord, yCoord)

# Return shank and electrode number for NP2.0 probes
# Index into these with original (acquired) channel IDs.
#
def NP20_ElecInd(meta):

    pType = meta['imDatPrb_type']
    imroList = meta['imroTbl'].split(sep=')')
    nChan = len(imroList) - 2     # first entry is header; last is trailing ')'
    chan = np.zeros(nChan, dtype='int')
    elecInd = np.zeros(nChan, dtype='int')
    bankMask = np.zeros(nChan, dtype='int')
    shankInd = np.zeros(nChan, dtype='int')
    connected = np.ones(nChan, dtype='int')

    
    if pType == '21':
        # Single shank probe
        # imro table entries: (channel, bankMask, refType, electrode #)

        for i in range(0,nChan):
            currList = imroList[i+1]
            currList = currList[1:len(currList)]    # trim leading '('
            currList = currList.split(' ')
            chan[i] = int(currList[0])
            bankMask[i] = int(currList[1])
            elecInd[i] = int(currList[3])
            
      
    else:
        # 4 shank probe
        # imro table entries: (channel, shank, bank, refType, electrode #)
        for i in range(0,nChan):
            currList = imroList[i+1]
            currList = currList[1:len(currList)]    # trim leading '('
            currList = currList.split(' ')
            chan[i] = int(currList[0])
            shankInd[i] = int(currList[1])
            bankMask = int(currList[2])
            elecInd[i] = int(currList[4])
        
    exChan = findDisabled(meta)
    
    for i in range(0,len(exChan)): 
        ind = np.argwhere(chan == exChan[i])
        if ind.size > 0:
            connected[ind] = 0  
  
    return (elecInd, shankInd, bankMask, connected)

# Return x y coords for electrode index for 2.0 probes
#    
def XYCoord20(meta, elecInd, bankMask, shankInd, showPlot):  

    pType = meta['imDatPrb_type']

    nElec = 1280   # per shank; pattern repeats for the four shanks
    vSep = 15      # in um
    hSep = 32

    elecPos = np.zeros((nElec,2), dtype='float')  

    # fill in x values
    ind0 = np.arange(0, nElec, step=2, dtype='int')
    elecPos[ind0, 0] = 0         # sites 0,2,4...
    ind1 = np.arange(1, nElec, step=2, dtype='int')
    elecPos[ind1, 0] = hSep      # sites 1,3,5...

    # fill in y values        
    viHalf = np.arange(0,(nElec/2), dtype='int')         # row numbers
    elecPos[ind0, 1] = viHalf * vSep       # sites 0,2,4...
    elecPos[ind1, 1] = elecPos[ind0, 1]    # sites 1,3,5...
    
   
    xCoord = elecPos[elecInd,0]
    yCoord = elecPos[elecInd,1]
    
    if showPlot:
        if pType == '21':
            # single shank probe. Plot only lowest selected electrode
            fig = plt.figure(figsize=(2,12))
        
            # plot all positions   
            marker_style = dict(c='w', edgecolor = 'k', linestyle='None', marker='s', s=20)                 
            plt.scatter(elecPos[:,0], elecPos[:,1], **marker_style)
        
            # plot selected positions
            marker_style = dict(c='b', edgecolor = 'b', linestyle='None', marker='s', s=15) 
            plt.scatter(xCoord,yCoord, **marker_style)
        
            plt.show()
            
        else:
            # four shank probe, no multiple connections   
            fig = plt.figure(figsize=(2,12))
        
            shankSep = 250
            
            # loop over shanks
            for sI in range(0,4):
                
                # plot all positions   
                marker_style = dict(c='w', edgecolor = 'k', linestyle='None', marker='s', s=20)                 
                plt.scatter(shankSep*sI + elecPos[:,0], elecPos[:,1], **marker_style)
        
                # plot selected positions
                currInd = np.argwhere(shankInd == sI)
                marker_style = dict(c='b', edgecolor = 'b', linestyle='None', marker='s', s=15) 
                plt.scatter(shankSep*sI + xCoord[currInd], yCoord[currInd], **marker_style)
    
            plt.show()
   
    return(xCoord, yCoord)


def CoordsToText(chans, xCoord, yCoord, connected, shankInd, shankSep, baseName, savePath, buildPath ):

    if buildPath:
        newName = baseName + '_siteCoords.txt'
        saveFullPath = Path(savePath / newName)
    else:
        saveFullPath = savePath

    # Note that the channel index written is the index of that channel in the saved file

    with open(saveFullPath, 'w') as outFile:
        for i in range(0,chans.size):
            currX = shankInd[i]*shankSep + xCoord[i]
            currLine = '{:d}\t{: .1f}\t{: .1f}\t{:d}\n'.format(i, currX, yCoord[i], shankInd[i])
            outFile.write(currLine)
            
def CoordsToJRCString(chans, xCoord, yCoord, connected, shankInd, shankSep, baseName, savePath, buildPath ):
    
    if buildPath:
        newName = baseName +'_forJRCprm.txt'
        saveFullPath = Path(savePath / newName)
    else:
        saveFullPath = savePath
    
    # siteMap, equivalent of chanMap in KS, is the order of channels in the saved file
    # rather than original channel indicies.
    nChan = chans.size
    siteMap = np.arange(0,nChan, dtype = 'int')
    siteMap = siteMap + 1   # convert to 1-based for MATLAB
    
    shankInd = shankInd + 1 # conver to 1-based for MATLAB
 
    shankStr = 'shankMap = ['
    coordStr = 'siteLoc = ['
    siteMapStr = 'siteMap = ['
    
    xCoord = shankInd*shankSep + xCoord
    
    for i in range(0,chans.size-1):
        shankStr = shankStr + '{:d},'.format(shankInd[i])   # convert to 1-based for MATLAB
        coordStr = coordStr + '{:.1f},{:.1f};'.format(xCoord[i], yCoord[i])
        siteMapStr = siteMapStr + '{:d},'.format(siteMap[i])    # convert to 1-based for MATLAB
    
    # final entries
    shankStr = shankStr + '{:d}];\n'.format(shankInd[nChan-1])
    coordStr = coordStr + '{:.1f},{:.1f}];\n'.format(xCoord[nChan-1], yCoord[nChan-1])
    siteMapStr = siteMapStr + '{:d}];\n'.format(siteMap[nChan-1])
    
    with open(saveFullPath, 'w') as outFile:
        outFile.write(shankStr) 
        outFile.write(coordStr)
        outFile.write(siteMapStr)


def CoordsToKSChanMap(chans, xCoord, yCoord, connected, shankInd, shankSep, baseName, savePath, buildPath ): 
    
    if buildPath:
        newName = baseName +'_kilosortChanMap.mat'
        saveFullPath = Path(savePath / newName)
    else:
        saveFullPath = savePath
    
    nChan = chans.size
    # channel map is the order of channels in the file, rather than the 
    # original indicies of the channels
    chanMap0ind = np.arange(0,nChan,dtype='float64')
    chanMap0ind = chanMap0ind.reshape((nChan,1))
    chanMap = chanMap0ind + 1
    
    connected = (connected==1)
    connected = connected.reshape((nChan,1))
    
    xCoord = shankInd*shankSep + xCoord
    xCoord = xCoord.reshape((nChan,1))
    yCoord = yCoord.reshape((nChan,1))
    
    kcoords = shankInd + 1
    kcoords = kcoords.reshape((nChan,1))
    kcoords = kcoords.astype('float64')
    
    name = baseName
    
    mdict = {
            'chanMap':chanMap,
            'chanMap0ind':chanMap0ind,
            'connected':connected,
            'name':name,
            'xcoords':xCoord,
            'ycoords':yCoord,
            'kcoords':kcoords,
            }
    scipy.io.savemat(saveFullPath, mdict)

# Given a path to a SpikeGLX metadata file, write out coordinates
# in formats for analysis software to consume
# Input params:
#   metaFullPath: full path, including the file name
#   outType:  format for the output
#   badChan:  channels other than reference channels to exclude
#   destFullPath: 
    
def MetaToCoords(metaFullPath, outType, badChan= np.zeros((0), dtype = 'int'), destFullPath = '', showPlot=False):
    
    # shank separation for multishank probe
    shankSep = 250
    
    # Read in metadata; returns a dictionary with string for values
    meta = readMeta(metaFullPath)
    
    if 'imDatPrb_type' in meta:
        pType = int(meta['imDatPrb_type'])
    else:
        pType = 0    #3A probe
        
    print(pType)
    
    if pType <= 1 or pType == 1100:  
        # Neuropixels 1.0 or 3A probe
        
        # Get indices of electrodes
        [elecInd, connected] = NP10_ElecInd(meta)
             
        # Get saved channels
        chans = OriginalChans(meta)     #inludes SY channel
        [AP,LF,SY] = ChannelCountsIM(meta)    
        chans = chans[0:AP]    

        # Trim elecInd, connected, and shankind to include only saved channels
        elecInd = elecInd[chans]
        shankInd = np.zeros(elecInd.size, dtype='int')
        connected = connected[chans]

        # Channels identified as noisy by kilosort helper indexed
        # according to position in the file
        # since these can include the SYNC channel, remove any from
        # list that are outside the range of AP channels
        badChan = badChan[badChan < AP]
        connected[badChan] = 0

        # Get XY coords for saved channels
        if pType <= 1:
            [xCoord, yCoord] = XYCoord10(meta, elecInd, showPlot)
        else:
            [xCoord, yCoord] = XYCoordUHD(meta, elecInd, showPlot)

    else:
        # Neuropixels type 21 (single shank) or 24 (four shank)
    
        # Get indices of all electrodes from the imro table
        [elecInd, shankInd, bankMask, connected] = NP20_ElecInd(meta)

        # Get saved channels
        chans = OriginalChans(meta)     # includes SY channel
        [AP, LF, SY] = ChannelCountsIM(meta)  
        chans = chans[0:AP]

        # Trim elecInd, connected, and shankind to include only saved channels
        elecInd = elecInd[chans]
        connected = connected[chans]
        shankInd = shankInd[chans]
        
        # Channels identified as noisy by kilosort helper indexed
        # according to position in the file
        # since these can include the SYNC channel, remove any from
        # list that are outside the range of AP channels
        badChan = badChan[badChan < AP]
        connected[badChan] = 0

        # Get XY coords for saved channels and plot
        [xCoord, yCoord] = XYCoord20(meta, elecInd, bankMask, shankInd, showPlot)

    baseName = metaFullPath.stem
    # write output as text
    if len(destFullPath) == 0:
        savePath = metaFullPath.parent
        buildPath = True
    else:
        buildPath = False
        savePath = destFullPath
    outputSwitch = {
            0: CoordsToText,
            1: CoordsToKSChanMap,
            2: CoordsToJRCString,
    }
    
    writeFunc = outputSwitch.get(outType)
    writeFunc(chans, xCoord, yCoord, connected, shankInd, shankSep, baseName, savePath, buildPath )
    
# Sample calling program to get a metadata file from the user,
# output a file set by outType
#
def main():
    
    outType = 1
    
    # Get file from user
    root = Tk()         # create the Tkinter widget
    root.withdraw()     # hide the Tkinter root window

    # Windows specific; forces the window to appear in front
    root.attributes("-topmost", True)

    metaFullPath = Path(filedialog.askopenfilename(title="Select meta file"))
    root.destroy()      # destroy the Tkinter widget
   
    MetaToCoords( metaFullPath=metaFullPath, outType=outType, showPlot=True  )

        

if __name__ == "__main__":
    main()