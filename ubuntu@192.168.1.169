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
########################################################################

SERVER = 'isotope11.selfip.com'
#SERVER = ''
PORT = 6666 

class repfigtest(threading.Thread):
	"""Threaded RepFibDigit"""
	#----------------------------------------------------------------------
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
	#----------------------------------------------------------------------
	def run(self):
		while True:
			# gets the number range to test from the queue
			starting_number = self.queue.get()
			#starting_number = int(self.get_next_chunk())
			print 'queue:',  threading.current_thread()
			print "Work unit search range:", starting_number

			#test the number range
			self.test_range(starting_number)
			print 'finished work unit queue:',  threading.current_thread()
			#print "completed: search range: ", starting_number

			# send a signal to the queue that the job is done
			self.queue.task_done()
 
    #----------------------------------------------------------------------
	def is_repfibdigit(self, number_to_test):
		n = map(int,str(number_to_test))
		while number_to_test > n[0]:
			n=n[1:]+[sum(n)]
		if (number_to_test == n[0]) & (number_to_test>9):
			print '---------------------------------------------'
			print 'queue:',  threading.current_thread()
			print number_to_test, " is a Keith Number!"
			print "PROOF:"
			n=map(int,str(number_to_test))
			while number_to_test > sum(n):
				print n ," = ", sum(n)
				n=n[1:]+[sum(n)]
			print n ," = ", sum(n)
			self.report_keith_num(number_to_test)
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
	def my_xrange(self, start, stop, step):
   		i = start
   		while i < stop:
       			yield i
       			i += step

	def test_range(self, the_range):
		for x in self.my_xrange(the_range[0], the_range[1], 1):
			self.is_repfibdigit(x)
		#self.report_work_completed(high)
		

	def report_keith_num(self, num):
		#establish coms with server
		s = socket.socket()         # Create a socket object
		while True:
			try:
				print 'Connecting to to REPORT KEITH # FOUND!! ', SERVER, PORT
				s.connect((SERVER, PORT))
				break
			except:
				time.wait(.2)
				pass
		msg = 'k:' + str(num)
		print 'CLIENT reporting new keith number >> ', msg
		s.send(msg)
		ack  = s.recv(1024)
		print 'SERVER >> ', ack
		s.close                     # Close the socket when done
		

def get_work_unit():
	print "Getting new work unit...."
	#establish coms with server
	s = socket.socket()         # Create a socket object
	#host = socket.gethostname() # Get local machine name
	#port = 8000                # Reserve a port for your service.
	while True:
		try:
			print 'Connecting to ', SERVER, PORT
			s.connect((SERVER, PORT))
			break
		except:
			time.wait(.2)
			pass
	msg = 'n'
	print 'CLIENT >> ', msg
	s.send(msg)
	server_reponse = s.recv(1024)
	new_work_unit = pickle.loads(server_reponse)
	print 'SERVER >> ', new_work_unit
	s.close                     # Close the socket when done
	return new_work_unit

def report_work_completed(work_unit_uuid):
	print "reporting work unit to server...."
	#establish coms with server
	s = socket.socket()         # Create a socket object
	#host = socket.gethostname() # Get local machine name
	#port = 8000                # Reserve a port for your service.
	while True:
		try:
			print 'Connecting to ', SERVER, PORT
			s.connect((SERVER, PORT))
			break
		except:
			time.wait(.2)
			pass
	msg = 'f:' + str(work_unit_uuid)
	print 'CLIENT reporting work completed >> ', msg
	s.send(msg)
	ack  = s.recv(1024)
	print 'SERVER >> ', ack
	s.close                     # Close the socket when done
########################################################################


if __name__=="__main__":

	# Set up some global variables
	#multiple threads slows app down
	num_fetch_threads = 1
	queue = Queue.Queue()

	# create a thread pool and give them a queue
	for i in range(num_fetch_threads):
		worker = repfigtest(queue)
		worker.setDaemon(True)
		worker.start()
		#time.sleep(2)
	print "finished setting up queue workers"
	#raw_input()
    	# give the queue some data
	#nowtime = time.clock()
	#x = 0
	while True:
		nowtime = time.clock()
		# get num to work from
		work_unit = get_work_unit()
		start_num = int(work_unit[0])
		#print "Starting number:", start_num
		#if start_num > 5752090994058710841670361653731519: break
		chunks = 1 + (((int(work_unit[1]))-start_num) / num_fetch_threads)
		#print "chucks:", chunks
		#raw_input()
		for i in xrange(num_fetch_threads):
			the_range = [( start_num + ( (chunks*(i+1)) - (chunks) )), ( start_num + (chunks * (i+1)))]
			print the_range, the_range[0], the_range[1]
			#print "Work Unit range:", the_range 
			#raw_input('next worker data')
			queue.put(the_range)
			#x = x + 1
			#raw_input('next worker data')

		# Now wait for the queue to be empty, indicating that we have
		# processed all of the downloads.
		print '*** Main thread waiting'
		queue.join()
		report_work_completed(work_unit[2])
		#raw_input('next series')
		print '-----------------------------------------------------'
		print "completion time:", abs(nowtime - time.clock()) 
		
		#raw_input()
