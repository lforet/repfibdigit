from twisted.internet import reactor, protocol
import cPickle as pickle
import time, datetime, uuid, sys, os


PORT = 6666

class work_unit:
	def __init__(self, guid, created_at, start, end, time):
		self.guid = guid
		self.created_at = created_at
		self.start = start
		self.end = end
		self.time = time

class Repfibdigit_server(protocol.Protocol):
	def __init__(self, port, workunit_size):
		self.PORT = PORT
		self.start_time = datetime.datetime.now()
		self.up_time = datetime.datetime.now()
		self.workunit_size = workunit_size
		self.work_units = []


	def dataReceived(self, data):
		#data is received by server
		#determine msg type
		#msg marked as completed work unit
		if data[0] == 'f':
			pos = data.index('^')
			completed_uuid= data[(data.find("^")+1):]
			clientID  = data[(data.find(":")+1):pos]
			print "clientID=", clientID
			print 'work unit recieved from CLIENT >> ', completed_uuid
			#time.sleep(5)
			self.record_work_unit_completed(clientID, completed_uuid)
			self.transport.write('work recorded')	

		#msg marked as Keith Number
		if data[0] == 'k':
			num = data[(data.find(":")+1):]
			f = open('found_repfibdigits.txt', "a")
			f.write(num)
			f.write('\n')
			f.close()
			self.transport.write('keith num record')
			self.update_display()	

		#client needs work unit
		if data == "n":
			#print self.issue_work_unit()
			work_unit_to_send = self.issue_work_unit()
			print "SERVER >>", work_unit_to_send 
			pickled_string = pickle.dumps(work_unit_to_send)
			self.transport.write(pickled_string)
			#self.transport.write("hi")


	def update_time(self):
			self.up_time  = self.start_time - datetime.today() 


	#work unit [lower_num, upper_num, uuid, issued, completed]
	#def create_work_units(self, starting_num, block_size, num_of_blocks):
	def create_work_unit(self):
		print "Creating New Work Unit Group"
		ln = self.largest_number_worked()
		print ln
		wu = work_unit (str(uuid.uuid1()), datetime.datetime.now(), (ln+1) , (ln + self.workunit_size), 0)
		print wu
		return wu

	#returns the largest number last worked
	def largest_number_worked(self):
		largest_num = 0
		for index,work_unit in enumerate(self.work_units):
			if work_unit.end > largest_num:
				largest_num = work_unit.end			
		return largest_num






