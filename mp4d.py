#!/usr/bin/python
# coding: utf-8
import os, struct, subprocess, sys, time, atexit, signal, logging, string
import Daemon, Video, Errors
from xmlrpclib import ServerProxy


#--------------------------------------------------------------------------------------------------
# mp4d daemon : walks the target directory and looks for videos to make mp4
#--------------------------------------------------------------------------------------------------
class mp4d(Daemon):

	def run(self):
		while True:
			walk('/home/paul/encoding')
			time.sleep(100)
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# Walking the video directory, downloads sub and make mp4
#--------------------------------------------------------------------------------------------------
def walk(path):

	files = os.listdir(path)

	# For each file in the directory
	for f in files:

		if os.path.isdir('/'.join([path, f])):
			# If f is a directory, we need to walk it too
			walk('/'.join([path, f]))

		fn, ext = os.path.splitext(f)

		if ext in ['.avi', '.divx', '.xvid', '.mkv', '.mov', '.mp4']:

			print('film detecte : %s' % (f))
			vid = Video('/'.join([path, f]))

			# Downloading subtitles, and then building mp4 file
			try :
				vid.subdl()
			Except subtitleError:
				pass
			Except:
				raise blexblex("Subtitle download went wrong")
			
			vid.make()
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
# Main program
#--------------------------------------------------------------------------------------------------
if __name__ == '__main__':

	#logging.basicConfig(filename='subdl.log', level=print)
	walk('/Users/anais/Paul')
	#daemon = mp4d('/tmp/mp4d.pid')

	#if len(sys.argv) == 2:
	#	if 'start' == sys.argv[1]:
	#		daemon.start()
	#	elif 'stop' == sys.argv[1]:
	#		daemon.stop()
	#	elif 'restart' == sys.argv[1]:
	#		daemon.restart()
	#	else:
	#		print "Unknown command"
	#	sys.exit(0)
	#else:
	#	print "usage: %s start|stop|restart" % sys.argv[0]
	#   	exit(2)
#--------------------------------------------------------------------------------------------------