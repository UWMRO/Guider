#! /usr/bin/python
"""
Camera.py
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
        
        if '.fit' not in name:
        #    pass
        #else:
            name = name+'.fits'
        name = dir+'/'+str(name)

        if dir == None:
            dir = os.getcwd()
        
        try:
            
            # Tells camera to take an image, it will output a binary file named "test" with 1000 ms exposure.
            # Can also use './camera test 0 0' to check camera.
            subprocess.Popen(['/home/linaro/Camera/camera', 'image', 'binary', str(exp * 1000)])

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

            name = 
            selfcheckFile(
            hdulist.writeto((str(name)))

            print "Camera and FITS routines complete" 
            return True
        except Exception,e:
            print "failed"
            print str(e)
            return False

    def checkFile(self, fileName):
        if os.path.exists(fileName):
            print fileName
            print 'file exists, deleting'
            os.system('rm %s' % fileName)
            return

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

    def help(self):
        print __doc__
        return

if __name__=="__main__":
    c = CameraExpose()
    c.expose('test.fits',1, None)
