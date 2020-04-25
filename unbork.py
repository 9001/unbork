#!/usr/bin/env python2
# coding: utf-8
from __future__ import print_function, unicode_literals

"""unbork.py: Filename fixer"""
__version__ = "1.2"
__author__ = "ed <irc.rizon.net>"
__license__ = "MIT"
__copyright__ = 2015

import struct
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


PY2 = sys.version_info.major == 2


# python doesn't provide a list of available encodings so here it is
enc_py26 = "eJxdkttyhCAMht/F615wBp+l02GUusrqHkZ0ZtunLwvJmu0N//eHhIDxs+lSiLH5aPo4apBpTiFlDncmbVElVFXwmrGiFry1uqjTDFSAYtyA1nxnIM9wUMg3ElSBQr2BetNWtbAPfVtZ61tV91u4B2fMAAgArmBL6BdwBIEgERSCRjAIFsFlGPbgz3eEmLxgTB32wQSXYOc1w9gLyUWBuazcMfm80PSbl5hugglRTzyM5+9W/LO1JYnIdzs8NhIo91i6LV7xXOd0i4cWloQVYU3YELaEHeGWMGfU0A6ctuC0B382Od+mrs8636LzK8Ke4dIFH37WuCwxgB3XYZiBYxiW7voNrrxYgFlvl+4KvO3rHNOU3X3Lcy2jT1M8bc8BUsYP/QrgdPft5MufWMH3w8ELcnlLhSMh8yvBgjpUn+LYfP0Bd0QChw=="
enc_py27 = "eJxdkt1ygyAQRt/F617wDz5Lp+MoNUo0MSM6k/bpi7AbN73xnA9wF8TPqo0+hOqj6sKgAeMUfUzuH0zaTCVUIWTNWKYVQBi3Vmc6zYACiOMGaIGu0MB6w4HwnpFABYQ6BuqYutDCPPSvZXm/VmW+hv1wxgyIAOEKpoR+CUcRKBJFoWgUg2JRjjP1u2+uD5QQG8GYOuOTCS4hTmuSoROSiyxTfnLH5LGh8Tc9QlwEE6JUPEPD36P4F0tLMiLfY//cyEDex9xu4Y51ndM1Fs0uiSvimrghbok74jVxzmignTltx2k/Thvyo+N1GdsucVqCa1aUPcmt9Y3/WcM8Bw9xWPt+Ag++n9v7N6R8fAFhXW7tHXzb1ynEMaXHli45/wdxDJftuE3q+NVfA3jV+3Zp8m9ZpOn602f0fJYi54LkrwUW6JBNDEP19Qcj/gml"


def zenc(lst):
    return base64.b64encode(zlib.compress(json.dumps(lst, separators=(",", ":"))))


def zdec(b64):
    return json.loads(zlib.decompress(base64.b64decode(b64)).decode())


if PY2 and sys.version_info.minor == 6:
    codecs = zdec(enc_py26)
else:
    codecs = zdec(enc_py27)


def eprint(*args, **kwargs):
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)
    sys.stderr.flush()  # ???


# Cross-platform (doubt.jpg) read single key
try:
    from msvcrt import getch
except:
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class Config:
    mode = None
    via = None


def enum(**enums):
    return type(str("Enum"), (), enums)


Modes = enum(URL=1, VIA=2)


def sanitize(txt, for_print=True):
    """strip unprintables"""
    pre = suf = ""
    if for_print:
        pre = "\x1b[1;31m"
        suf = "\x1b[0m"

    if PY2:
        f = unichr
    else:
        f = chr

    bads = {}
    for r in [range(0, 32), range(127, 160)]:
        for n in r:
            bads[f(n)] = "<{0:02x}>".format(n)

    ret = ""
    for ch in txt:
        if ch in bads:
            ret += pre + bads[ch] + suf
        else:
            ret += ch

    return ret


