#! /usr/bin/python
"""
guideCam.py
MRO guider imaging and fits routines using input from camera.cpp
"""

__author__ = "Matt Armstrong"
__copyright__ = "NA"
__credits__ = ["github.com/UWMRO/"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "NA"
__email__ = "NA"
__status__ = "Developement"

import numpy as np
import pyfits
import subprocess
import time
import os
import glob
import thread
import traceback


class GuideCamera(object):
    def __init__(self):
        self.wait = 1.0
        self.status = None
        self.ssag = os.getcwd()+"/camera"
        self.statusDict = {1:'idle', 2:'expose', 3:'reading'}
        self.gain = 1

    def expose(self, name, exp, dir, gain):
        thread.start_new_thread(self.runExpose, (name, exp, dir, gain))

    def runExpose(self, name, exp, dir, gain):
        """
        Connect to the OpenSSAG and take image
        input a given file name and exposure
        output whether the image was successful
        Tells camera to take an image, it will output a binary file named "test" with 1000 ms exposure.
        Can also use './camera test 0 0' to check camera.
        """

        if dir == None:
            dir = os.getcwd()

        if '.fit' not in name:
            name = name+'.fits'
        name = dir+'/'+str(name)
        #print dir, name, self.ssag, exp
        expose = float(exp)*1000

        if gain == None:
            gain = self.gain

        try:

            subprocess.Popen([self.ssag, 'image', 'binary', str(expose), str(gain)])
            self.status = 2
            #Pause for the camera to run
            time.sleep(self.wait+float(exp))
            self.status = 1

        except Exception,e:
            print ("failed")
            print (str(e))
            traceback.print_exc()
            return False
        return True

    def binarytoFits(self, fileName, exp, gain, focus):
        binary=np.fromfile(fileName, dtype='u1').reshape(1024,1280)

        fileName = os.path.split(fileName)[1]
        fileName = fileName[:-4]
        print fileName
        prihdr = self.createHeader(exp, gain)  #create emtpy header information
        hdu=pyfits.PrimaryHDU(binary, header = prihdr)  #create a primary header file for the FITS image
        hdulist=pyfits.HDUList([hdu])

        prihdr['FOCUSPOS'] = str(focus)
        prihdr['IMAGTYP'] = 'guide'
        # Write the image and header to a FITS file using variable name.

        hdulist.writeto(os.getcwd()+"/20171015/%s.fits"%fileName, clobber=True)
        return

    def createHeader(self, exp, gain):
        prihdr = pyfits.Header()
        prihdr['COMMENT'] = 'MRO Guider Camera'
        prihdr['COMMENT'] = 'Orion Star Shoot Auto Guider'
        prihdr['IMAGTYP'] = None
        prihdr['EXPTIME'] = exp
        prihdr['CCDBIN1'] = 1
        prihdr['CCDBIN2'] = 1
        prihdr['GAIN'] = gain
        prihdr['RN'] = None
        return prihdr

    def checkStatus(self):
        print ("return some status message")
        print (self.status, self.statusDict[self.status])
        return self.status

    def checkConnection(self):
        try:
            subprocess.Popen([self.ssag, '0', '0', '0'])
        except Exception, e:
            print (e)

    def help(self):
        print (__doc__)
        return

if __name__=="__main__":
    gc = GuideCamera()
    fNameList = glob.glob(os.getcwd()+'/20171015/*.raw')

    for fName in fNameList:
        gc.binarytoFits(fName, exp, gain, focus)



    #c.runExpose('test',0.1, None, 8)
