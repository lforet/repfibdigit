# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import reactor, protocol
import cPickle as pickle
import time
import uuid
import numpy as np

global_block_size=1000000
global_num_of_blocks=100

class Echo(protocol.Protocol):
	"""This is just about the simplest possible protocol"""

	def dataReceived(self, data):
		print "CLIENT >>", data
		self.monitor_work_units()
		if len(data) > 1:
			if data[0] == 'f':
				completed_uuid = data[(data.find(":")+1):]
				print 'work unit recieved from CLIENT >> ', completed_uuid
				self.record_work_unit_completed(completed_uuid)
				self.transport.write('work recorded')	
			if data[0] == 'k':
				num = data[(data.find(":")+1):]
				f = open('found_repfibdigits.txt', "a")
				f.write(num)
				f.write('\n')
				f.close()
				self.transport.write('keith num record')

		if data == "n":
			#print self.issue_work_unit()
			work_unit_to_send = self.issue_work_unit()
			print "SERVER >>", work_unit_to_send 
			pickled_string = pickle.dumps(work_unit_to_send)
			self.transport.write(pickled_string)
		#else:
		#	print "SERVER >>", data
		#	self.transport.write(data)
	
	#this function is to get around the 32bit native int barrier
	#not needed in 64 native systems
	def my_xrange(self,start, stop, step):
		i = start
		while i < stop:
			yield i
			i += step

	def save_last_number_process(self, num):
		f = open('last_repfibdigit.txt', "w")
		f.write(str(num))
		f.close()

	def get_last_number_process(self):
		f = open('last_repfibdigit.txt', "r")
		data = f.read()
		f.close()
		return data

	def issue_work_unit(self):
			work_units = pickle.load( open( "work_units.p", "rb" ) )
			# find_next_work_unit
			for index,next_unit in enumerate(work_units):
				if next_unit[3] == False: break
			#print "next:", work_units[index]
			#mark_work_unit_as_issued(work_units)
			work_units[index][3] = True
			pickle.dump(work_units, open( "work_units.p", "wb" ) )
			return work_units[index]

	def record_work_unit_completed(self, uuid):
			work_units = pickle.load( open( "work_units.p", "rb" ) )
			# find work unit with matching uuid
			for index,next_unit in enumerate(work_units):
				if next_unit[2] == uuid: break
			#mark_work_unit_as_completed
			work_units[index][4] = True
			pickle.dump(work_units, open( "work_units.p", "wb" ) )
			return work_units[index]
			
	def monitor_work_units(self):
			work_units = pickle.load( open( "work_units.p", "rb" ) )
			last_number = int(self.get_last_number_process())
			print "last Num:", last_number	
			# find_next_work_unit
			#print work_units
			incompleted_count = 0
			for index,next_unit in enumerate(work_units):
				if next_unit[4] == False: incompleted_count = incompleted_count + 1
			print "Incompleted Work Units:" , incompleted_count
			if incompleted_count == 0: 
				largest_num = work_units[len(work_units)-1][1]
				print 'largest_num:', largest_num
				self.save_last_number_process(largest_num)
				self.create_work_units(starting_num=largest_num, block_size=global_block_size, num_of_blocks=global_num_of_blocks)  


	#work unit [lower_num, upper_num, uuid, issued, completed]
	def create_work_units(self, starting_num, block_size, num_of_blocks):
		print starting_num, block_size, num_of_blocks
		print "Creating New Work Unit Group"
		chunks = (block_size/num_of_blocks)
		#print "chunks:", chunks
		work_units =[]
		high = (starting_num + block_size)
		print starting_num, high, chunks
		for i in self.my_xrange(starting_num, high , chunks):
			the_range = [i, (i + chunks) ]
			print the_range, the_range[0], the_range[1]
			#print "range:", the_range 
			work_units.append([the_range[0], the_range[1], str(uuid.uuid1()), False, False])
		pickle.dump(work_units, open( "work_units.p", "wb" ) )
		print work_units
		#sys.exit(-1)
		return

#this function is to get around the 32bit native int barrier
#not needed in 64 native systems
def my_xrange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step



#work unit [lower_num, upper_num, uuid, issued, completed]
def create_work_units(starting_num, block_size, num_of_blocks):
	print starting_num, block_size, num_of_blocks
	print "Creating New Work Unit Group"
	chunks = (block_size/num_of_blocks)
	#print "chunks:", chunks
	work_units =[]
	for i in my_xrange(starting_num, (starting_num + block_size), chunks):
		the_range = [i, (i + chunks) ]
		print the_range, the_range[0], the_range[1]
		#print "range:", the_range 
		work_units.append([the_range[0], the_range[1], str(uuid.uuid1()), False, False])
	pickle.dump(work_units, open( "work_units.p", "wb" ) )
	print work_units
	#sys.exit(-1)
	return





def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
	
	f = open('last_repfibdigit.txt', "r")
	last_num = int(f.read())
	f.close()
	if last_num == 1:
		create_work_units(starting_num=1, block_size=global_block_size, num_of_blocks=global_num_of_blocks)
	if last_num > 1:
		create_work_units(starting_num=last_num, block_size=global_block_size, num_of_blocks=global_num_of_blocks)

	main()


	#print issue_work_unit()
	#print issue_work_unit()

	#units[2][2] = True
	#pickle.dump(units, open( "work_units.p", "wb" ) )
	#print issue_work_unit()
 
	
