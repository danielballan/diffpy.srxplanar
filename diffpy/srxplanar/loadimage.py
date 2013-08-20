#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanar  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSENOTICE.txt for license information.
#
##############################################################################

import numpy as np
import fabio, fabio.openimage
import os,fnmatch, sys
from diffpy.srxplanar.srxplanarconfig import _configPropertyR

class LoadImage(object):
    '''
    provide methods to filter files and load images 
    '''
    # define configuration properties that are forwarded to self.config
    xdimension = _configPropertyR('xdimension')
    ydimension = _configPropertyR('ydimension')
    tifdirectory = _configPropertyR('tifdirectory')
    filenames = _configPropertyR('filenames')
    includepattern = _configPropertyR('includepattern')
    excludepattern = _configPropertyR('excludepattern')
    fliphorizontal = _configPropertyR('fliphorizontal')
    flipvertical = _configPropertyR('flipvertical')
    backgroundfile = _configPropertyR('backgroundfile')

    def __init__(self, p):
        self.config = p
        self.prepareCalculation()
        return

    def prepareCalculation(self):
        '''
        prepare the calculation
        '''
        if (self.backgroundfile != '') and (os.path.exists(self.backgroundfile)):
            temp = fabio.openimage.openimage(self.backgroundfile)
            self.backgroundpic = self.flipImage(temp.data)
            self.backgroundenable = True
        else:
            self.backgroundenable = False
        return
        
    def flipImage(self, pic):
        '''
        flip image if configured in config
        
        :param pic: 2d array, image array
        
        :return: 2d array, flipped image array
        '''
        if self.fliphorizontal:
            pic = pic[:,::-1]
        if self.flipvertical:
            pic = pic[::-1,:]
        return pic
    
    def loadImage(self, filename):
        '''
        load image, then subtract the background if configed in self.backgroundpic.
        
        :param filename: str, image file name
        
        :return: 2d ndarray, 2d image array (flipped)
        '''
        if os.path.exists(filename):
            filenamefull = filename
        else:
            filenamefull = os.path.normpath(self.tifdirectory+'/'+filename)
        image = fabio.openimage.openimage(filenamefull)
        image = self.flipImage(image.data)
        image[image<0] = 0
        if self.backgroundenable:
            image = image - self.backgroundpic
        return image
    
    def genFileList(self, filenames=None, opendir=None, includepattern=None, excludepattern=None):
        '''
        generate the list of file in opendir according to include/exclude pattern
        
        :param filenames: list of str, list of file name patterns, all files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files that will be loaded, 
            all files match ALL patterns in this list will be included  
        :param excludepattern: list of str, list of wildcard of files that will be blocked,
            any files match ANY patterns in this list will be blocked
        
        :return: list of str, a list of filenames (not include their full path)
        '''
        filenames = self.filenames if filenames == None else filenames
        opendir = self.tifdirectory if opendir == None else opendir
        includepattern = self.includepattern if includepattern == None else includepattern
        excludepattern = self.excludepattern if excludepattern == None else excludepattern
        
        fileset = self.genFileSet(filenames, opendir, includepattern, excludepattern)
        return sorted(list(fileset))
    
    def genFileSet(self, filenames=None, opendir=None, includepattern=None, excludepattern=None):
        '''
        generate the list of file in opendir according to include/exclude pattern
        
        :param filenames: list of str, list of file name patterns, all files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files that will be loaded, 
            all files match ALL patterns in this list will be included  
        :param excludepattern: list of str, list of wildcard of files that will be blocked,
            any files match ANY patterns in this list will be blocked
        
        :return: set of str, a list of filenames (not include their full path)
        '''
        filenames = self.filenames if filenames == None else filenames
        opendir = self.tifdirectory if opendir == None else opendir
        includepattern = self.includepattern if includepattern == None else includepattern
        excludepattern = self.excludepattern if excludepattern == None else excludepattern
        # filter the filenames according to include and exclude pattern
        filelist = os.listdir(opendir)
        fileset = set()
        for includep in includepattern:
            fileset |= set(fnmatch.filter(filelist, includep))
        for excludep in excludepattern:
            fileset -= set(fnmatch.filter(filelist, excludep))
        # filter the filenames according to filenames
        if len(filenames)>0:
            fileset1 = set()
            for filename in filenames:
                fileset1 |= set(fnmatch.filter(fileset, filename))
            fileset = fileset1
        return fileset
