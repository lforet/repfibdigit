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
import cProfile


def is_repfibdigit(self, number_to_test):
		n=map(int,str(number_to_test))
		number_to_test = long(number_to_test)

		while number_to_test > n[0]:
			n=n[1:]+[sum(n)]
			#print n
		if (number_to_test == n[0]) & (number_to_test>9):
			print '---------------------------------------------'
			print 'queue:',  threading.current_thread()
			print number_to_test, " is a Keith Number!"
			#print "PROOF:"
			#n=map(int,str(number_to_test))
			#while number_to_test > sum(n):
			#	print n ," = ", sum(n)
			#	n=n[1:]+[sum(n)]
			#print n ," = ", sum(n)
			self.report_keith_num(number_to_test)
			print "new keith number reported!!!!"
			print '---------------------------------------------'
			#time.sleep(1)
		#else:
		#	print number_to_test, " is NOT a Keith Number"
		return
	#this function is to get around the 32bit native int barrier
	#not needed in 64 native systems

def my_xrange(self, start, stop, step):
   	i = start
   	while i < stop:
 		yield i
       		i += step

def test_range(self, the_range):
	low = the_range[0]
	high = the_range[1]
	for x in self.my_xrange(low, high, 1):
		self.is_repfibdigit(x)
		#self.report_work_completed(high)
		

def report_keith_num(self, num):
		#establish coms with server
		s = socket.socket()         # Create a socket object
		host = socket.gethostname() # Get local machine name
		port = 8000                # Reserve a port for your service.
		print 'Connecting to ', host, port
		s.connect((host, port))
		#while True:
		msg = 'k:' + str(num)
		print 'CLIENT reporting new keith number >> ', msg
		s.send(msg)
		ack  = s.recv(1024)
		print 'SERVER >> ', ack
		s.close                     # Close the socket when done
		

def get_work_unit():
		#establish coms with server
		s = socket.socket()         # Create a socket object
		host = socket.gethostname() # Get local machine name
		port = 8000                # Reserve a port for your service.
		print 'Connecting to ', host, port
		s.connect((host, port))
		msg = 'n'
		print 'CLIENT >> ', msg
		s.send(msg)
		server_reponse = s.recv(1024)
		new_work_unit = pickle.loads(server_reponse)
		print 'SERVER >> ', new_work_unit
		s.close                     # Close the socket when done
		return new_work_unit

def report_work_completed(work_unit_uuid):
		#establish coms with server
		s = socket.socket()         # Create a socket object
		host = socket.gethostname() # Get local machine name
		port = 8000                # Reserve a port for your service.
		print 'Connecting to ', host, port
		s.connect((host, port))
		msg = 'f:' + str(work_unit_uuid)
		print 'CLIENT reporting work completed >> ', msg
		s.send(msg)
		ack  = s.recv(1024)
		print 'SERVER >> ', ack
		s.close                     # Close the socket when done
########################################################################



if __name__=="__main__":

		while True:
			# gets the number range to test from the queue
			starting_number = self.queue.get()
			#starting_number = int(self.get_next_chunk())
			print 'queue:',  threading.current_thread()
			print "search in range:", starting_number

			#test the number range
			self.test_range(starting_number)
			print 'queue:',  threading.current_thread()
			print "completed: search range: ", starting_number

			# send a signal to the queue that the job is done
			self.queue.task_done()
 
