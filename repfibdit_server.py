# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet import reactor, protocol


class Echo(protocol.Protocol):
	"""This is just about the simplest possible protocol"""

	def dataReceived(self, data):
		print "CLIENT >>", data
		if len(data) > 1:
			num = data[(data.find(":")+1):]
			f = open('found_repfibdigits.txt', "a")
			f.write(num)
			f.close()

		if data == "n":
			new_num = self.new_number()
			print "SERVER >>", new_num
			self.transport.write(new_num)
		else:
			print "SERVER >>", data
			self.transport.write(data)	
	
	def new_number(self):
		f = open('next_repfibdigit.txt', "r")
		data = f.read()
		f.close()
		return data


def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
