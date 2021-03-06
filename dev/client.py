#!/usr/bin/python
 
import socket              
import os
import time
import itertools
import cPickle as pickle
import numpy as np
import timeit
import uuid
import sys

########################################################################
import esky
from esky.util import appdir_from_executable

#python setup.py bdist_esky

def restart_this_app():
    appexe = appexe_from_executable(sys.executable)
    os.execv(appexe,[appexe] + sys.argv[1:])

def appexe_from_executable(exepath):
    appdir = appdir_from_executable(exepath)
    exename = os.path.basename(exepath)
    #  On OSX we might be in a bundle
    if sys.platform == "darwin":
        if os.path.isdir(os.path.join(appdir,"Contents","MacOS")):
            return os.path.join(appdir,"Contents","MacOS",exename)
    return os.path.join(appdir,exename)

def initialize_client():
	#handled auto-update stuff
	app = esky.Esky(sys.executable, "http://isotope11.selfip.com:8000")
	print "You are running Client version: %s" % app.active_version
	print "checking for client update..."
	time.sleep(2)
	if app.find_update() == None:
		print "no update available..."
		time.sleep(2)
	#print "Update available....", app.find_update(), app.active_version
	#raw_input()
	if app.find_update() != None:
		print "Update available....", app.find_update()
		print "SuperUser permission required to update..."
		if app.has_root() == False:
			 app.get_root()
		print "auto-updating..."
		try:
			app.auto_update()
		except Exception, e:
			print "ERROR UPDATING APP:", e
		app.reinitialize()
		print "restarting with new client..."
		time.sleep(3)
		restart_this_app()

########################################################################


if __name__=="__main__":

	initialize_client()

