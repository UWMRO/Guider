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
        self.ref= None
        self.refName = None
        self.quit = False
	self.expTime = .5
	self.readoutOffset = 0
        self.c = CameraExpose()
        self.l = Logger()
        self.fakeImageDir = '/Users/jwhueh/projects/MRO/guiding_images/gcam_UT150425/'
        self.fakeOut = True
        self.currentImage = 2
        self.logType = 'guider'
        self.thres = 30
	self.takeRef = False

    def takeImage(self, imType = None, imgName = None, imExp = None, imDir = None):
        if self.fakeOut != True:
            im = self.c.expose(imgName, imExp, imDir)
            self.l.logStr('Image\t%s %s %s' % (str(imgName), str(imExp), str(imDir)), self.logType)
            if im == True:
                return
            else:
                raise Exception
        else:
            return 3

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

    def takeRef(self)
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        if self.fakeOut == True:
            self.refName = self.fakeImageDir+'g' + str(self.currentImage).zfill(4)+'.fits'
            self.currentImage = self.currentImage +1
            self.l.logStr('FakeImage\t%s' % str(self.refName), self.logType)
        self.takeImage('image', self.refName,self.expTime)
        refOptions = self.analyze(self.refName)
        # reference coords are (singluar selection, not robust).  Don't assume the first element is the best.
        self.ref = refOptions[0]


    return


    def run(self):
	if self.takeRef == True or self.ref == None: #if you want a new ref image, this will be True
	    self.takeRef(self)	
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
            self.l.logStr('ReferenceStar\t%s' % str(foundStar), self.logType)
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
    g.run()
    #g.test()


