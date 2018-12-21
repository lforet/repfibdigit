from datetime import datetime
import multiprocessing

def search_for_keith_number(search_range=[], worker_id=1):
	print ('Worker: ' + str(i) + '  Searching range:'+ str(search_range))
	test_range(search_range, worker_id)
	print ('Worker: ' + str(i) + ' finished')
	return

def is_repfibdigit(number_to_test, worker_id=None):
	n = map(int,str(number_to_test))
	while number_to_test > n[0]:
		n=n[1:]+[sum(n)]
	if (number_to_test == n[0]) & (number_to_test>9):
		print ('-'*40)
		print('WORKER ID:'+ str( worker_id))
		print (str(number_to_test) + " is a Keith Number!")
		print ("PROOF:")
		n=map(int,str(number_to_test))
		while number_to_test > sum(n):
			print( str(n) + " = " + str(sum(n)))
			n=n[1:]+[sum(n)]
		print (str(n) + " = " + str(sum(n)))
		print ('-'*40)
		#print "press ENTER to continue"
		#raw_input()
		#time.sleep(1)
	return

def split_workload(num_of_chucks=4, low_int=0, high_int=1000):
	"""
	this function splits the workload into the given number of chucks
	returns: list of the chuck. Each chuck is a list contain 2 elements: [low_int, high_int]
	"""
	list_to_rtn = []
	chuck_size = high_int / num_of_chucks
	low_range = low_int
	for i in range(1,num_of_chucks+1):
		high_range = chuck_size * i
		list_to_rtn.append([low_range, high_range])
		low_range = high_range + 1
	return list_to_rtn
	

#this function is to get around the 32bit native int barrier
#not needed in 64 native systems
def my_xrange(start, stop, step):
	i = start
	while i < stop:
   			yield i
   			i += step

def test_range(the_range, worker_id=None):
	for x in my_xrange(the_range[0], the_range[1], 1):
		is_repfibdigit(x, worker_id)

if __name__=="__main__":
	num_of_workers = 4
	now = datetime.now()
	#test_range((1, 7913838))

	search_ranges = split_workload(num_of_chucks=num_of_workers, low_int=100000000, high_int=900000000)
	workers = []
	for i in range(num_of_workers):
		p = multiprocessing.Process(target=search_for_keith_number, args=(search_ranges[i], i))
		workers.append(p)
		p.start()

	for each_worker in workers:
		each_worker.join()

	runtime = datetime.now() - now
	print('Time:' + str(runtime))

