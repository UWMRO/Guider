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
        self.ref= None  # Variable name to eventually hold the coordinate list for an image
        self.refName = None # Variable to hold the name of the reference image once taken
        self.quit = False # Boolean value that will stop operation if True, can be
			  # changed via the GUI and set via the startGuiding and
			  # stopGuiding functions.
	self.expTime = .5 # Image exposure time in seconds, used when calling the 
			  # CameraExpose object to take images.
	self.readoutOffset = 0 # Buffer added to sleep time to avoid the error thrown
			       # if code continues without completing image capture.
        self.c = CameraExpose() # CameraExpose object, used to take images
        self.l = Logger() #Logger class creates logfile of processes
        self.fakeImageDir = '/Users/jwhueh/projects/MRO/guiding_images/gcam_UT150425/' # Directory where fake images are
										       # stored for testing. 
        self.fakeOut =  False # Boolean value that if set to True, will test code using
			      # a set of test images, rather than taking new images
        self.currentImage = 2 # Integer used in testing, tracks how many images have been taken
        self.logType = 'guider' # Parameter used in  Logger class to create logfile
        self.thres = 30 # Thresholc value used in coordCompare when matching coordinates of
			# objects in images
	self.takeRef = False # Boolean value set to tell code to take a new reference image.
			     # Can be changed via the setTakeRef function.

    def takeImage(self, imType = None, imgName = None, imExp = None, imDir = None): 
        """Takes the class, a string keyword for image type, a string for image
        name, an integer for exposure tiem, and a string for directory name.
        The function checks if the variable fakeOut is equal to true first
        -- if so, ends function and carries out rest of code using existing
        images.  If not, the function takes an image using the CameraExpose
        object defined in the constructor, and checks that the image has
        been taken and saved.

        Args:
            imType (str): the type of image (bias, dark, object)
            imgName (str): the name of the image
            imExp (str): the exposure length in seconds
            imDir (str):  the directory of the image to be saved

        Returns:
            int.
            0 -- image was taken
            1 -- image not taken
            2 -- unknown state

        Raises:
            Exception

        """
        if self.fakeOut != True: 
            im = self.c.runExpose(imgName, imExp, imDir)
            self.l.logStr('Image\t%s %s %s' % (str(imgName), str(imExp), str(imDir)), self.logType)
            if im == True: # check on completion and save of image exposure
                return 0
            else:
                raise Exception("Image exposure not completed") 
                return 1
        else:
            return 3 # Simply returns if no exception raised

# Takes the class, and a string image name as parameters. The
# function then creates an array to store the object ccoordinates
# in, opens the image with the passed name, and takes the data
# (0th layer) from the image.  The function then uses PyGuide's
# (written by Russel Owen) function findStars to find the
# stars in the image.  The output of findStars is then iterated
# through, and x and y coordinates are pulled out and used along 
# with star names to populate the coorinate list 'output',
# which is then returned.
    def analyze(self,im): 
        output=[]
        hdulist = fits.open(im)
        data = hdulist[0].data

        ccd = PyGuide.CCDInfo(200,21.3,1.6) # Since we're using it on one CCD, these should be constants
        ctr,imstat = PyGuide.findStars(data,None,None,ccd,1,False)[0:2]

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

# Takes the class and the coordinate array from the analyze 
# function as parameters and finds the difference between these 
# coordinates and those for the reference image, to get x and 
# y offsets to give to the telescope. Before the offsets in x 
# and y are returned, runs a check to ensure that the offsets 
# are not too large (greater than some threshold defined 
# globally).  If they are, sets self.quit to True and writes 
# an error message to the console.
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

   
# Takes the class, the coordinate list generated from the reference 
# image, the coordinate list generated from the most recent tracking
# image, as well as the globally defined offset threshold as parameters.
# The function then goes through coordinate lists for current image and 
# finds new coordinates of guide star (chosen in ref image) by comparing
# coordinates and matching within some given threshold. If found within
# the threshold, returns true.  If not, sets self.quit to True to stop
# guiding operatinos and prints an error message to the console.
     def coordCompare(self, c0, c1, thres): 
        if np.abs(c0[1] - c1[1]) > float(thres) and np.abs(c0[2] - c1[2]) > float(thres):
            self.quit = True
            print 'too far off'
        else:
            return True

# This function takes only the class as a parameter, and is used for
# testing purposes.
    def test(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        self.takeImage('image', self.refName,self.expTime, None)
        print self.refName
	print self.analyze(self.refName)
	return

# Takes only the class as a parameter.  This function takes a new 
# reference image, the coordinate of objects in which  will 
# serve as the target for guiding.  This function creates a name 
# for the reference image and saves it, takes the image, analyzes
# it, and globally saves the coordinate list for that image.  It 
# then sets the guide star to be the star at the 0th spot in the 
# coordinate array (the brightest star), and sets the coordinates
# of it to the variable name self.ref.
    def takeRef(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
        if self.fakeOut == True: # If program has been set to guide on fake data for testing,
				 # variables are set differently than if not testing.  These
				 # differences are set in this section.
            self.refName = self.fakeImageDir + 'g' + str(self.currentImage).zfill(4) + '.fits'
            self.currentImage = self.currentImage + 1
            self.l.logStr('FakeImage\t%s' % str(self.refName), self.logType)
        self.takeImage('image', self.refName,self.expTime)
        refOptions = self.analyze(self.refName)
        # Future change: reference coords are (singluar selection, not robust). 
	# Don't assume the first (brightest) element is the best (or allow user
	# to choose guide star graphically).
        self.ref = refOptions[0]
        return

# This function takes only the class as a parameter.  The first
# check is if a new reference image is needed or not.  If so,
# it is taken and analyzed, and then the program returns to this
# function.  So long as not told to quit, the program enters a
# loop of taking images and sending offsets.  Each time through,
# a new image is taken (and the program sleeps during this),
# it is analyzed, the guide star is found using the
# coordCompare funciton, and offsets are found and returned
# via the getOffset function.  All of these processes are 
# written to the logfile each time, and there is a written
# process for running this same loop on fake images for
# testing.
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


