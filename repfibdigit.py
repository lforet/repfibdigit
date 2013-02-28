#!/usr/bin/python           # This is client.py file
 
import socket               # Import socket module
#System modules
import os
import Queue
import threading
import time


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
			#number_range = self.queue.get()
			number_range = self.get_next_chunk()
			print "number_range", number_range
			

			#test the number range
			self.test_range(number_range)
			
			print "done with task"


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
			print number_to_test, " is a Keith Number!"
			print "PROOF:"
			n=map(int,str(number_to_test))
			while number_to_test > sum(n):
				print n ," = ", sum(n)
				n=n[1:]+[sum(n)]
			print n ," = ", sum(n)
		#else:
		#	print number_to_test, " is NOT a Keith Number"
		return

	def test_range(self, number_range):
		#print "number_range", number_range
		low = number_range[0] 
		high = number_range[1]
		for x in xrange(low, high, 1):
			self.is_repfibdigit(x)
		return

	def get_next_chunk(self):
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

	#raw_input()
    # give the queue some data

	# get num to work from
	start_num = get_next_chunk()
	print "starting number:", start_num
	chunks = 1000
	raw_input()

	for i in range(3):
		the_range = [( (chunks*(i+1)) - (chunks-1)), (chunks * (i+1))]
		print the_range, the_range[0], the_range[1]
		queue.put(the_range)
		#raw_input()

	# Now wait for the queue to be empty, indicating that we have
	# processed all of the downloads.
	print '*** Main thread waiting'
	queue.join()
	print '*** Done'

