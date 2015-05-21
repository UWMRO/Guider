# Camera.py
# Camera imaging and fits routines using input from camera.cpp

import numpy as np
import pyfits
import subprocess
import time

# =========================================
# Run camera routine
# =========================================
name = "basic"
expose = "4000"

# Tells camera to take an image, it will output a binary file named "test" with 1000 ms exposure.
# Can also use './camera test 0 0' to check camera.
subprocess.Popen(['/home/linaro/Camera/camera', 'image', 'binary', expose])

# Pause for the camera to run
time.sleep(3+(int(expose)/1000))

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

# Create a primary header file for the FITS image
hdu=pyfits.PrimaryHDU(binary)
hdulist=pyfits.HDUList([hdu])

# Add time, exposure length, and file name to header.
# Need to add

# Write the image and header to a FITS file using variable name.
hdulist.writeto(name+'.fits')

print "Camera and FITS routines complete" 
