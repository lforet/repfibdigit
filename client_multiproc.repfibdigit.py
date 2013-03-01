
import socket               # Import socket module
#System modules
import os
import Queue
import threading
import time
import itertools
import pp

def is_repfibdigit(number_to_test):
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
		report_keith_num(number_to_test)
		print "new keith number reported!!!!"
		print '---------------------------------------------'

def my_xrange(start, stop):
	i = start
	while i < stop:
   			yield i
   			i += 1

def test_range(the_range):
	low = the_range[0]
	high = the_range[1]
	for x in my_xrange(low, high):
		is_repfibdigit(x)
	report_work_completed(high)

def report_work_completed(num):
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
	

def report_keith_num(num):
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
	s.close                     # Close the socket when don

if __name__ == '__main__':

	job_server = pp.Server()
	print "# of CPU:", job_server.get_ncpus()
	raw_input()
	nowtime = time.time()
	print "nowtime", nowtime
	p1 = job_server.submit(test_range,( (1,250000) ),) 

	p2 = job_server.submit(test_range,((250001,500000)),)

	p3 = job_server.submit(test_range,((500001,750000)),)

	p4 = job_server.submit(test_range,((750001,1000000)),)

	print "time:", abs(nowtime - time.time())
