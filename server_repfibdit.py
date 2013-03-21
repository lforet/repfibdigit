# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import reactor, protocol
import cPickle as pickle
import time
import uuid
import numpy as np
import sys
import os
from itertools import groupby

global_block_size=4000000
global_num_of_blocks=100
SERVER = 'http://repfibdigit.isotope11.com'
PORT = 6666
last =  7000000000000000000000026042750000
global_block_start_time = time.time()

#		print "Work Unit completion time:", abs(nowtime - time.clock()) 

class Echo(protocol.Protocol):
	def __init__(self):
		self.last_number_checked = self.get_last_number_process()
		self.incompleted_count = 0
		self.block_size = global_block_size
		self.num_of_blocks = global_num_of_blocks
		self.SERVER = SERVER
		self.PORT = PORT
		self.work_units = None
		self.block_time = 0

	def dataReceived(self, data):
		print "CLIENT >>", data
		self.work_units = pickle.load( open( "work_units.p", "rb" ) )
                #print 'data received..press enter to load work units', self.work_units
                #raw_input()
		self.monitor_work_units()
		self.update_display()
		if len(data) > 1:
			if data[0] == 'f':
				pos = data.index('^')
				completed_uuid= data[(data.find("^")+1):]
				clientID  = data[(data.find(":")+1):pos]
				print "clientID=", clientID
				print 'work unit recieved from CLIENT >> ', completed_uuid
				#time.sleep(5)
				self.record_work_unit_completed(clientID, completed_uuid)
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
			#work_units = pickle.load( open( "work_units.p", "rb" ) )
			work_unit_index_to_return = 0
			# find_next_work_unit
			for index1,next_unit in enumerate(self.work_units):
				if next_unit[3] == False: break

			num_work_units = len(self.work_units)

			#count wu issued
			wu_issued = 0
			for i,next_unit in enumerate(self.work_units):
				if next_unit[3] == True: wu_issued = wu_issued +1
			if wu_issued == num_work_units:
				print "ALL work units issues in unit block"
				#check for all completed
				completed_count = 0
				issued_count = 0
				for index,next_unit in enumerate(self.work_units):
					if next_unit[4] == True: completed_count = completed_count + 1
					if next_unit[3] == True: issued_count = issued_count + 1
				#print "completed_count:", completed_count, "  issued_count:", issued_count 
				#IF DONT MATCH REISSUE non-completed work units
				if issued_count != completed_count:
					for index,next_unit in enumerate(self.work_units):
						if next_unit[3] == True and next_unit[4] == False:
							work_unit_index_to_return = index
							print "found unit issued but not completed...... reissuing unit", work_unit_index_to_return
							time.sleep(.2)
							#print work_units
							#raw_input()
							break
			else:
				self.work_units[index1][3] = True
				work_unit_index_to_return = index1
			#print "storing work units"
			pickle.dump(self.work_units, open( "work_units.p", "wb" ) )
			#print "returning:", work_units[work_unit_index_to_return]
			return self.work_units[work_unit_index_to_return]

	def record_work_unit_completed(self, clientID, uuid):
			#work_units = pickle.load( open( "work_units.p", "rb" ) )
			# find work unit with matching uuid
			for index,next_unit in enumerate(self.work_units):
				if next_unit[2] == uuid: break
			#mark_work_unit_as_completed
			self.work_units[index][4] = True
			self.work_units[index][5] = clientID
			pickle.dump(self.work_units, open( "work_units.p", "wb" ) )
			#return self.work_units[index]

	def dupli(self, the_list):
    		count = the_list.count # this optimization added courtesy of Sven's comment
    		result = [(item, count(item)) for item in set(the_list)]
    		result.sort()
    		return result


	def count_clients(self):
		#work_units = pickle.load( open( "work_units.p", "rb" ) )
		clients = []
		num_of_clients = 0
		for index,next_unit in enumerate(self.work_units):
			if next_unit[5] != None: clients.append(next_unit[5])
		clients_sorted = self.dupli(clients)
		return clients_sorted
	

	def monitor_work_units(self):
			#work_units = pickle.load( open( "work_units.p", "rb" ) )
			self.last_number_checked = int(self.get_last_number_process())

			#count incompleted units
			incompleted_count = 0
			not_issued_count = 0
			for index,next_unit in enumerate(self.work_units):
				if next_unit[4] == False: incompleted_count = incompleted_count + 1
				if next_unit[3] == False: not_issued_count = not_issued_count + 1
			#print "Incompleted Work Units:" , incompleted_count
			self.incompleted_count = incompleted_count
			if incompleted_count == 1: print self.work_units
			#if no incompleted units create new work block
			if incompleted_count == 0 and not_issued_count == 0: 
				largest_num = self.work_units[len(self.work_units)-1][1]
				#print 'largest_num:', largest_num
				#print 'press enter to create new work block'
				#time.sleep(1)
				#raw_input()
				self.save_last_number_process(largest_num)
				self.create_work_units(starting_num=largest_num, block_size=global_block_size, num_of_blocks=global_num_of_blocks)  

	def update_display(self):
		global global_block_start_time
		os.system("clear")
		self.block_time  = abs(global_block_start_time - time.time())
		web_page_end ='''
		</HTML>
		'''
		new_html_page = '''
		<HTML>
		<meta http-equiv="refresh" content="4" > 
		'''
		pgbreak = "-----------------------------------------------"
		webbreak = 	"---------------------------------------------------------------------------------------<br>"
		print pgbreak
		new_html_page = new_html_page + webbreak
		print "Last Block: ", self.last_number_checked
		new_html_page = new_html_page + "Last Block: " + str(self.last_number_checked)+ "<br>"
		print "Block Size: ", self.block_size
		new_html_page = new_html_page + "Block Size:  " + str(self.block_size) + "<br>"
		print "Units per Block: ", self.num_of_blocks
		new_html_page = new_html_page + "Units per Block:  " + str(self.num_of_blocks) + "<br>"
		print "Remaining Work Units:" , self.incompleted_count
		new_html_page = new_html_page + "Remaining Work Units: "+ str(self.num_of_blocks) + "/" + str(self.incompleted_count)+ "<br>"
		print "Time worked on current Block:", self.block_time
		new_html_page = new_html_page + "Time worked on current Block:" +  str(self.block_time) + "<br>"
		f = open('found_repfibdigits.txt', "r")
		print "KEITH NUMBERS:"
		new_html_page = new_html_page + "KEITH NUMBERS FOUND:" + "<br>"
		while True:
			line=f.readline()
			if not line: break
			print line  
			new_html_page = new_html_page + line +  "<br>"
		f.close() 
		
		client_count = self.count_clients()
		print "clientID:             # of Work Units completed: "
		new_html_page = new_html_page + "<br>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clientID:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Units completed: " + "<br>"
		print "-------------------------------------------------"
		new_html_page = new_html_page + webbreak
		for x in client_count:
			print x[0] , " .......  " , x[1]
			new_html_page = new_html_page + x[0] + " .......  " + str(x[1]) + "<br>"
		print "-------------------------------------------------"
		new_html_page = new_html_page + webbreak
		print "                          Total Active Clients: ", len(client_count)
		new_html_page = new_html_page + "Total Active Clients: " + str(len(client_count)) + "<br>"


		print; print "TRAFFIC:"
		print pgbreak
		new_html_page = new_html_page +  web_page_end
		f_handle = open('index.html', 'w')
		f_handle.write(str(new_html_page))
		f_handle.close()
		

	#work unit [lower_num, upper_num, uuid, issued, completed]
	def create_work_units(self, starting_num, block_size, num_of_blocks):
		global global_block_start_time
		print starting_num, block_size, num_of_blocks
		print "Creating New Work Unit Group"
		chunks = (block_size/num_of_blocks)
		#print "chunks:", chunks
		self.work_units =[]
		high = (starting_num + block_size)
		print starting_num, high, chunks
		for i in self.my_xrange(starting_num, high , chunks):
			the_range = [i, (i + chunks) ]
			#print the_range, the_range[0], the_range[1]
			#print "range:", the_range 
			self.work_units.append([the_range[0], the_range[1], str(uuid.uuid1()), False, False, None])
		pickle.dump(self.work_units, open( "work_units.p", "wb" ) )
		global_block_start_time = time.time()
		#print "new work block created", self.work_units
		#raw_input()
		#sys.exit(-1)
		#return

def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(PORT,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':

	#f = open('last_repfibdigit.txt', "r")
	#last_num = int(f.read())
	#f.close()
	#if last_num > 1:
	#	create_work_units(starting_num=last_num, block_size=global_block_size, num_of_blocks=global_num_of_blocks)
	main()

 
