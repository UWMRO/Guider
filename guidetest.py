#!/usr/bin/env python

'''
Hardware control code for telescope guide camera
and associated field rotation and linear focus
motors.
'''

#Basic imports
from ctypes import *
import os, sys
import numpy as np
import time, datetime
import pyfits
import subprocess
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Phidget import PhidgetLogLevel

"""
Haydon Kerk Bipolar Stepper start parameters
A = Red/White
B = Red
C = Green/White
D = Green
Rotational:
A = Black
B = Green
C = Blue
D = Red
Linear:
A = Black (Red/White)
B = Red
C = Black (Green/White)
D = Green
Vel Limit = 22321
Accel = 262144
Current Limit = 0.31
"""


class GuideCamera(object):
    def __init__(self):
	self.stepper = Stepper()
	self.steppername = None
        self.stepperLin = 418356
        self.stepperRot = 399312

	self.gain = 1
	self.expScale = 5
	self.expNum = 1
	self.minFocus = -2000
	self.maxFocus = 2000
	self.focusStep = 100

    def testimage(self):
	'''
	Loop through a list of focus positions ranging from
	self.minFocus to self.maxFocus with a step size of
	self.focusStep

	At each focus position the camera will take self.expNum images
	with an exposure time of nX where n ranges (1 -> self.expNum) and
	X is self.expScale

	The camera gain is set with self.gain, must be int(1-8)
	'''

        #posList = [-10000, -5000, 0, 5000, 10000]
    	posList = np.arange(self.minFocus, self.maxFocus+self.focusStep, self.focusStep)
	print posList
	i = 0
    	j = 0
    	numPics = self.expNum
    	while run == True:
    	    while j < len(posList):
    	        p.move("linear", posList[j])
    	        while i < numPics:
		    now = datetime.datetime.now()
                    fileName = now.strftime("%Y%m%d-%H%M%S-%f")
                    exp = self.expScale*(i+1)
                    gain = self.gain
                    focus = posList[j]
                    print "Taking %.2f second image with gain of %d called %s" %(exp, gain, fileName)
		    subprocess.call('./camera image testimgs/%s.raw %d %d'%(fileName, int(exp*1000), int(gain)), shell=True)
                    self.binarytoFits(fileName, exp, gain, focus)
                    i = i+1
    		i = 0
    		j = j+1
    	    j = 0
	return

    def binarytoFits(self, fileName, exp, gain, focus):
        '''
	Routine to convert binary image files to FITS format
	and append a header with useful information
	'''

	binary=np.fromfile('testimgs/'+fileName+'.raw', dtype='u1').reshape(1024,1280)

        fileName = os.path.split(fileName)[1]
        prihdr = self.createHeader(exp, gain, focus)  #create emtpy header information
        hdu=pyfits.PrimaryHDU(binary, header = prihdr)  #create a primary header file for the FITS image
        hdulist=pyfits.HDUList([hdu])

        # Write the image and header to a FITS file using variable name.
        hdulist.writeto(os.getcwd()+"/testimgs/%s.fits"%fileName, clobber=True)

	#Remove the raw data file after the FITS is created
	try:
    	    os.remove('testimgs/'+fileName+'.raw')
	except OSError:
    	    pass

        return

    def createHeader(self, exp, gain, focus):
	'''
	FITS header object
	'''
        prihdr = pyfits.Header()
        prihdr['COMMENT'] = 'MRO Guider Camera'
        prihdr['COMMENT'] = 'Orion Star Shoot Auto Guider'
        prihdr['IMAGTYP'] = None
        prihdr['EXPTIME'] = exp
        prihdr['CCDBIN1'] = 1
        prihdr['CCDBIN2'] = 1
        prihdr['GAIN'] = gain
        prihdr['RN'] = None
	prihdr['FOCUSPOS'] = focus
        prihdr['IMAGTYP'] = 'guide'

        return prihdr


    def MotorChoice(self, name):
	if name == "linear":
	    self.steppername = self.stepperLin
	elif name == "rotational":
	    self.steppername = self.stepperRot
	else:
	    self.steppername = None
	    print("wrong stepper name")
	self.stepper.openPhidget(self.steppername)
	self.stepper.waitForAttach(10000)
        self.DisplayDeviceInfo
	return

    def DisplayDeviceInfo(self):
    	print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
  	print("Number of Motors: %i" % (self.stepper.getMotorCount()))

    def disconnDev(self):
	#print "Setting to Home Position"
	#self.stepper.setTargetPosition(0, 0)
	#time.sleep(4)
	#print "Shutting Down"
	self.motorPower(False)
	#print "Goodbye"
	self.stepper.closePhidget()

    def setupParm(self):
	self.stepper.setAcceleration(0, 30000)
    	self.stepper.setVelocityLimit(0, 8000)
	self.stepper.setCurrentLimit(0, 1.0)
	self.stepper.setCurrentPosition(0,0)

    def moveMotor(self, pos = None):
	self.stepper.setTargetPosition(0, int(pos))
	while self.stepper.getCurrentPosition(0) != int(pos) :
	    #print self.stepper.getCurrentPosition(0)
	    time.sleep(.1)

    def motorPower(self, val = False):
	self.stepper.setEngaged(0,val)


    def move(self, motor, pos):
        self.MotorChoice(motor)
        self.setupParm()
        self.motorPower(True)
        #self.DisplayDeviceInfo()
        time.sleep(1)
        print("Moving %s to %i" %(motor, pos))
	self.moveMotor(pos)
	time.sleep(2)
	self.disconnDev()

if __name__ == "__main__":
    gc = GuideCamera()
    run = True
    while run == True:
        gc.testimage()
