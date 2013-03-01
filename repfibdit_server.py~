# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import reactor, protocol
import cPickle as pickle
import time
import uuid
import numpy as np

class Echo(protocol.Protocol):
	"""This is just about the simplest possible protocol"""

	def dataReceived(self, data):
		print "CLIENT >>", data
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
	
	def save_last_number_process(self, num):
		f = open('last_repfibdigit.txt', "w")
		f.write(num)
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
			last_number_process(self, num):
			# find_next_work_unit
			uncompleted_count = 0
			for index,next_unit in enumerate(work_units):
				if next_unit[4] == False: uncompleted_count = uncompleted_count + 1
			print "Work Units Not completed:", uncompleted_count
			if uncompleted_count == 0: 
				create_work_units(starting_num=work_units[len(work_units)][1], block_size=10000, num_of_blocks=10)
			pickle.dump(work_units, open( "work_units.p", "wb" ) )
			return work_units[index]	


#work unit [lower_num, upper_num, uuid, issued, completed]
def create_work_units(starting_num, block_size, num_of_blocks):
	#f = open('next_repfibdigit.txt', "r+")
	#f.write(str(num))
	#f.close()
	chunks = (block_size/num_of_blocks)
	work_units =[]
	for i in xrange(starting_num, block_size, chunks):
		the_range = [i, ((i + chunks)-1) ]
		#print the_range, the_range[0], the_range[1]
		print "range:", the_range 
		work_units.append([the_range[0], the_range[1], str(uuid.uuid1()), False, False])
		
	return work_units

def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
	units = create_work_units(starting_num=1, block_size=10000, num_of_blocks=10)
	print units
	pickle.dump(units, open( "work_units.p", "wb" ) )
	main()


	#print issue_work_unit()
	#print issue_work_unit()

	#units[2][2] = True
	#pickle.dump(units, open( "work_units.p", "wb" ) )
	#print issue_work_unit()
 
	
