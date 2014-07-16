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



SERVER = 'http://repfibdigit.isotope11.com'
PORT = 6666
base_starting_number =  5752090994058710841670361653731519

last=0
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
				self.update_display()	

		if data == "n":
			#print self.issue_work_unit()
			work_unit_to_send = self.issue_work_unit()
			print "SERVER >>", work_unit_to_send 
			pickled_string = pickle.dumps(work_unit_to_send)
			self.transport.write(pickled_string)
			#self.transport.write("hi")


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
			self.work_units = pickle.load( open( "work_units.p", "rb" ) )
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
							print "All incomplete Work Units:"
							for index,next_unit in enumerate(self.work_units):
								if next_unit[4] == False: print "WU#: ", index, self.work_units[index]
							#could be issuing new work units here instead of waiting
							#time.sleep(3)
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
			#self.work_units = pickle.load( open( "work_units.p", "rb" ) )
			self.last_number_checked = int(self.get_last_number_process())
 			print "self.last_number_checked:", self.last_number_checked 
			#count incompleted units
			incompleted_count = 0
			not_issued_count = 0
			for index,next_unit in enumerate(self.work_units):
				if next_unit[4] == False: incompleted_count = incompleted_count + 1
				if next_unit[3] == False: not_issued_count = not_issued_count + 1
			#print "Incompleted Work Units:" , incompleted_count
			self.incompleted_count = incompleted_count
			#if incompleted_count == 1: print self.work_units
			#if no incompleted units create new work block
			if incompleted_count == 0 and not_issued_count == 0: 
				#print "loading work units"
				self.work_units = pickle.load( open( "work_units.p", "rb" ) )
				largest_num = self.work_units[len(self.work_units)-1][1]
				#print 'largest_num:', largest_num
				#print 'press enter to create new work block'
				#time.sleep(1)
				#raw_input()
				self.save_last_number_process(largest_num)
				create_work_units(starting_num=largest_num, block_size=global_block_size, num_of_blocks=global_num_of_blocks)  

	def update_display(self):
		global global_block_start_time
		os.system("clear")
		self.block_time  = abs(global_block_start_time - time.time())
		web_page_end ='''
		</HTML>
		'''
		new_html_page = '''
		<HTML>
		<meta http-equiv="refresh" content="5" > 
		'''
		pgbreak = "-----------------------------------------------"
		webbreak = 	"---------------------------------------------------------------------------------------<br>"
		print pgbreak
		new_html_page = new_html_page + webbreak
		print "Total Numbers Checked:",  (self.last_number_checked - base_starting_number)
		print numToWords((self.last_number_checked - base_starting_number))
		print
		new_html_page = new_html_page + "Total Numbers Checked:" + str((self.last_number_checked - base_starting_number))+ "<br>"
		new_html_page = new_html_page + numToWords((self.last_number_checked - base_starting_number)) + "<br>"
		print "Last Block: ", self.last_number_checked	
		new_html_page = new_html_page + "Last Block: " + str(self.last_number_checked)+ "<br>"
		print "Block Size: ", self.block_size
		new_html_page = new_html_page + "Block Size:  " + str(self.block_size) + "<br>"
		print "Units per Block: ", self.num_of_blocks
		new_html_page = new_html_page + "Units per Block:  " + str(self.num_of_blocks) + "<br>"
		print "Numbers per Work Unit: " , global_numbers_per_wu 
		new_html_page = new_html_page + "Numbers per Work Unit:" + str(global_numbers_per_wu ) + "<br>"
		print "Remaining Work Units:" , self.incompleted_count
		new_html_page = new_html_page + "Remaining Work Units: "+ str(self.num_of_blocks) + "/" + str(self.incompleted_count)+ "<br>"
		print "Time worked on current Block:", display_time(self.block_time)
		new_html_page = new_html_page + "Time worked on current Block:" +  display_time(self.block_time) + "<br>"

		completed_numbers = (self.num_of_blocks - self.incompleted_count) * global_numbers_per_wu 
		print "Completed numbers:", completed_numbers
		print "Incomplete numbers:", self.block_size - completed_numbers
		new_html_page = new_html_page + "Completed numbers:" +  str(completed_numbers) + "<br>"
		numbers_per_second = int (((completed_numbers / self.block_time) * 10000) ) / 10000
		print "Numbers per second:", numbers_per_second
		print numToWords(numbers_per_second)
		new_html_page = new_html_page + "Numbers per second:" +  str(numbers_per_second ) + "<br>"
		new_html_page = new_html_page + numToWords(numbers_per_second) + "<br>"
		print pgbreak
		try:
			print "Time Remaining:",  display_time(int ( (self.block_size - completed_numbers) / numbers_per_second))
			new_html_page = new_html_page + "Time Remaining:" + str(display_time(int ( (self.block_size - completed_numbers) / numbers_per_second))) + "<br>"
		except:
			pass
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
		#print "clientID:             # of Work Units completed: "
		#new_html_page = new_html_page + "<br>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clientID:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Units completed: " + "<br>"
		#print "-------------------------------------------------"
		#new_html_page = new_html_page + webbreak
		#for x in client_count:
		#	print x[0] , " .......  " , x[1]
		#	new_html_page = new_html_page + x[0] + " .......  " + str(x[1]) + "<br>"
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
#def create_work_units(self, starting_num, block_size, num_of_blocks):
def create_work_units( starting_num, block_size, num_of_blocks):
	global global_block_start_time
	print starting_num, block_size, num_of_blocks
	print "Creating New Work Unit Group"
	chunks = (block_size/num_of_blocks)
	#print "chunks:", chunks
	work_units =[]
	high = (starting_num + block_size)
	print starting_num, high, chunks
	for i in my_xrange(starting_num, high , chunks):
		the_range = [i, (i + chunks) ]
		#print the_range, the_range[0], the_range[1]
		#print "range:", the_range 
		work_units.append([the_range[0], the_range[1], str(uuid.uuid1()), False, False, None])
	pickle.dump(work_units, open( "work_units.p", "wb" ) )
	global_block_start_time = time.time()
	print "new work block created", work_units
	#raw_input()
	#sys.exit(-1)
	return

