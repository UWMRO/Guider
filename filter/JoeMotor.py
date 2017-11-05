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

class PhidgetMotorController(object):
	def __init__(self):
		self.stepper = Stepper()
		self.steppername = None
#		self.stepper.openPhidget(418356)
	#	self.stepper.openPhidget()
		print('attaching stepper dev ...')
	#	self.stepper.waitForAttach(10000)
	#	self.DisplayDeviceInfo
		
	def MotorChoice(self, name):
		if name == "linear":
			self.steppername = 418356
		elif name == "rotational":
			self.steppername = 399312
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
#		print "Setting to Home Position"
#		self.stepper.setTargetPosition(0, 0)
#		time.sleep(4)
#		print "Shutting Down"
		self.motorPower(False)
#		print "Goodbye"
		self.stepper.closePhidget()

	def setupParm(self):
		self.stepper.setAcceleration(0, 30000)
	    	self.stepper.setVelocityLimit(0, 8000)
    		self.stepper.setCurrentLimit(0, 1.0)
		self.stepper.setCurrentPosition(0,0)

	def moveMotor(self, pos = None):
		self.stepper.setTargetPosition(0, int(pos))
		while self.stepper.getCurrentPosition(0) != int(pos) :
		#	print self.stepper.getCurrentPosition(0)
			time.sleep(.1)

	def motorPower(self, val = False):
		self.stepper.setEngaged(0,val)

	def filterselect(self, num = None):
		print "Moving to filter position %d" % num
		if int(num)<= 6 and int(num)>=1:
			self.stepper.setTargetPosition(0, int(num)*6958)
		elif int(num)>6:
			print "Not Valid Filter Number"
		elif int(num)<1:
			print "Not Valid Filter Number"

#	def findhome(self):
#		while x = False
#			self.stepper.setTargetPosition(0, 9999999)
#		

	def move(self, motor, pos):
            self.MotorChoice(motor)
	    self.setupParm()
            self.motorPower(True)
            #self.DisplayDeviceInfo()
            time.sleep(1)
            print("Moving %s to %i" %(motor, pos))
	    self.moveMotor(pos)
	    time.sleep(1)
	    self.disconnDev()


if __name__ == "__main__":

	p = PhidgetMotorController()
	p.move("linear", 10000)
	'''
	p.MotorChoice("linear")
	p.setupParm()
	p.motorPower(True)
	p.DisplayDeviceInfo()
	time.sleep(1)
	p.moveMotor(-20000)
	time.sleep(1)
	p.moveMotor(0)
	time.sleep(1)
	p.moveMotor(10000)

	p = PhidgetMotorController()
	p.MotorChoice("rotational")
	p.setupParm()
	p.motorPower(True)
	p.DisplayDeviceInfo()
	time.sleep(1)
	p.moveMotor(2000)
	time.sleep(1)
	p.moveMotor(0)
	p.disconnDev()
	'''