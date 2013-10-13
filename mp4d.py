#!/usr/bin/python
# coding: utf-8
import os
import struct
import subprocess
import sys
import time
import atexit
import signal
import logging
import string
from xmlrpclib import ServerProxy

#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# Daemon class
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

class Daemon:

#--------------------------------------------------------------------------------------------------
# Class constructor
#--------------------------------------------------------------------------------------------------
	def __init__(self, pidfile): self.pidfile = pidfile
#--------------------------------------------------------------------------------------------------	

#--------------------------------------------------------------------------------------------------
# Daemonize function
#--------------------------------------------------------------------------------------------------
	def daemonize(self):
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError as err: 
			sys.stderr.write('fork #1 failed: {0}\n'.format(err))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir('/') 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:

				# exit from second parent
				sys.exit(0) 
		except OSError as err: 
			sys.stderr.write('fork #2 failed: {0}\n'.format(err))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(os.devnull, 'r')
		so = open(os.devnull, 'a+')
		se = open(os.devnull, 'a+')

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)

		pid = str(os.getpid())
		with open(self.pidfile,'w+') as f:
			f.write(pid + '\n')
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# Delpid function
#--------------------------------------------------------------------------------------------------	
	def delpid(self):
		os.remove(self.pidfile)
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# Start function
#--------------------------------------------------------------------------------------------------
	def start(self):

		# Check for a pidfile to see if the daemon already runs
		try:
			with open(self.pidfile,'r') as pf:

				pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile {0} already exist. " + \
					"Daemon already running?\n"
			sys.stderr.write(message.format(self.pidfile))
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# Stop function
#--------------------------------------------------------------------------------------------------
	def stop(self):

		# Get the pid from the pidfile
		try:
			with open(self.pidfile,'r') as pf:
				pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile {0} does not exist. " + \
					"Daemon not running?\n"
			sys.stderr.write(message.format(self.pidfile))
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError as err:
			e = str(err.args)
			if e.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print (str(err.args))
				sys.exit(1)
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# Restart function
#--------------------------------------------------------------------------------------------------
	def restart(self):
		self.stop()
		self.start()
#--------------------------------------------------------------------------------------------------
	
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# Mp4d class
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
class mp4d(Daemon):
#--------------------------------------------------------------------------------------------------
	def run(self):
		while True:
			walk('/home/paul/encoding')
			time.sleep(100)
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
			
			
			
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# Video class 
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

class Video:
	path			= None
	videofile		= None
	fullvideofile   = None
	targetdir		= None
	audiofile 		= None
	fullaudtmpfile	= None
	fullaudiofile	= None
	fullsubfile		= None
	name			= None
	target			= None
	hash			= None

#--------------------------------------------------------------------------------------------------
# Class constructor, _path is the video path
#--------------------------------------------------------------------------------------------------
	def __init__(self, _path):
		self.fullvideofile  = _path
		self.path			= os.path.dirname(_path)
		self.videofile		= os.path.basename(_path)
		self.targetdir		= '/home/paul/videos'
		self.hash			= self.hashit()
		self.size			= os.path.getsize(_path)
		self.fullaudiofile	= '/'.join([self.path, 'tmp.aac'])
		self.fullaudtmpfile	= '/'.join([self.path, 'tmp.aud'])
		self.fullvideofile	= '/'.join([self.path, 'tmp.vid'])
		self.fullsubfile	= '/'.join([self.path, 'tmp.srt'])
#--------------------------------------------------------------------------------------------------
		
