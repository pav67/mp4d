#!/usr/bin/python
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


class Daemon:
	"""A generic daemon class.

	Usage: subclass the daemon class and override the run() method."""

	def __init__(self, pidfile): self.pidfile = pidfile
	
	def daemonize(self):
		"""Deamonize class. UNIX double fork mechanism."""

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
	
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""Start the daemon."""

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

	def stop(self):
		"""Stop the daemon."""

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

	def restart(self):
		"""Restart the daemon."""
		self.stop()
		self.start()

	def run(self):
		"""You should override this method when you subclass Daemon.
		
		It will be called after the process has been daemonized by 
		start() or restart()."""



class mp4d(Daemon):
	def run(self):
		while True:
			walk('/home/paul/encoding')
			time.sleep(100)

def walk(path):
        files = os.listdir(path)
        for f in files:
                if os.path.isdir(path+'/'+f):
                        walk(path+'/'+f)
                fn, ext = os.path.splitext(f)
                if ext in ['.avi', '.divx', '.xvid', '.mkv', '.mov', '.mp4']:
			logging.debug('film detecte')
                	sub, name = subdl(path+'/'+f)
			if None not in [sub, name]:
				logging.debug("le dl des soustitres s'est bien passe")
				vid = encode(path+'/'+f, path+'/'+sub, name)
				logging.debug("encode(%s, %s, %s)" %(path+'/'+f, path+'/'+sub, name))
				if vid != None:
					#os.rename(path+'/'+vid, '/home/paul/videos/'+vid)
					#os.remove(path+'/'+sub)  
					logging.debug("os.rename(%s,%s)" % (path+'/'+vid,'/home/paul/videos/'+vid ))
					logging.debug("os.remove(%s)" % (path+'/'+sub))
                else:  
                       	#os.remove(path+'/'+f)
			logging.debug("os.remove(%s)" % (path+'/'+f))


def hurt_me_plenty(text):
        logging.debug("[!] " + text )
        exit(1)

def hashFile(path):

        try:

                longlongformat = 'Q' 
                bytesize = struct.calcsize(longlongformat)
                format = "<%d%s" % (65536//bytesize, longlongformat)
                
                f = open(path, "rb")
                filesize = os.fstat(f.fileno()).st_size
                hash = filesize

                if filesize < 65536 * 2:
                        hurt_me_plenty("Hash error : size")
                buffer = f.read(65536)
                longlongs = struct.unpack(format, buffer)
                hash += sum(longlongs)
                
                f.seek(-65536, os.SEEK_END)
                buffer = f.read(65536)
                longlongs = struct.unpack(format, buffer)
                hash += sum(longlongs)
                hash &= 0xFFFFFFFFFFFFFFFF
                
                f.close()
                returnedhash = "%016x" % hash
		logging.debug("hash : %s" % (returnedhash))
                return returnedhash

        except IOError:
                hurt_me_plenty("Hash error : IO")

def subdl(path):

	sub  = None
	name = None
	logging.debug("subdl(%s)" % (path))

        # Connecting to the server
        server  = ServerProxy('http://api.opensubtitles.org/xml-rpc')
        session = server.LogIn('woutich', 'woutich', 'en', 'opensubtitles-download 1.0')

        if session['status'] != '200 OK':
                hurt_me_plenty("Login error")

        logging.debug("login OK")
	token = session['token']
	
        # Computing movie file hash
        moviehash = hashFile(path)
        moviesize = os.path.getsize(path)

        # Preparing xmlrpc request
        search = []
        search.append({'moviehash' : moviehash, 'moviebytesize' : str(moviesize)})
	search.append({'query' : path})

        # Subtitle search request
        sublist = server.SearchSubtitles(token, search)
	
	#logging.debug("data fetched %s" % (str(sublist)))
        if sublist['data']:
		
		logging.debug("infos soustitres recuperees")

                # Sanitize strings to avoid parsing errors
                for item in sublist['data']:
                        item['MovieName']   = item['MovieName'].strip('"')
                        item['MovieName']   = item['MovieName'].strip("'")
                        item['SubFileName'] = item['SubFileName'].strip('"')
                        item['SubFileName'] = item['SubFileName'].strip("'")

                # Getting information about the movie
                sub_imdbid  = sublist['data'][0]['IDMovieImdb']
                sub_infos   = server.GetIMDBMovieDetails(token, sub_imdbid)
                isfrench    = False

		logging.debug("sub_infos : %s" % (sub_infos['data']['language']))

                if 'French' in sub_infos['data']['language']:
			logging.debug('le film est francais, pas besoin de soustitres')
                        isfrench = True

                if isfrench == False:

                	logging.debug("downloading subtitles")

			# Download subtitles
                        sub_dir     = os.path.dirname(path)
                        sub_url     = sublist['data'][0]['SubDownloadLink']
                        sub_file    = os.path.basename(path)[:-3] + sublist['data'][0]['SubFileName'][-3:]
                        op_download = subprocess.call('wget -O - ' + sub_url + ' | gunzip > "' + sub_dir + '/' + sub_file+ '"', shell=True)

			logging.debug("op_download : %s" % (str(op_download)))

			if op_download == 0:
				sub = sub_file
				logging.debug("sub_file : %s" % (sub_file))
				
				# Sanitizing film name
				tmpname = sub_infos['data']['title']
				valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
				name = ''.join(c for c in tmpname if c in valid_chars)
				logging.debug('subtitle bien dl %s pour le film %s' % (sub,name))

        # Loging out
        server.LogOut(token)
	logging.debug("sortie de subdl : ['%s', '%s']" % (sub, name))
	return [sub, name]

#def mkvmerge(path, subtitles, name):

#	logging.debug("appel mkvmerge(%s, %s, %s)" % (path, subtitles, name))
#	output = None
	
#	dirname = os.path.dirname(path)
#	mkvfile = name + '.mkv'

#	logging.debug('mkvmerge -o "%s" "%s" "%s"' % (dirname+'/'+mkvfile, path, subtitles))

#	op_merge = subprocess.call('mkvmerge -o "%s" "%s" "%s"' % (dirname+'/'+mkvfile, path, subtitles), shell=True)
#
#	if op_merge == 0:
#		logging.debug("mkv bien merge : %s" % (mkvfile))
#		output = mkvfile
	
#	logging.debug("sortie de mkvmerge : %s" % (output))
#	return output

def encode(path, subtitles, name):
	print "todo"

if __name__ == '__main__':

	logging.basicConfig(filename='subdl.log', level=logging.DEBUG)

	daemon = mp4d('/tmp/mp4d.pid')

	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
        	exit(2)
