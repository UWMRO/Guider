#! /usr/bin/python
"""
Guider.py
Control of the guiding image acquisition and analysis
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
import pyfits

class Guider(object):

    def __init__(self):
        self.ref=[]
        self.refName = ""
        self.startGuiding = True
        self.quit = False
	self.expTime = .5
	self.readoutOffset = 0
        self.c = CameraExpose()

    def takeImage(self, imType = None, imgName = None, imExp = None, imDir = None):
        im = self.c.expose(imgName, imExp, imDir)
        print "Takes image with camera, and saves it to the current directory"
        if im == True:
            return
        else:
            raise Exception

    def analyze(self,fits):
        output=[]
        hdulist = pyfits.open(fits)
        data = hdulist[0].data

        ccd = PyGuide.CCDInfo(200,21.3,1.6) #Since we're using it on one CCD, these should be constants
        ctr,imstat = PyGuide.findStars(data,None,None,ccd,1,False)[0:2] #need to choose mask here


        size= len(ctr)-1
        xcoord = ['XCoord']
        ycoord = ['YCoord']
        names = ['StarName']

        for x in range(size):
            xcoord = ctr[x].xyCtr[0]
            ycoord = ctr[x].xyCtr[1]
            name = x
            star_out = [name, xcoord, ycoord]
            print star_out
            output.append(star_out)

        #print "Running PyGuide.findStars on img to get coordinates of 0th star in list"
        return output

    def getOffset(self, imCoords):
        print self.ref[0]
        print imCoords[0]
        x = self.ref[1]
        y = self.ref[2]
        xx = imCoords[1]
        yy = imCoords[2]
        xoff = xx - x
        yoff = yy - y
        print "Finding offset between position of star 0 in current image and reference image"
        return xoff, yoff

    def coordCompare(self,c0 , c1, thres):
        print c0[1] - c1[1], c0[2] - c1[2]
        if np.abs(c0[1] - c1[1]) > float(thres) and np.abs(c0[2] - c1[2]) > float(thres):
            raise Exception
        else:
            return True


    def test(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        self.takeImage('image', self.refName,self.expTime, None)
        print self.refName
	print self.analyze(self.refName)
	return

    def run(self):
        self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        print 'taking reference image %s' % self.refName
	self.takeImage('image', self.refName,self.expTime) 
        refOptions = self.analyze(self.refName)
        print 'reference coords are (singluar selection, not robust): '
        self.ref = refOptions[0]
        print self.ref

        #for x in range(0,1):
        while (self.quit != True):

        #this is going to end up being a while loop for while(self.startGuiding == True) , which I think is controlled by the GUI.... or something
        # how do we knwo that the 0th image will always be the same?  Maybe create a threshold parameter.

            imName = time.strftime("%Y%m%dT%H%M%S.fits")
            self.takeImage('image',imName,self.expTime)
            time.sleep(float(self.expTime) + self.readoutOffset)
            coords = self.analyze(imName)
            for star in coords:
                print star
                if self.coordCompare(self.ref, star, 30):
                    foundStar = star
                    break
            print 'this is the start that corresponds to the ref star'
            print foundStar
            offsetx, offsety = self.getOffset(foundStar)
            print offsetx, offsety
            #print "Returning offset to telescope to drive it some way we haven't figured out yet"
        print 'guiding stopped'
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


