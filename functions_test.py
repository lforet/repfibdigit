#test functions

from twisted.internet import reactor, protocol
import cPickle as pickle
import time, datetime, uuid, sys, os
import multiprocessing
import platform



PORT = 6666

class client:
	def __init__(self):
		self.cpu_count = None
		self.hz = None
		self.brand = None
		self.guid = None
		self.started_at = None
		
class work_unit:
	def __init__(self, guid, created_at, start, end):
		self.guid = guid
		self.created_at = None
		self.completed_at = None
		self.start = start
		self.end = end
		self.time = None

class Repfibdigit_server(protocol.Protocol):
	def __init__(self, port, workunit_size):
		self.PORT = PORT
		self.start_time = datetime.datetime.now()
		self.up_time = datetime.datetime.now()
		self.workunit_size = workunit_size
		self.work_units = []


	#work unit [lower_num, upper_num, uuid, issued, completed]
	#def create_work_units(self, starting_num, block_size, num_of_blocks):
	def create_work_unit(self):
		print "Creating New Work Unit Group"
		ln = self.largest_number_worked()
		print ln
		wu = work_unit (str(uuid.uuid1()), datetime.datetime.now(), (ln+1) , (ln + self.workunit_size))
		print wu
		return wu

	#returns the largest number last worked
	def largest_number_worked(self):
		largest_num = 0
		for index,work_unit in enumerate(self.work_units):
			if work_unit.end > largest_num:
				largest_num = work_unit.end			
		return largest_num

repserver =  Repfibdigit_server(6666, 10000)

print repserver.work_units


repserver.work_units.append(repserver.create_work_unit())
repserver.work_units[0].end = 5000
repserver.work_units.append(repserver.create_work_unit())
repserver.work_units.append(repserver.create_work_unit())
repserver.work_units.append(repserver.create_work_unit())
repserver.work_units.append(repserver.create_work_unit())

for i in repserver.work_units:
	print i.guid, i.created_at, i.start, i.end, i.time

print "processor count:", multiprocessing.cpu_count()
print "cpu info:", platform.processor()

import pycpuinfo

client1 = client()
client1.cpu_count = pycpuinfo.get_cpu_info_from_proc_cpuinfo()['count']
client1.brand = pycpuinfo.get_cpu_info_from_proc_cpuinfo()['brand']
client1.hz = pycpuinfo.get_cpu_info_from_proc_cpuinfo()['hz']

print "client1.cpu_count ", client1.cpu_count 
print "client1.brand ", client1.brand
print "client1.hz ", client1.hz

#info = pycpuinfo.get_cpu_info_from_proc_cpuinfo()
#print pycpuinfo.get_cpu_info_from_proc_cpuinfo()['vendor_id']

#print('Vendor ID', info['vendor_id'])
#print('Brand', info['brand'])
#print('Arch', info['arch'])
#print('Bits', info['bits'])
#print('Count', info['count'])
#print('Flags:', info['flags'])


