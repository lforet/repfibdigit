import multiprocessing
from subprocess import call
import time
import os

cpus = multiprocessing.cpu_count()

print "Number of CPU Detected:", cpus
print "Launching ", cpus, "workers in 5 seconds"

timer = "."
for i in range(5):
	print timer
	timer = timer + timer
	time.sleep(1)

for i in range(cpus):
	#call(['gnome-terminal -e "python client_repfibdigit.py"'])
	print 'gnome-terminal -e "python client_repfibdigit.py"'
	os.system('gnome-terminal -e "python client_repfibdigit.py"')
	time.sleep(.2)