#this function is to get around the 32bit native int barrier
#not needed in 64 native systems
def my_xrange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step

intervals = (
    ('week', 604800),
    ('day', 86400),
    ('hours', 3600),
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])





def numToWords(num,join=True):
    '''words = {} convert an integer number into words'''
    units = ['','one','two','three','four','five','six','seven','eight','nine']
    teens = ['','eleven','twelve','thirteen','fourteen','fifteen','sixteen', \
             'seventeen','eighteen','nineteen']
    tens = ['','ten','twenty','thirty','forty','fifty','sixty','seventy', \
            'eighty','ninety']
    thousands = ['','thousand','million','billion','trillion','quadrillion', \
                 'quintillion','sextillion','septillion','octillion', \
                 'nonillion','decillion','undecillion','duodecillion', \
                 'tredecillion','quattuordecillion','sexdecillion', \
                 'septendecillion','octodecillion','novemdecillion', \
                 'vigintillion']
    words = []
    if num==0: words.append('zero')
    else:
        numStr = '%d'%num
        numStrLen = len(numStr)
        groups = (numStrLen+2)/3
        numStr = numStr.zfill(groups*3)
        for i in range(0,groups*3,3):
            h,t,u = int(numStr[i]),int(numStr[i+1]),int(numStr[i+2])
            g = groups-(i/3+1)
            if h>=1:
                words.append(units[h])
                words.append('hundred')
            if t>1:
                words.append(tens[t])
                if u>=1: words.append(units[u])
            elif t==1:
                if u>=1: words.append(teens[u])
                else: words.append(tens[t])
            else:
                if u>=1: words.append(units[u])
            if (g>=1) and ((h+t+u)>0): words.append(thousands[g]+',')
    if join: return ' '.join(words)
    return words

def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(PORT,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':

	global_block_size=100000000
	global_num_of_blocks=500
	

	if len(sys.argv) > 1:
		global_block_size=int(sys.argv[1])

	if len(sys.argv) > 2:
		global_num_of_blocks=int(sys.argv[2])

	global_numbers_per_wu = (global_block_size / global_num_of_blocks)

	try:
		print "loading work units"
		work_units = pickle.load( open( "work_units.p", "rb" ) )
	except:
		f = open('last_repfibdigit.txt', "r")
		starting_number = int(f.read())
		f.close()
		create_work_units(starting_num = starting_number , block_size=global_block_size, num_of_blocks=global_num_of_blocks)	


	#if len(sys.argv) > 1:
	#	starting_number = int(sys.argv[1])
	#	create_work_units(starting_num = starting_number , block_size=global_block_size, num_of_blocks=global_num_of_blocks)	

	
	#if last_num > 1:
		
	main()

 
