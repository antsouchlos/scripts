#!/usr/bin/python

import sys
import math
import subprocess
from threading import Timer
import time
import signal
import os

version = "[v0.1_pre-alpha]"
tad = "9/2/2017 16:02"

signal_distance_constant = 0.05454545454
point_distance_constant = 5

def usage():
	print("What it does:\nTakes 2 measurements of the signal strenght of a station, wich it uses to determine possible locations of the station\n")
	print("Usage: '" + sys.argv[0] + " [interface] [bssid of station] [station type]'")
	print("\t[station type]: determines weather the station is an access point ('ap') or a client ('c')")
	print("Example: './find_location.py ath0mon 2C:26:C5:28:7B:B4'")


def error(message, error="Error"):
	print(error + ": " + message)
	sys.exit()

#makes sure there are enough arguments and of the right type
def verifyArguments():
	n = len(sys.argv)

	if n < 4:
		if n > 1:
			if (sys.argv[1] == "-h"):
				usage()
				sys.exit()

		error("Not enough arguments provided\nUse the '-h' option for help")

	if (sys.argv[3] != "ap") and (sys.argv[3] != "c"):
		error("Argument 3 can either be 'ap', or 'c'\nUse thre '-h' option for help")

#takes the output of the "airodump-ng [interface]" command and a bssid as an argument and finds
#the signal strength of the access point with the given bssid
def findSignalStrength(data, bssid, station_type):
	for item in data.split("\n"):
		if bssid in item:

			words = item.split()

			if station_type == "ap":
				return words[words.index(bssid) + 1]
			else:
				return words[words.index(bssid) + 2]

	return 100

def getOutput(interface):
	cmd = ["./airodump_wrapper " + interface]

	child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout, nothing = child.communicate()

	return str(stdout)


def measureSignalStrength(interface, bssid, station_type):
	ss = findSignalStrength(getOutput(interface), bssid, station_type)
	return ss

def calculateDistance(ss):
	return float(ss)*signal_distance_constant

#calculates the angle the station is located at, in relation to the line connecting the
#two spots the measurements were made at
def calculateAngle(ss1, ss2):
	d1 = calculateDistance(ss1)
	d2 = calculateDistance(ss2)

	x = (d1**2 - d2**2) / point_distance_constant + point_distance_constant

	print("[DEBUG] x: " + str(x))
	print("[DEBUG] d1: " + str(d1))

	if x**2 >= d1*22:
		error("An error occurred while claculating the position of the host. Trying again with other spots might solve the issue")

	y = math.sqrt(d1**2 - x**2)

	angle = math.degrees(math.atan(y / x))

	return angle

def main():
	print("find_location " + version + "\nDevelopment started " + tad + "\n")

	verifyArguments()

	print("Go to a spot where you have a line of about 5 meters of free space to move on.")
	input("Press any key to take the first measurement\n")

	ss1 = measureSignalStrength(sys.argv[1], sys.argv[2], sys.argv[3])

	if ss1 == 100:
		error("The signal strength of the station could not be determined", "Error")

	print(ss1)

	print("Move to a spot approximately 5 meters away from you")
	input("Press any key to take the second measurement\n")

	ss2 = measureSignalStrength(sys.argv[1], sys.argv[2], sys.argv[3])

	angle = calculateAngle(ss1, ss2)
	distance = calculateDistance(ss2)

	print("The station is located at an angle of approximately " + angle + " degrees at the point you are standing, in relation to the line connecting the two points at which the measurements were made.")
	print("Your distance to the station is approximately " + distance + "meters")

main()
