#!/usr/bin/python           # This is client.py file
 

#System modules
import os
import time
import itertools
import cPickle as pickle
import numpy as np
#import cProfile
import timeit
import uuid
import sys 
import fib


########################################################################

pgbreak = "-----------------------------------------------"


#----------------------------------------------------------------------
def is_repfibdigit( number_to_test):
	n = map(int,str(number_to_test))
	while number_to_test > n[0]:
		n=n[1:]+[sum(n)]
	if (number_to_test == n[0]) & (number_to_test>9):
		show_proof(number_to_test)
		#raw_input()
		#time.sleep(1)
	#else:
	#	print number_to_test, " is NOT a Keith Number"
	return


def is_repfibdigit2( number_to_test):
	if fib.is_repfibdigit(number_to_test) == True: 
		show_proof(number_to_test)
		#raw_input()
		#time.sleep(1)
	#else:
	#	print number_to_test, " is NOT a Keith Number"
	return



#this function is to get around the 32bit native int barrier
#not needed in 64 native systems
def my_xrange( start, stop, step):
	i = start
	while i < stop:
   			yield i
   			i += step

def show_proof(kn):
	print '---------------------------------------------'
	#print 'queue:',  threading.current_thread()
	print kn, " is a Keith Number!"
	print "PROOF:"
	n=map(int,str(kn))
	while kn > sum(n):
		print n ," = ", sum(n)
		n=n[1:]+[sum(n)]
	print n ," = ", sum(n)
	#self.report_keith_num(number_to_test)
	#print "new keith number reported!!!!"
	print '---------------------------------------------'
	print "press ENTER to continue"		


########################################################################


if __name__=="__main__":

	if len(sys.argv) > 1:
		end_num = sys.argv[1]

	nowtime = time.clock()
	# get num to work from
	start_num = 0
	print "Starting number:", start_num

	for x in xrange(start_num, int(end_num)):
		is_repfibdigit2(x)
		

	print
	print "completion time:", abs(nowtime - time.clock()) 
	print pgbreak

	#raw_input()
