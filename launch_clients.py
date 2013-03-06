import multiprocessing
import subprocess
import time
import os

cpus = multiprocessing.cpu_count()



proc = subprocess.Popen(["uname"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()

if out == "Linux\n":
	print "system is Linux"
proc = subprocess.Popen(["uname -i"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()

if out == 'i386\n':
	print "os system is 32bit"

if out == 'x86_64\n':
	print "os system is 64bit"
proc = subprocess.Popen(["uname -p"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
if out == 'x86_64\n' or out == 'i686':
	print "CPU is 64bit"
if out == 'i386':
	print "CPU is 32bit"

print "Number of CPU Detected:", cpus
print "Launching ", cpus, "workers in 5 seconds"
'''
timer = "."
for i in range(5):
	print timer
	timer = timer + timer
	time.sleep(1)
'''

'''
for i in range(cpus):
	#call(['gnome-terminal -e "python client_repfibdigit.py"'])
	print 'gnome-terminal -e "python client_repfibdigit.py"'
	os.system('nohup "python client_repfibdigit.py"')
	time.sleep(.5)


proc = subprocess.Popen(["uname", "-p"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
print "program output:", out
'''

os.system("python client_repfibdigit.py &")

time.sleep(3)

os.system('killall -9 python')
'''
p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()

for line in out.splitlines():
	if 'python' in line:
		print "kill pid:", line
		pid = int(line.split(None, 1)[0])
		os.kill(pid, signal.SIGKILL)
'''
