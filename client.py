#!/usr/bin/python
 
import socket              
import os
import time
import itertools
import cPickle as pickle
import numpy as np
import timeit
import uuid
import sys

########################################################################
import esky
from esky.util import appdir_from_executable

#python setup.py bdist_esky

def restart_this_app():
    appexe = appexe_from_executable(sys.executable)
    os.execv(appexe,[appexe] + sys.argv[1:])

def appexe_from_executable(exepath):
    appdir = appdir_from_executable(exepath)
    exename = os.path.basename(exepath)
    #  On OSX we might be in a bundle
    if sys.platform == "darwin":
        if os.path.isdir(os.path.join(appdir,"Contents","MacOS")):
            return os.path.join(appdir,"Contents","MacOS",exename)
    return os.path.join(appdir,exename)

def initialize_client():
	#handled auto-update stuff
	app = esky.Esky(sys.executable, "http://isotope11.selfip.com:8000")
	print "You are running Client version: %s" % app.active_version
	print "checking for client update..."
	time.sleep(2)
	if app.find_update() == None:
		print "no update available..."
		time.sleep(2)
	#print "Update available....", app.find_update(), app.active_version
	#raw_input()
	if app.find_update() != None:
		print "Update available....", app.find_update()
		print "SuperUser permission required to update..."
		if app.has_root() == False:
			 app.get_root()
		print "auto-updating..."
		try:
			app.auto_update()
		except Exception, e:
			print "ERROR UPDATING APP:", e
		app.reinitialize()
		print "restarting with new client..."
		time.sleep(3)
		restart_this_app()

########################################################################
#SERVER = ''
SERVER = 'isotope11.selfip.com'
#PORT = 5555
PORT = 6666
pgbreak = "-----------------------------------------------"


#----------------------------------------------------------------------
def is_repfibdigit( number_to_test):
	n = map(int,str(number_to_test))
	while number_to_test > n[0]:
		n=n[1:]+[sum(n)]
	if (number_to_test == n[0]) & (number_to_test>9):
		print '---------------------------------------------'
		print number_to_test, " is a Keith Number!"
		print "PROOF:"
		n=map(int,str(number_to_test))
		while number_to_test > sum(n):
			print n ," = ", sum(n)
			n=n[1:]+[sum(n)]
		print n ," = ", sum(n)
		report_keith_num(number_to_test)
		print "new keith number reported!!!!"
		print '---------------------------------------------'
		print "press ENTER to continue"
		raw_input()
		#time.sleep(1)
	#else:
	#	print number_to_test, " is NOT a Keith Number"
	return

#this function is to get around the 32bit native int barrier
#not needed in 64 native systems
def my_xrange(start, stop, step):
	i = start
	while i < stop:
   			yield i
   			i += step

def test_range( the_range):
	for x in my_xrange(the_range[0], the_range[1], 1):
		is_repfibdigit(x)
	

def report_keith_num( num):
	#establish coms with server
	s = socket.socket()         # Create a socket object
	while True:
		try:
			print pgbreak
			print 'Connecting to to REPORT KEITH # FOUND!! ', SERVER, PORT
			s.connect((SERVER, PORT))
			break
		except:
			print "connection failed."
			time.sleep(1)
			pass
	while True:
		try:
			msg = 'k:' + str(num)
			print 'CLIENT reporting new keith number >> ', msg
			s.send(msg)
			break
		except:
			print "waiting on repsonse from SERVER:"
			time.sleep(.5)
			pass
	while True:
		try:
			ack  = s.recv(1024)
			break
		except:
			print "waiting on acknowledgement from SERVER that KEITH number was recorded:"
			time.sleep(.5)
			pass
	print 'SERVER >> ', ack
	s.close                     # Close the socket when done
		

def get_work_unit():
	#establish coms with server
	s = socket.socket()         # Create a socket object
	#host = socket.gethostname() # Get local machine name
	#port = 8000                # Reserve a port for your service.
	while True:
		try:
			print 
			print "Getting new work unit...."
			print 'Connecting to ', SERVER, PORT
			s.connect((SERVER, PORT))
			break
		except:
			print "connection failed."
			time.sleep(1)
			pass
	while True:
		try:
			msg = 'n'
			print 'CLIENT >> ', msg
			s.send(msg)
			break
		except:
			print "new work request failed...."
			time.sleep(1)
			pass
	while True:
		try:
			server_reponse = s.recv(1024)
			break
		except:
			print "waiting on repsonse from SERVER:"
			time.sleep(.5)
			pass
	new_work_unit = pickle.loads(server_reponse)
	print 'SERVER >> ', new_work_unit
	s.close                     # Close the socket when done
	return new_work_unit

def report_work_completed(clientID, work_unit_uuid):
	#print "reporting work unit to server...."
	#establish coms with server
	s = socket.socket()         # Create a socket object
	#host = socket.gethostname() # Get local machine name
	#port = 8000                # Reserve a port for your service.
	while True:
		try:
			print
			print "reporting work unit to server...."
			print 'Connecting to ', SERVER, PORT
			s.connect((SERVER, PORT))
			break
		except:
			print "connection failed."
			time.sleep(1)
			pass
	while True:
		try:
			msg = 'f:' + clientID + "^" + str(work_unit_uuid)
			s.send(msg)
			print 'CLIENT reporting work completed >> ', msg
			break
		except:
			print "CLIENT reporting work to SERVER failed...."
			time.sleep(.5)
			pass
	while True:
		try:
			ack = s.recv(1024)
			break
		except:
			print "waiting on acknowledgement from SERVER that work unit was recorded:"
			time.sleep(.5)
			pass
	print 'SERVER >> ', ack
	s.close                     # Close the socket when done
########################################################################


if __name__=="__main__":

	initialize_client()

	# Set up some global variables
	clientID = str(uuid.uuid1())
	while True:
		print pgbreak
		nowtime = time.clock()
		# get num to work from
		work_unit = get_work_unit()
		the_range = (int(work_unit[0]), int(work_unit[1])+1)
		test_range(the_range)
		report_work_completed(clientID, work_unit[2])
		print
		print "completion time:", abs(nowtime - time.clock()) 
		print pgbreak
		#raw_input()

