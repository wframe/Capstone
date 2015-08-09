from scrapy.cmdline import execute
import os
from os import path

class Exec:         
	def __init__( self, newPath ):  
		self.savedPath = os.getcwd()
		os.chdir(newPath)
		execute(['scrapy', 'crawl', 'midiworld'])

	def __del__( self ):
		os.chdir(self.savedPath )

try:
	Exec(path.abspath('midispider'))
except:
	pass


