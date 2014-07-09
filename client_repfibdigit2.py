#!/usr/bin/python           # This is client.py file
 
import socket               # Import socket module
#System modules
import os
import Queue
import threading
import time
import itertools
import cPickle as pickle
import numpy as np
#import cProfile
import timeit
import uuid
import sys 
#import fib

import keith

########################################################################

pgbreak = "-----------------------------------------------"


#----------------------------------------------------------------------
def is_repfibdigit(number_to_test):
	n = map(int,str(number_to_test))
	while number_to_test > n[0]:
		n=n[1:]+[sum(n)]
	if (number_to_test == n[0]) & (number_to_test>9):
	#if fib.is_repfibdigit(number_to_test) == True:
		print '---------------------------------------------'
		print 'queue:',  threading.current_thread()
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

def cuda_keith(the_range):
	print "calling cuda test for range:", the_range
	k_numbers = keith.find_keith(the_range[0], end_value=the_range[1], block_size=None, grid_size=None, verbose=True, iteration_limit=None)
	if len(k_numbers) > 0:
		print "FOUND KEITH NUMBER USING CUDA!!", k_numbers
		print "verifying..", the_range
		for x in k_numbers:
			is_repfibdigit(x)
		#raw_input()
	

def test_range(the_range):
	cuda_keith(the_range)
	#print type(the_range[0])
	#raw_input()
	#sys.exit()
	#for x in self.my_xrange(the_range[0], the_range[1], 1):
	#	self.is_repfibdigit(x)
	#self.report_work_completed(high)
	

def report_keith_num(num):
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

	#host = socket.gethostname() # Get local machine name
	#port = 8000                # Reserve a port for your service.
	new_work_unit = None
	while new_work_unit == None:
		s = socket.socket()         # Create a socket object
		try:
			print 
			print "Getting new work unit...."
			print 'Connecting to ', SERVER, PORT
			s.connect((SERVER, PORT))
		except:
			print "connection failed."
			time.sleep(1)
			pass
		try:
			msg = 'n'
			print 'CLIENT >> ', msg
			s.send(msg)
		except:
			print "new work request failed...."
			time.sleep(1)
			pass

		try:
			server_reponse = s.recv(1024)
			#break
		except:
			print "waiting on repsonse from SERVER:"
			time.sleep(.5)
			pass
		try:
			new_work_unit = pickle.loads(server_reponse)
			print 'SERVER >> ', new_work_unit
			#s.close
		except:
			#s.close
			print "corrupt new work unit..."
			#new_work_unit = None
			time.sleep(1)
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

	#multiple threads slows app down
	num_fetch_threads = 1	


	SERVER = 'isotope11.selfip.com'
	#SERVER = 'localhost'
	PORT = 6666 

	#if len(sys.argv) < 1:
	#	print "restart with parameters: SERVER_NAME or SERVER_IP"

	if len(sys.argv) > 1:
		try:
			SERVER = sys.argv[1]
		except:
			print "restart with parameters: #_of_threads, SERVER_NAME or SERVER_IP"
			sys.exit()

	# Set up some global variables
	clientID = str(uuid.uuid1())

	while True:
		nowtime = time.clock()
		# get num to work from
		work_unit = get_work_unit()
		the_range = [int(work_unit[0]), int(work_unit[1])]
		test_range(the_range)

		
		#print "Work_unit:", work_unit
		#start_num = int(work_unit[0])
		#print "Starting number:", start_num
		#if start_num > 5752090994058710841670361653731519: break
		#chunks = 1 + (((int(work_unit[1]))-start_num) / num_fetch_threads)
		#print "chucks:", chunks
		#raw_input()
		#for i in xrange(num_fetch_threads):
		#	the_range = [( start_num + ( (chunks*(i+1)) - (chunks) )), ( start_num + (chunks * (i+1)))]
			#print the_range, the_range[0], the_range[1]
			#print "Work Unit range:", the_range 
			#raw_input('next worker data')
		#	queue.put(the_range)
			#x = x + 1
			#raw_input('next worker data')

		# Now wait for the queue to be empty, indicating that we have
		# processed all of the downloads.
		#print '*** Main thread waiting'
		#queue.join()
		report_work_completed(clientID, work_unit[2])
		#raw_input('next series')
		print
		print "completion time:", abs(nowtime - time.clock()) 
		print pgbreak *2
		
		#raw_input()
