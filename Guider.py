
#! /usr/bin/python
"""
Guider.py
Control of the guiding image acquisition and analysis

TODO:
something looks wrong with the run function.  I think it will trap us in the future.  Break it apart to separate functions.
implement PID (P term only) code

"""

__author__ = ["Courtney Johnson", "Adrian Davila"]
__copyright__ = "NA"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "NA"
__email__ = "NA"
__status__ = "Developement"

import time
import subprocess
import PyGuide
import numpy as np
from astropy.io import fits
import subprocess
from camera import *
import thread
from logger import *

class Guider(object):

    def __init__(self):
        self.ref= None  #coordinate array for reference image, starts empty
        self.refName = None #name of reference image
        self.quit = False #tells program to stop running, changed via start/stopGuiding set functions
	self.expTime = 5 #exposure time given to camera for iamges
	self.readoutOffset = 0 #um?
        self.c = CameraExpose() #
        self.l = Logger() #Logger class creates logfile of processes
        self.fakeImageDir = '/Users/jwhueh/projects/MRO/guiding_images/gcam_UT150425/' 
        self.fakeOut =  False #variable to tell class to guide on fake data already in directory
        self.currentImage = 2 #?
        self.logType = 'guider' #parameter for Logger class?
        self.thres = 30 #threshold to match coordinates, to find ref star with coordCompare
	self.tRef = False #variable can be set to True to get a new reference image taken

    def takeImage(self, imType = None, imgName = None, imExp = None, imDir = None): 
        if self.fakeOut != True:
            im = self.c.runExpose(imgName, imExp, imDir)
            self.l.logStr('Image\t%s %s %s' % (str(imgName), str(imExp), str(imDir)), self.logType)
            #if im == True:
            #    return
            #else:
            #    raise Exception
        else:
            return 3

    #uses PyGuide function findStars on iamge to get coordinates of all stars in field, stores 
    #coordinates in an array
    def analyze(self,im): 
        output=[]
        hdulist = fits.open(im)
        data = hdulist[0].data

        ccd = PyGuide.CCDInfo(200,21.3,1.6) #Since we're using it on one CCD, these should be constants
        ctr,imstat = PyGuide.findStars(data,None,None,ccd,1,False)[0:2] #need to choose mask here

        size= len(ctr)
        xcoord = ['XCoord']
        ycoord = ['YCoord']
        names = ['StarName']

        for x in range(size):
            xcoord = ctr[x].xyCtr[0]
            ycoord = ctr[x].xyCtr[1]
            name = x
            star_out = [name, xcoord, ycoord]
            self.l.logStr('StarPos\t'+str(star_out), self.logType)
            output.append(star_out)
        return output

    #Takes the coordinate array from analyze and finds the difference between these coordinates
    #and those for the reference image, to get x and y offsets to give to the telescope
		#do we need to do anything here to convert this to RA and dec?
    def getOffset(self, imCoords):
        self.l.logStr('OffsetInput\t'+str(self.ref)+'\t'+str(imCoords), self.logType)
        x = self.ref[1]
        y = self.ref[2]
        xx = imCoords[1]
        yy = imCoords[2]
        xoff = xx - x
        yoff = yy - y
        if np.abs(xoff) > float(self.thres) and np.abs(yoff) > float(self.thres):
            self.quit = True
            print 'stopped guiding becuase offset is too large'
            return
        return xoff, yoff

   
#goes through coordinate list for current image and finds new coordinates of guide star (chosen in ref image)
#by comparing coordinates and matching within some given threshole
    def coordCompare(self, c0, c1, thres): 
        if np.abs(c0[1] - c1[1]) > float(thres) and np.abs(c0[2] - c1[2]) > float(thres):
            self.quit = True
            print 'too far off'
        else:
            return True

    def test(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        self.takeImage('image', self.refName,self.expTime, None)
        print self.refName
	print self.analyze(self.refName)
	return

#takes a new reference image. This the coordinate of objects in this image will serve as the target for guiding
#this function creates a name for the reference image and saves it, takes the image, analyzes it, and saves the
#coordinate list for that image. It then sets the guide star to be the star at the 0th spot in the coordinate array
    def takeRef(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        if self.fakeOut == True: #if has been told to guide on fake data that already exists in the directory, goes into this loop
            self.refName = self.fakeImageDir+'g' + str(self.currentImage).zfill(4)+'.fits'
            self.currentImage = self.currentImage +1
            self.l.logStr('FakeImage\t%s' % str(self.refName), self.logType)
        self.takeImage('image', self.refName,self.expTime)
        refOptions = self.analyze(self.refName)
        # reference coords are (singluar selection, not robust).  Don't assume the first element is the best.
        self.ref = refOptions[0]
        return

#does literally everything -- come up with a good explanation for this, but first we need to break it up
    def run(self): 
	if self.tRef == True or self.ref == None: #if you want a new ref image, this will be True
	    self.takeRef()	
        while (self.quit != True):
            self.l.logStr('GuidingStarted', self.logType)
            imName = time.strftime("%Y%m%dT%H%M%S.fits")    #take image
            self.takeImage('image',imName,self.expTime) 
            time.sleep(float(self.expTime) + self.readoutOffset) #sleep while reading out 
            if self.fakeOut: #fakeout?
                imName = self.fakeImageDir+'g' + str(self.currentImage).zfill(4)+'.fits'
                self.currentImage = self.currentImage +1
                self.l.logStr('FakeImage\t%s' % str(imName), self.logType)
            coords = self.analyze(imName)
            for star in coords: #find the new coordinates of the reference star by matching coordinates within
                if self.coordCompare(self.ref, star, 30): #some passed threshold
                    foundStar = star
                    break
	    try:
            	self.l.logStr('ReferenceStar\t%s' % str(foundStar), self.logType)
	    except:
		print "no found star"
            offsetx, offsety = self.getOffset(foundStar)
            print 'dRA, dDEC: %.2f, %.2f' % (float(offsetx), float(offsety))
            self.l.logStr('Offset\t'+str([offsetx, offsety]), self.logType)
        self.l.logStr('GuidingStopped', self.logType)
	return

    def startGuiding(self):
        self.quit = True
        thread.start_new_thread(self.run,())
	return
    
    def stopGuiding(self):
        self.quit = False
	return	

    def updateExpTime(self, time):
	self.expTime = time
	return

    def setTakeRef(self):
	self.takeRef = True
	return

#write in dummy functions for rotation and focus
#(should be same concept as taking an exposure ... ??)
#equated status functions ... ??
   # def moveGuiderFocus(self, m):
#       ser.write('more %\r\n' % str(m))
#
#       while self.inPosition != True:
#               if self.statusGuiderFocus() == float(m):
#                       self.inPosition = True
#               time.sleep(,2)
 #   return

#    def statusGuiderFocus(self):
        #????
        #????
 #   return


if __name__ == "__main__": #the if is so that the program only runs when the command is
    g = Guider()           #python guider.py, not when the program is imported
    #g.startGuiding()
    g.test()
    #g.test()


