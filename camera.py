#! /usr/bin/python
"""
camera.py
Camera imaging and fits routines using input from camera.cpp
"""

__author__ = "John Armstrong"
__copyright__ = "NA"
__credits__ = ["Joseph Huehnerhoff"]
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
import Image

class CameraExpose(object):
    def __init__(self):
        self.wait = 1.0
        self.status = None

    def expose(self, name, exp, dir):
        """
        Connect to the OpenSSAG and take image
        input a given file name and exposure
        output whether the image was successful
        """
        
        if dir == None:
            dir = os.getcwd()

        if '.fit' not in name:
            name = name+'.fits'
        name = dir+'/'+str(name)
       
        try:
            
            # Tells camera to take an image, it will output a binary file named "test" with 1000 ms exposure.
            # Can also use './camera test 0 0' to check camera.
            #subprocess.Popen(['/home/linaro/Camera/camera', 'image', 'binary', str(exp * 1000)])

            #Pause for the camera to run
            time.sleep(self.wait+float(exp))

            #==============================================
            # Open binary file from camera as a numpy array
            # =============================================
            binary=np.fromfile('binary',dtype='u1').reshape(1280,1024)

            # --------------------------
            # Used for testing array procedure, can remove once program is tested on-sky.
            # print binary.shape
            # print binary.dtype.name
            # print binary
            # ---------------------------

            prihdr = self.createHeader()  #create emtpy header information
            hdu=pyfits.PrimaryHDU(binary, header = prihdr)  #create a primary header file for the FITS image
            hdulist=pyfits.HDUList([hdu])

            # Write the image and header to a FITS file using variable name.
            name = self.checkFile(name)
            hdulist.writeto(name)
            im = Image.fromarray(binary)
            im.save("tmp.jpg")
            

            print "Camera and FITS routines complete" 
            return True
        except Exception,e:
            print "failed"
            print str(e)
            return False

    def checkFile(self, fileName):
        if os.path.exists(fileName):
            print '%s exists, appending unique date stamp' % fileName
            name = fileName.replace('.fits','')+time.strftime('_%Y%m%dT%H%M%S.fits')
            print 'New filename is %s' % name
            return name
        else:
            return fileName

    def createHeader(self):
        prihdr = pyfits.Header()
        prihdr['COMMENT'] = 'MRO Guider Camera'
        prihdr['COMMENT'] = 'Orion Star Shoot Auto Guider'
        prihdr['IMAGTYP'] = None
        prihdr['EXPTIME'] = None
        prihdr['CCDBIN1'] = 1
        prihdr['CCDBIN2'] = 1
        prihdr['GAIN'] = None
        prihdr['RN'] = None
        return prihdr

    def checkStatus(self):
        print "return some status message"
        self.status = False
        return self.status

    def checkConnection(self):
        try:
            subprocess.Popen(['/home/linaro/Camera/camera', '0', '0', '0'])
        except Exception, e:
            print e


    def help(self):
        print __doc__
        return

if __name__=="__main__":
    c = CameraExpose()
    c.expose('test',1, None)