def rename(cfg, folder):
    """Iterate through a folder and find files to rename"""
    for name in os.listdir(folder):
        if cfg.mode == Modes.URL:
            if PY2:
                fixed = unquote(name)
            else:
                fixed = unquote(name.decode("utf-8", "ignore")).encode("utf-8")

        elif cfg.mode == Modes.VIA:
            try:
                bork8 = name.decode("utf-8")
                if not cfg.via.search(bork8):
                    continue

                fixed = bork8.encode(via).decode(enc).encode("utf-8")
            except Exception as e:
                continue
        else:
            raise Exception("Unknown conversion mode [%s]" % cfg.mode)

        if fixed == name:
            continue

        msg = "({0}) => (\x1b[1;32m{1}\x1b[0m) ".format(
            sanitize(name.decode("utf-8", "replace")), sanitize(fixed.decode("utf-8"))
        )
        eprint(msg, end="")
        ch = getch()
        eprint(ch)
        if ch == "y":
            path_from = os.path.join(folder, name)
            path_to = os.path.join(folder, fixed)
            os.rename(path_from, path_to)
        if ch == "q":
            sys.exit(0)


def iterate(cfg, folder):
    """Recursively traverse a folder"""
    rename(cfg, folder)
    for subfolder in os.listdir(folder):
        path = os.path.join(folder, subfolder)
        if os.path.isdir(path):
            eprint("Entering [{0}]".format(sanitize(path.decode("utf-8", "replace"))))
            iterate(cfg, path)


cfg = Config()

# Check if mode 1 (url)
if len(sys.argv) == 2 and sys.argv[1] == "url":
    cfg.mode = Modes.URL

# Check if mode 2 (via)
elif len(sys.argv) == 4 and sys.argv[2] == "via":
    cfg.mode = Modes.VIA
    enc = sys.argv[1]
    via = sys.argv[3]
    cs = b""
    for a in range(128, 255):
        cs += struct.pack(b"B", a)
    cs = cs.decode(via)
    cs = "([" + cs + "]{3}|(?:[" + cs + "].){2})"
    cfg.via = re.compile(cs, flags=re.U)
    # eprint(cs)

# Check if mode 3 (detect)
elif len(sys.argv) == 4 and sys.argv[1] == "find":
    hits = 0
    bad = sys.argv[2]
    good = sys.argv[3]
    # eprint(repr(bad))
    # sys.exit(0)
    if PY2:
        bad = bad.decode("utf-8")
        good = good.decode("utf-8")

    for via in codecs:
        try:
            tmp = bad.encode(via)
        except:
            continue

        for enc in codecs:
            try:
                tmp2 = tmp.decode(enc)
                if tmp2 != good:
                    continue
            except:
                continue

            hits += 1
            eprint(
                "%s \x1b[1;31m%s\x1b[0m via \x1b[1;32m%s\x1b[0m"
                % (sys.argv[0], enc, via,)
            )

    eprint("Detection complete, found %d possible fixes" % (hits,))
    sys.exit(0)

else:
    eprint(
        """
\x1b[0;33mUsage:\x1b[0m
   unbork.py url
   unbork.py ENCODING via ENCODING
   unbork.by find 'BROKEN' 'GOOD'

\x1b[0;33mExample 1:\x1b[0m
   URL-escaped UTF-8, looks like this in ls:
   ?%81%8b?%81%88?%82%8a?%81??%81%a1.mp3

   \x1b[33m{0}\033[0;1m url\x1b[0m
   (\x1b[1;31m81%8b81%8882%8a81▒81%a1.mp3\x1b[0m) => (\x1b[1;32mかえりみち.mp3\x1b[0m)

\x1b[0;33mExample 2:\x1b[0m
   SJIS (cp932) parsed as MSDOS (cp437) looks like...
   ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3

   \x1b[33m{0}\033[0;1m cp932 via cp437\x1b[0m
   (\x1b[1;31mëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3\x1b[0m) => (\x1b[1;32m宇多田ヒカル - 桜流し.mp3\x1b[0m)

\x1b[0;33mExample 3:\x1b[0m
   Find a correction method from BROKEN to GOOD

   \x1b[33m{0}\033[0;1m find 'УпРlЙ╣Кy' '同人音楽'\x1b[0m
      .../unbork.py \x1b[1;31mcp932\x1b[0m via \x1b[1;32mcp866\x1b[0m ...
      Detection complete, found 4 possible fixes
""".format(
            sys.argv[0],
        )
    )
    sys.exit(1)


eprint("\nListing files. For each file, select [Y]es [N]o [Q]uit.\n")
iterate(cfg, b".")
eprint("done")


# url (bad testcase, find a better one)
# echo h > '%E3%81%8B%E3%81%88%E3%82%8A%E3%81%BF%E3%81%A1.mp3'
#
# sjis via latin1
# echo h > "$(echo ごみ箱 | iconv -t sjis | iconv -f latin1)"
