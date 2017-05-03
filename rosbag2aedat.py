#!/usr/bin/env python

""" 
rosbag2aedat.py is a Python script that converts the .rosbag output file from the rpg_davis_simulator [1] into a 
2.0 .aedat file [2] that can be processed by the software jAER [3].

[1] rpg_davis_simulator: https://github.com/uzh-rpg/rpg_davis_simulator
[2] AEDAT file formats: https://inilabs.com/support/software/fileformat/
[3] jAER: https://sourceforge.net/p/jaer/wiki/Home/

Author: F. Paredes Valles
Created: 03-05-2017
"""

import os
import sys
import rosbag
import struct

# input file
bagFile  = sys.argv[1]
bagSplit = bagFile.split('.')

# check if the output file already exists
aedatFile = bagSplit[0] + '.aedat'
if os.path.isfile(aedatFile):
    while True:
		entry = raw_input("\nThe file already exists. Do you want to delete it and create a new one? [y/n] ")
		if entry == 'y' or entry == 'Y':
			os.remove(aedatFile)
			break
		elif entry == 'n' or entry == 'N':
			sys.exit()

print "\nFormatting: .rosbag -> .aedat (This should take a couple of minutes)\n"

# open the file and write the headers
file = open(aedatFile, "w")
file.write('#!AER-DAT2.0\r\n')
file.write('# This is a raw AE data file created by saveaerdat.m\r\n');
file.write('# Data format is int32 address, int32 timestamp (8 bytes total), repeated for each event\r\n');
file.write('# Timestamps tick is 1 us\r\n');

# open the rosbag file and process the events
bag = rosbag.Bag(bagFile)
for topic, msg, t in bag.read_messages(topics=['/dvs/events']):
    for e in msg.events:

        ts = int(e.ts.to_nsec() / 1000.0)
        x = '{0:07b}'.format(e.x)
        y = '{0:07b}'.format(e.y)
        p = '1' if e.polarity else '0'
        address = "0" + y + x + p

        # write the event using big endian format
        file.write("%s" % struct.pack('>I', int(address, 2)))
        file.write("%s" % struct.pack('>I', int(ts)))

bag.close()