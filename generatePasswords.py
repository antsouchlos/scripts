#!/usr/bin/python

# function: generates passwords based on commonly used patterns and a dictionary of words


# ----------------- NOT USED, TOO MANY POSSIBILITIES ------------------
#
# EBNF of how a password could be built
#
# password = words, [number]
# words = [word], [symbol], word
#		| [symbol], words, [symbol]
#		| [date], words
# date = day, month, year
#		| day, symbol, month, symbol (* same symbol as before*), year
#		| month, day, year
#		| month, symbol, day, symbol (* same symbol as before*), year
# day = (* integer between 1 and 31 *)
# month = (*integer between 1 and 12*)
# year = whole_year | part_year
# whole_year = (* integer between 1900 and 2017 *)
# part_year = (* integer (prefaced with zeros until len==2) between 0 and 99*)
# symbol = (* defined at runtime *)
# word = (* defined at runtime *)
# number = (* integer between 0 and 999*)


# -------------------------------- USED --------------------------------
#
# EBNF of a how a password could be built (less frequently used patterns removed)
#
# password = words
# words = word, ([number] | [date])
#			| [date], word
# date = day, month, year
# day = (* integer between 1 and 31 *)			COULD BE FURTHER OPTIMIZED: INCLUDE 31 DAYS ONLY FOR CERTAIN MONTHS AND 29 DAYS FOR FEBRUARY
# month = (*integer between 1 and 12*)
# year = (* integer (prefaced with zeros until len==2) between 0 and 99*)
# word = (* defined at runtime *)
# number = (* integer between 0 and 100 *)
#
# In total (with a dictionary of 100 words): 7,375,600 different combinations

from sys import argv, exit

version = "[v0.1_pre-alpha]"
tad = "11/2/2017 - 18:12"

def help():
	print("What it does:")
	print("generates passwords, based on commonly used pattern and a dictionary of words\n")
	print("Usage: '" + argv[0] + " <file containing the dictionary of words to be used> [name of output file]'")
	print("\tThe second argument is optional, with a default output file of 'passwords.txt'")
	print("Example: './generatePasswords dictionary.txt passwords.txt'\n")
	print("The dictionary-file must contain one word in each line")

	exit()

def error(message):
	print("Error: ", + message)
	exit()

def writePassword(password, file):
	file.write(password + "\n")

def readDictionary(filename):
	return [line.rstrip('\n') for line in open(filename)]

def addDate(word, file):
	for day in range(1, 31):
		for month in range(1, 12):
			for year in range(0, 99):
				writePassword(word + str(day) + str(month) + str(year).zfill(2), file)

def addNumber(word, file):
	for i in range(0, 100):
		writePassword(word + str(i), file)

#makes sure if there are enough arguments and displays help
def verifyArguments():
	if len(argv) < 2:
		error("Not enough arguments provided\nUse the -h option for help")

	if argv[1] == "-h":
		help()

def main():
	print(version + "\nDevelopment started " + tad)

	file = None

	if (len(argv) > 3):
		file = open(argv[2])
	else:
		file = open("passwords.txt", "w")

	dictionary = readDictionary(argv[1])

	for word in dictionary:
		writePassword(word, file)

	for word in dictionary:
		addNumber(word, file)
		addDate(word, file)

	for day in range(1, 31):
		for month in range(1, 12):
			for year in range(0, 99):
				for word in dictionary:
					writePassword(str(day) + str(month) + str(year).zfill(2) + word, file)

	file.close()

main()
