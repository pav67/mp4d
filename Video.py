#!/usr/bin/python
# coding: utf-8			

import Errors

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
		self.targetdir		= '/home/anais/videos'
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
				raise blexblex("Hash error : size")
			
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
			raise blexblex("Hash error : IO")
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
			
		#if subprocess.call("" % (), shell=True) != 0 :
		#	raise blexblex("Couldn't demux avi file")
		
		
		# 1.2) if video is a mkv file -> mkvextract (demux)
		elif ext == ".mkv":
			print("mkvextract tracks %s 0:%s 1:%s" % ( self.fullvideofile, self.fullvideofile, self.fullaudtmpfile ) )
			#if subprocess.call("" % (), shell=True) != 0 :
				#raise blexblex("Couldn't demux mkv file") 
		
		else :
			print("os.rename(%s, %s)" % ( self.fullvideofile, self.fullvideofile ))
			
		# 2) if audio is not aac -> ffmpeg (encode)
		if isAac() == False:
			print("ffmpeg -i %s -c:a libfaac -b:a 192k %s" % ( self.fullaudtmpfile, self.fullaudiofile ) )
			#if subprocess.call("" % (), shell=True) != 0 :
				#raise blexblex("Couldn't convert audio track")
		else:
			print("os.rename(%s, %s)" % ( self.fullaudtmpfile, self.fullaudiofile ) )

		# 3) MP4Box (mux)
		print("MP4Box -add %s -add %s -add %s %s" % ( self.fullaudiofile, self.fullvideofile, self.fullsubfile, '/'.join([self.path, self.target]) ) )
		#if subprocess.call("" % (), shell=True) != 0:
		#	raise blexblex("Couldn't build mp4 file")

		
		# 4) move movie file to video dir
		try:
			#os.rename(path+'/'+vid, '/home/paul/videos/'+vid)
			#os.remove(path+'/'+sub)  
			print("os.rename(%s, %s)" % ( '/'.join([self.path, self.target]), '/'.join([self.targetdir, self.target])))
			print("os.remove(%s)" % (self.fullsubfile))
			print("os.remove(%s)" % (self.fullaudiofile))
			print("os.remove(%s)" % (self.fullvideofile))
			print("os.remove(%s)" % (self.fullaudtmpfile))
		Except :
			raise blexblex("Error during file renaming / removing")
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------	
# Subdl method : downloads subtitles if the movie is not already in french 
#--------------------------------------------------------------------------------------------------	
	def subdl(self):
				
		# Connecting to the server
		server  = ServerProxy('http://api.opensubtitles.org/xml-rpc')
		session = server.LogIn('woutich', 'woutich', 'en', 'opensubtitles-download 1.0')
	
		if session['status'] != '200 OK':
			raise subtitleError("Login error")
	
		print("login OK")
		token = session['token']
	
		# Preparing xmlrpc request
		search = []
		search.append({'moviehash' : self.hash, 'moviebytesize' : str(self.size)})
		search.append({'query' : self.fullvideofile })
	
		# Subtitle search request
		sublist = server.SearchSubtitles(token, search)
		
		#print("data fetched %s" % (str(sublist)))
		if not sublist['data']:
			raise subtitleError("Subtitle not found")
			
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

		#print("sub_infos : %s" % (sub_infos['data']['language']))
		print("sub_infos : %s" % (sub_infos))


		if 'French' not in sub_infos['data']['language']:
			raise subtitleError("Movie is already in french")

		print("downloading subtitles")

		# Download subtitles
		sub_url		= sublist['data'][0]['SubDownloadLink']
		#if subprocess.call('wget -O - %s | gunzip > "%s/tmp.srt"' % (sub_url, self.path), shell=True) != 0
		#	raise blexblex("Download failed")
		
		
		#--------------------- for testing purposes -- to be deleted  --------
		tmp = "%s.gz" % (sub_url.split('.gz')[0])
		tmp2 = tmp.split('/')[-1]
		print ("suburl : %s -- %s" % (tmp, tmp2))
		
		if subprocess.call("curl -O %s" % (tmp), shell=True) not = 0:
			raise subtitleError("curl failed")
		if subprocess.call('cat %s | gunzip > "%s/tmp.srt"' % (tmp2, self.path), shell=True) not = 0:
			raise subtitleError("gunzip failed")
		#----------------------------------------------------------------------
		
							
		# Sanitizing film name
		tmpname 	= sub_infos['data']['title']
		valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
		self.name 	= ''.join(c for c in tmpname if c in valid_chars)
		self.target	= "%s/%s.mp4" % (self.path, self.name)
									
		# Loging out
		server.LogOut(token)
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------