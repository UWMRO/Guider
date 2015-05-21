import time
import subprocess
import PyGuide
import numpy as np
from astropy.io import fits
import subprocess



class Guider(object):

    def __init__(self):
        self.ref=[]
        self.refName = ""
        self.startGuiding = True
        self.quit = False
	self.expTime = 1000
	self.readoutOffset = 0

    def takeImage(self, imType = None, imgName = None, imExp = None):
        print "subprocess.Popen(['sudo','/home/linaro/Camera/camera'," + str(imType) + "," + str(imgName) + "," + str(imExp) + "])"
	subprocess.Popen(['sudo','/home/linaro/Camera/camera',str(imType),str(imgName),str(imExp)])
        print "Takes image with camera, and saves it to the current directory"
        #the file is not /home/linaro/Camera/camera anymore oh no >.<

    def analyze(self,fits):
        hdulist = fits.open(fits)
        data = hdulist[0].data

        ccd = PyGuide.CCDInfo(200,21.3,1.6) #Since we're using it on one CCD, these should be constants
        ctr,imstat = PyGuide.findStars(data,None,None,ccd,1,False)[0:2] #need to choose mask here

        xcoord = ['XCoord']
        ycoord = ['YCoord']
        names = ['StarName']

        for x in range(0,size):
            xcoord = np.append(xcoord, ctr[x].xyCtr[0])
            ycoord = np.append(ycoord, ctr[x].xyCtr[1])
            names = np.append(names, x)

        one = xcoord.reshape((size + 1,1))
        two = ycoord.reshape((size + 1,1))
        thr = names.reshape((size + 1,1))
        guideData = np.hstack((thr,one,two))
        print "Running PyGuide.findStars on img to get coordinates of 0th star in list"
        return guideData

    def getOffset(self,ref, imCoords):
        x = ref[1][1]
        y = ref[1][2]
        xx = imCoords[1][1]
        yy = imCoords[1][2]
        xoff = xx - x
        yoff = yy - y
        print "Finding offset between position of star 0 in current image and reference image"
        return xoff, yoff


    def test(self):
	self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fit"
        self.takeImage('image', self.refName,self.expTime)
	time.sleep(3)
	print self.analyze(self.refName)
	return

    def run(self):
        self.refName = time.strftime("%Y%m%dT%H%M%S") + ".fits"
	self.takeImage('image', self.refName,self.expTime) 
        self.ref = self.analyze(self.refName)

        for x in range(0,1):
        #while (self.quit == True):

        #this is going to end up being a while loop for while(self.startGuiding == True) , which I think is controlled by the GUI.... or something

            imName = time.strftime("%Y%m%dT%H%M%S.fits")
            takeImage('image',imName,self.expTime)
            time.sleep(float(self.expTime) + self.readoutOffset)
            coords = analyze(imName)
            offsetx, offsety = getOffset(self.ref, coords)
            print "Returning offset to telescope to drive it some way we haven't figured out yet"
	return

    def startGuiding(self):
        self.quit = True
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


#if __main__ == "__main__": #the if is so that the program only runs when the command is
#    g = Guider(object)           #python guider.py, not when the program is imported
  #  g.startGuiding()
   # g.run()
 #   g.takeImage('image', imName, self.expTime)


g = Guider()
g.test()


