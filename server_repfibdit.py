# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import reactor, protocol
import cPickle as pickle
import time
import uuid
import numpy as np

global_block_size=1000000
global_num_of_blocks=100
SERVER = 'isotope11.selfip.com'
PORT = 6666

class Echo(protocol.Protocol):
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
			work_unit_index_to_return = 0
			# find_next_work_unit
			for index1,next_unit in enumerate(work_units):
				if next_unit[3] == False: break
			#print "index:", index1+1, "  len(work_unit)", len(work_units)
			#if index1 == 8: 
			#	print "test: marking 4th wu as issued but not completed"
			#	work_units[3][4] = False
			#	print work_units[3][4] 
			#	print work_units
			#	raw_input()
			num_work_units = len(work_units)
			#print "index:", index1+1, "  len(work_unit)", len(work_units)
			#count wu issued
			wu_issued = 0
			for i,next_unit in enumerate(work_units):
				if next_unit[3] == True: wu_issued = wu_issued +1
			if wu_issued == num_work_units:
				print "ALL work units issues in unit block"
				#check for all completed
				completed_count = 0
				issued_count = 0
				for index,next_unit in enumerate(work_units):
					if next_unit[4] == True: completed_count = completed_count + 1
					if next_unit[3] == True: issued_count = issued_count + 1
				print "completed_count:", completed_count, "  issued_count:", issued_count 
				#IF DONT MATCH REISSUE non-completed work units
				if issued_count != completed_count:
					for index,next_unit in enumerate(work_units):
						if next_unit[3] == True and next_unit[4] == False:
							work_unit_index_to_return = index
							print "found unit issued but not completed sp reissuing unit", work_unit_index_to_return
							print work_units
							#raw_input()
							break
			else:
				work_units[index1][3] = True
				work_unit_index_to_return = index1
			#print "storing work units"
			pickle.dump(work_units, open( "work_units.p", "wb" ) )
			#print "returning:", work_units[work_unit_index_to_return]
			return work_units[work_unit_index_to_return]

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
			#print "last Num:", last_number	
			# count issued:
			
			# find_next_work_unit
			#print work_units
			#count incompleted units
			incompleted_count = 0
			not_issued_count = 0
			for index,next_unit in enumerate(work_units):
				if next_unit[4] == False: incompleted_count = incompleted_count + 1
				if next_unit[3] == False: not_issued_count = not_issued_count + 1
			print "Incompleted Work Units:" , incompleted_count
			if incompleted_count == 1: print work_units
			#if no incompleted units create new work block
			if incompleted_count == 0 and not_issued_count == 0: 
				largest_num = work_units[len(work_units)-1][1]
				#print 'largest_num:', largest_num
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
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(PORT,factory)
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

 
	
