#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function

"""unbork.py: Filename fixer"""
__version__   = "1.1"
__author__    = "ed <irc.rizon.net>"
__license__   = "MIT"
__copyright__ = 2015

import base64
import zlib
import json
import sys
import os
import re

try:
    from urllib import unquote
except:
    from urllib.parse import unquote

enc_py26 = 'eJxdkttyhCAMht/F615wBp+l02GUusrqHkZ0ZtunLwvJmu0N//eHhIDxs+lSiLH5aPo4apBpTiFlDncmbVElVFXwmrGiFry1uqjTDFSAYtyA1nxnIM9wUMg3ElSBQr2BetNWtbAPfVtZ61tV91u4B2fMAAgArmBL6BdwBIEgERSCRjAIFsFlGPbgz3eEmLxgTB32wQSXYOc1w9gLyUWBuazcMfm80PSbl5hugglRTzyM5+9W/LO1JYnIdzs8NhIo91i6LV7xXOd0i4cWloQVYU3YELaEHeGWMGfU0A6ctuC0B382Od+mrs8636LzK8Ke4dIFH37WuCwxgB3XYZiBYxiW7voNrrxYgFlvl+4KvO3rHNOU3X3Lcy2jT1M8bc8BUsYP/QrgdPft5MufWMH3w8ELcnlLhSMh8yvBgjpUn+LYfP0Bd0QChw=='

enc_py27 = 'eJxdkt1ygyAQRt/F617wDz5Lp+MoNUo0MSM6k/bpi7AbN73xnA9wF8TPqo0+hOqj6sKgAeMUfUzuH0zaTCVUIWTNWKYVQBi3Vmc6zYACiOMGaIGu0MB6w4HwnpFABYQ6BuqYutDCPPSvZXm/VmW+hv1wxgyIAOEKpoR+CUcRKBJFoWgUg2JRjjP1u2+uD5QQG8GYOuOTCS4hTmuSoROSiyxTfnLH5LGh8Tc9QlwEE6JUPEPD36P4F0tLMiLfY//cyEDex9xu4Y51ndM1Fs0uiSvimrghbok74jVxzmignTltx2k/Thvyo+N1GdsucVqCa1aUPcmt9Y3/WcM8Bw9xWPt+Ag++n9v7N6R8fAFhXW7tHXzb1ynEMaXHli45/wdxDJftuE3q+NVfA3jV+3Zp8m9ZpOn602f0fJYi54LkrwUW6JBNDEP19Qcj/gml'

def zenc(lst):
    return base64.b64encode(zlib.compress(json.dumps(lst, separators=(',',':'))))

def zdec(b64):
    return json.loads(zlib.decompress(base64.b64decode(b64)).decode())

if sys.version_info.major == 2 and sys.version_info.minor == 6:
    codecs = zdec(enc_py26)
else:
    codecs = zdec(enc_py27)

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
            fixed = unquote(name)
        elif cfg.mode == Modes.VIA:
            try:
                reg = cfg.via.search(name)
                if not reg:
                    continue

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
        
        print('({0}) => (\x1b[1;32m{1}\x1b[0m) '.format(
            sanitize(name, True), fixed), end='')
        ch = getch()
        print(ch)
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
        path = os.path.join(folder, subfolder)
        if os.path.isdir(path):
            print("Entering [" + sanitize(path, True) + "]")
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
    print(cs)

# Check if mode 3 (detect)
elif len(sys.argv) == 4 and sys.argv[1] == 'find':
    hits = 0
    for via in codecs:
        try:
            tmp = sys.argv[2].decode('utf-8').encode(via)
        except:
            continue

        for enc in codecs:
            try:
                tmp2 = tmp.decode(enc).encode('utf-8')
                if tmp2 == sys.argv[3]:
                    print('%s \x1b[1;31m%s\x1b[0m via \x1b[1;32m%s\x1b[0m' % (sys.argv[0], enc, via,))
                    hits += 1
            except:
                pass
    print('Detection complete, found %d possible fixes' % (hits,))
    sys.exit(0)

else:
    print()
    print('\x1b[0;33mUsage:\x1b[0m')
    print('   unbork.py url')
    print('   unbork.py ENCODING via ENCODING')
    print('   unbork.by find \'BROKEN\' \'GOOD\'')
    print()
    print('\x1b[0;33mExample 1:\x1b[0m')
    print('   URL-escaped UTF-8, looks like this in ls:')
    print('   ?%81%8b?%81%88?%82%8a?%81??%81%a1.mp3')
    print()
    print('   \x1b[1m{0} url\x1b[0m'.format(sys.argv[0],))
    print('   (\x1b[1;31m81%8b81%8882%8a81▒81%a1.mp3\x1b[0m) => (\x1b[1;32mかえりみち.mp3\x1b[0m)')
    print()
    print('\x1b[0;33mExample 2:\x1b[0m')
    print('   SJIS (cp932) parsed as MSDOS (cp437) looks like...')
    print('   ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3')
    print()
    print('   \x1b[1m{0} cp932 via cp437\x1b[0m'.format(sys.argv[0],))
    print('   (\x1b[1;31mëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3\x1b[0m) => (\x1b[1;32m宇多田ヒカル - 桜流し.mp3\x1b[0m)')
    print()
    print('\x1b[0;33mExample 3:\x1b[0m')
    print('   Find a correction method from BROKEN to GOOD')
    print()
    print('   \x1b[1m{0} find \'УпРlЙ╣Кy\' \'同人音楽\'\x1b[0m'.format(sys.argv[0],))
    print('      .../unbork.py \x1b[1;31mcp932\x1b[0m via \x1b[1;32mcp866\x1b[0m ...')
    print('      Detection complete, found 4 possible fixes')
    sys.exit(1)



print()
print("Listing files. For each file, select [Y]es [N]o [Q]uit.")
print()
iterate(cfg, os.getcwd())
print('done')