#--------------------------------------------------------------------------------------------------	
# Make method : builds mp4 file with subtitles
#--------------------------------------------------------------------------------------------------	
	def hashit(self):
		try:
			longlongformat 	= 'Q' 
			bytesize 		= struct.calcsize(longlongformat)
			format 			= "<%d%s" % (65536//bytesize, longlongformat)
			
			f 				= open(self.fullvideofile, "rb")
			filesize 		= os.fstat(f.fileno()).st_size
			hash 			= filesize

			if filesize < 65536 * 2:
				hurt_me_plenty("Hash error : size")
			
			buffer 			= f.read(65536)
			longlongs 		= struct.unpack(format, buffer)
			hash 			+= sum(longlongs)

			f.seek(-65536, os.SEEK_END)
			buffer 			= f.read(65536)
			longlongs 		= struct.unpack(format, buffer)
			hash 			+= sum(longlongs)
			hash 			&= 0xFFFFFFFFFFFFFFFF

			f.close()
			returnedhash 	= "%016x" % hash

			print "[+] Hash ok : " + returnedhash
			return returnedhash

		except IOError:
			hurt_me_plenty("Hash error : IO")
#--------------------------------------------------------------------------------------------------

			
#--------------------------------------------------------------------------------------------------	
# Make method : builds mp4 file with subtitles
#--------------------------------------------------------------------------------------------------	
	def make(self):
		
		res = 0
		fn, ext = os.path.splitext(self.videofile)
		
		# 1.1) if video is an avi file -> MP4Box (demux)
		if ext == ".avi":
			print("MP4Box -aviraw video %s -out %s" % ( self.fullvideofile, self.fullvideofile ) )
			print("MP4Box -aviraw audio %s -out %s" % ( self.fullvideofile, self.fullaudtmpfile ) )
		# res += subprocess.call("" % (), shell=True)
		
		
		# 1.2) if video is a mkv file -> mkvextract (demux)
		elif ext == ".mkv":
			print("mkvextract tracks %s 0:%s 1:%s" % ( self.fullvideofile, self.fullvideofile, self.fullaudtmpfile ) )
			#if res == 0 :
				#res += subprocess.call("" % (), shell=True)
		
		else :
			print("os.rename(%s, %s)" % ( self.fullvideofile, self.fullvideofile ))
			
		# 2) if audio is not aac -> ffmpeg (encode)
		if isAac() == False:
			print("ffmpeg -i %s -c:a libfaac -b:a 192k %s" % ( self.fullaudtmpfile, self.fullaudiofile ) )
			#if res == 0 :
				#res += subprocess.call("" % (), shell=True)
		else:
			print("os.rename(%s, %s)" % ( self.fullaudtmpfile, self.fullaudiofile ) )

		# 3) MP4Box (mux)
		print("MP4Box -add %s -add %s -add %s %s" % ( self.fullaudiofile, self.fullvideofile, self.fullsubfile, '/'.join([self.path, self.target]) ) )
		# res += subprocess.call("" % (), shell=True)

		
		# 4) move movie file to video dir
		if res == 0:
			#os.rename(path+'/'+vid, '/home/paul/videos/'+vid)
			#os.remove(path+'/'+sub)  
			print("os.rename(%s, %s)" % ( '/'.join([self.path, self.target]), '/'.join([self.targetdir, self.target])))
			print("os.remove(%s)" % (self.fullsubfile))
			print("os.remove(%s)" % (self.fullaudiofile))
			print("os.remove(%s)" % (self.fullvideofile))
			print("os.remove(%s)" % (self.fullaudtmpfile))
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------	
# Subdl method : downloads subtitles if the movie is not already in french 
#--------------------------------------------------------------------------------------------------	
	def subdl(self):

		dlok  = False
			
		# Connecting to the server
		server  = ServerProxy('http://api.opensubtitles.org/xml-rpc')
		session = server.LogIn('woutich', 'woutich', 'en', 'opensubtitles-download 1.0')
	
		if session['status'] != '200 OK':
			hurt_me_plenty("Login error")
	
		print("login OK")
		token = session['token']
	
		# Preparing xmlrpc request
		search = []
		search.append({'moviehash' : self.hash, 'moviebytesize' : str(self.size)})
		search.append({'query' : self.fullvideofile })
	
		# Subtitle search request
		sublist = server.SearchSubtitles(token, search)
		
		#print("data fetched %s" % (str(sublist)))
		if sublist['data']:
			
			print("infos soustitres recuperees")
	
			# Sanitize strings to avoid parsing errors
			for item in sublist['data']:
				item['MovieName']   = item['MovieName'].strip('"')
				item['MovieName']   = item['MovieName'].strip("'")
				item['SubFileName'] = item['SubFileName'].strip('"')
				item['SubFileName'] = item['SubFileName'].strip("'")
	
			# Getting information about the movie
			sub_imdbid  = sublist['data'][0]['IDMovieImdb']
			sub_infos   = server.GetIMDBMovieDetails(token, sub_imdbid)
	
			print("sub_infos : %s" % (sub_infos['data']['language']))
	
			if 'French' not in sub_infos['data']['language']:
	
				print("downloading subtitles")
	
				# Download subtitles
				sub_url		= sublist['data'][0]['SubDownloadLink']
				op_download = subprocess.call('wget -O - %s | gunzip > "%s/tmp.srt"' % (sub_url, self.path), shell=True)
	
				print("op_download : %s" % (str(op_download)))
	
				if op_download == 0:
									
					# Sanitizing film name
					tmpname 	= sub_infos['data']['title']
					valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
					self.name 	= ''.join(c for c in tmpname if c in valid_chars)
					self.target	= "%s/%s.mp4" % (self.path, self.name)
										
					dlok = True
	
		# Loging out
		server.LogOut(token)
		return dlok
#--------------------------------------------------------------------------------------------------
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
			if vid.subdl() == True:
				vid.make()
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
# Error function
#--------------------------------------------------------------------------------------------------
def hurt_me_plenty(text):
	print("[!] " + text )
	exit(1)
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
# Main program
#--------------------------------------------------------------------------------------------------
if __name__ == '__main__':

	#logging.basicConfig(filename='subdl.log', level=print)
	walk('/Users/paul/Downloads')
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