# unbork - Repair filename mojibake

Currently supports three modes:
* Decode partially URL-escaped UTF-8
* Decode incorrectly parsed foreign charsets
* Find a way to convert from X to Y

Starts in your current directory and makes its way down recursively

Detects corrupted filenames and asks for confirmation on each file


## Usage
    unbork.py url
    unbork.py ENCODING via ENCODING
    unbork.py find 'BAD' 'GOOD'

## Example 1:
URL-escaped UTF-8, looks like this in ls:

    ?%81%8b?%81%88?%82%8a?%81??%81%a1.mp3
    
`unbork.py url` outputs the following:

    (81%8b81%8882%8a81▒81%a1.mp3) => (かえりみち.mp3)

## Example 2:
SJIS (cp932) parsed as MSDOS (cp437) looks like this in ls:

    ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3
    
`unbork.py cp932 via cp437` outputs the following:

    (ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3) => (宇多田ヒカル - 桜流し.mp3)

## Example 3:
Find a correction method from BAD to GOOD

`unbork.py find 'УпРlЙ╣Кy' '同人音楽'` outputs the following:

    /bin/unbork.py cp932 via cp866
    /bin/unbork.py shift_jis via cp866
    /bin/unbork.py shift_jis_2004 via cp866
    /bin/unbork.py shift_jisx0213 via cp866
    Detection complete, found 4 possible fixes
