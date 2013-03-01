#!/usr/bin/python           # This is client.py file
 
import socket               # Import socket module
#System modules
import os
import Queue
import threading
import time
import itertools

########################################################################
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
			print "search in range:", starting_number

			#test the number range
			self.test_range(starting_number)
			print 'queue:',  threading.current_thread()
			print "completed: search range: ", starting_number

			# send a signal to the queue that the job is done
			self.queue.task_done()
 
    #----------------------------------------------------------------------

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
			print "PROOF:"
			n=map(int,str(number_to_test))
			while number_to_test > sum(n):
				print n ," = ", sum(n)
				n=n[1:]+[sum(n)]
			print n ," = ", sum(n)
			self.report_keith_num(number_to_test)
			print "new keith number reported!!!!"
			print '---------------------------------------------'
			time.sleep(1)
		#else:
		#	print number_to_test, " is NOT a Keith Number"
		return
	#this function is to get around the 32bit native int barrier
	#not needed in 64 native systems
	def my_xrange(self, start, stop):
   		i = start
   		while i < stop:
       			yield i
       			i += 1

	def test_range(self, the_range):
		low = the_range[0]
		high = the_range[1]
		for x in self.my_xrange(low, high):
			self.is_repfibdigit(x)
		self.report_work_completed(high)
		

	def report_work_completed(self, num):
		#establish coms with server
		s = socket.socket()         # Create a socket object
		host = socket.gethostname() # Get local machine name
		port = 8000                # Reserve a port for your service.
		print 'Connecting to ', host, port
		s.connect((host, port))
		#while True:
		msg = 'f:' + str(num)
		print 'CLIENT reporting work completed >> ', msg
		s.send(msg)
		ack  = s.recv(1024)
		print 'SERVER >> ', ack
		s.close                     # Close the socket when done
		

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
		

def get_next_chunk():
	#establish coms with server
	s = socket.socket()         # Create a socket object
	host = socket.gethostname() # Get local machine name
	port = 8000                # Reserve a port for your service.
	print 'Connecting to ', host, port
	s.connect((host, port))
	#while True:
	print 'CLIENT >> '
	msg = 'n'
	s.send(msg)
	new_num = s.recv(1024)
	print 'SERVER >> ', new_num
	s.close                     # Close the socket when done
	return new_num
########################################################################



if __name__=="__main__":


	# Set up some global variables
	num_fetch_threads = 2
	queue = Queue.Queue()

	# create a thread pool and give them a queue
	for i in range(num_fetch_threads):
		worker = repfigtest(queue)
		worker.setDaemon(True)
		worker.start()
		#time.sleep(2)
	print "finished setting up queue workers"

	raw_input()
    	# give the queue some data


	
	#x = 0
	while True:
		# get num to work from
		start_num = int(get_next_chunk())
		print "starting number:", start_num
		chunks = 100000
		#raw_input()
		for i in range(num_fetch_threads*2):
			the_range = [( start_num + ( (chunks*(i+1)) - (chunks-1) )), ( start_num + (chunks * (i+1)))]
			print the_range, the_range[0], the_range[1]
			print "range:", the_range 
			#raw_input('next worker data')
			queue.put(the_range)
			#x = x + 1
			#raw_input('next worker data')

		# Now wait for the queue to be empty, indicating that we have
		# processed all of the downloads.
		print '*** Main thread waiting'
		queue.join()
		print '*** Done'
		#raw_input('next series')
		print 'next series.....................................'

