#!/usr/bin/env python

#Basic imports
from ctypes import *
import sys
import time
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

Vel Limit = 22321
Accel = 262144
Current Limit = 0.31
"""

class PhidgetMotorController(object):
	def __init__(self):
		self.stepper = Stepper()
		self.stepper.openPhidget()
		print('attaching stepper dev ...')
		self.stepper.waitForAttach(10000)
		self.DisplayDeviceInfo()
		

	def DisplayDeviceInfo(self):
    		print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.stepper.isAttached(), self.stepper.getDeviceName(), self.stepper.getSerialNum(), self.stepper.getDeviceVersion()))
    		print("Number of Motors: %i" % (self.stepper.getMotorCount()))

	def disconnDev(self):
		self.motorPower(False)
		self.stepper.closePhidget()

	def setupParm(self):
		self.stepper.setAcceleration(0, 90000)
	    	self.stepper.setVelocityLimit(0, 6200)
    		self.stepper.setCurrentLimit(0, 0.3)
		self.stepper.setCurrentPosition(0,0)

	def moveMotor(self, pos = None):
		self.stepper.setTargetPosition(0, int(pos))
		while self.stepper.getCurrentPosition(0) != int(pos) :
			print self.stepper.getCurrentPosition(0)
			time.sleep(.1)

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)
	

if __name__ == "__main__":
	p = PhidgetMotorController()
	p.setupParm()
	p.motorPower(True)
	p.moveMotor(20000)
	p.moveMotor(0)
	p.disconnDev()
