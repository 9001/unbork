#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""unbork.py: Filename fixer"""
__version__   = "1.0"
__author__    = "ed <irc.rizon.net>"
__license__   = "MIT"
__copyright__ = 2015

import urllib
import sys
import os
import re

# Cross-platform read single key
def find_getch():
	try:
		import termios
	except ImportError:
		import msvcrt
		return msvcrt.getch
	
	import sys, tty
	def getch_impl():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch
	return getch_impl

getch = find_getch()

# Config object
class Config:
	mode = None
	via = None

def enum(**enums):
	return type('Enum', (), enums)

Modes = enum(URL=1, VIA=2)

# Remove ANSI escape codes and newlines
# Optionally hilight changes when displaying on a VT100 term
def sanitize(txt, for_print=False):
	pre = suf = ''
	if for_print:
		pre = "\x1b[1;31m"
		suf = "\x1b[0m"
	txt = txt.replace("\x1b", pre + '<ESC>' + suf)
	txt = txt.replace("\x0d", pre + '<CR>'  + suf)
	txt = txt.replace("\x0a", pre + '<LF>'  + suf)
	return txt

# Iterate through a folder and find files to rename
def rename(cfg, folder):
	for name in os.listdir(folder):
		if cfg.mode == Modes.URL:
			fixed = urllib.unquote(name)
		elif cfg.mode == Modes.VIA:
			try:
				reg = cfg.via.search(name)
				if not reg:
					#print 'Skip   ' + sanitize(name, True)
					continue
				#print reg.groups()
				#print 'Decode ' + sanitize(name, True)
				fixed = name\
					.decode('utf-8')\
					.encode(via)\
					.decode(enc)\
					.encode('utf-8')
			except:
				continue
		else:
			raise Exception('Unknown conversion mode [%s]' % cfg.mode)
		
		fixed = sanitize(fixed)
		if fixed == name:
			continue
		
		print '(' + sanitize(name, True) + ') => (\x1b[1;32m' + fixed + '\x1b[0m) ',
		ch = getch()
		print ch
		if ch == 'y':
			path_from = os.path.join(folder, name)
			path_to   = os.path.join(folder, fixed)
			os.rename(path_from, path_to)
		if ch == 'q':
			sys.exit(0)

# Recursively traverse a folder
def iterate(cfg, folder):
	rename(cfg, folder)
	for subfolder in os.listdir(folder):
		if os.path.isdir(subfolder):
			path = os.path.join(folder, subfolder)
			print "Entering [" + sanitize(path, True) + "]"
			iterate(cfg, path)

cfg = Config()

# Check if mode 1 (url)
if len(sys.argv) == 2 and sys.argv[1] == 'url':
	cfg.mode = Modes.URL

# Check if mode 2 (via)
elif len(sys.argv) == 4 and sys.argv[2] == 'via':
	cfg.mode = Modes.VIA
	enc = sys.argv[1]
	via = sys.argv[3]
	cs = ''
	for a in range(128, 255):
		cs += chr(a)
	cs = cs.decode(via).encode('utf8')
	cs = '([' + cs + ']{3}|(?:[' + cs + '].){2})'
	cfg.via = re.compile(cs, flags=re.U)
	print cs

else:
	print
	print '\x1b[0;33mUsage:\x1b[0m'
	print '   unbork.py url'
	print '   unbork.py ENCODING via ENCODING'
	print
	print '\x1b[0;33mExample 1:\x1b[0m'
	print '   URL-escaped UTF-8, looks like this in ls:'
	print '   ?%81%8b?%81%88?%82%8a?%81??%81%a1.mp3'
	print
	print '   \x1b[1munbork.py url\x1b[0m'
	print '   (\x1b[1;31m81%8b81%8882%8a81▒81%a1.mp3\x1b[0m) => (\x1b[1;32mかえりみち.mp3\x1b[0m)'
	print
	print '\x1b[0;33mExample 2:\x1b[0m'
	print '   SJIS (cp932) parsed as MSDOS (cp437) looks like...'
	print '   ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3'
	print
	print '   \x1b[1munbork.py cp932 via cp437\x1b[0m'
	print '   (\x1b[1;31mëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3\x1b[0m) => (\x1b[1;32m宇多田ヒカル - 桜流し.mp3\x1b[0m)'
	sys.exit(1)



print
print "Listing files. For each file, select [Y]es [N]o [Q]uit."
print
iterate(cfg, os.getcwd())
print 'done'
