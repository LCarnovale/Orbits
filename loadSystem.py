# LoadFile - loads data from a .txt file that is laid out as a table
# In the text file:
#  - Lines beginning with '#' will be ignored
#  - Lines beginning with '$' will be parsed in as variables to the data dictionary.
#    The variables will be stored as strings in a dictionary within the main data dictionary
#    under the key '$VAR'.
#  - Lines beginning with '~' are used to tell the program how to read the file.
#    - ~DELIM = ',' , this will tell the program that each term in the rows and header
#      are separated by commas. For tabs, use '\t', or leave the command out, as tab is the default.
#    - ~REQUIRED = '.' / 'X,Y' , this parameter tells the program which of the names is
#      is required for an entry to be valid. Each row has an additional value under '$valid',
#      if a row is missing values from the designated columns then that value will be False, otherwise True.
#      '.' indicates there are no required values. The default is to require all values.
#    - ~KEY_COL = '2' , Designates which column will be used as the key in the final data dictionary.
#  - There must always be 1 line beginning with '!' that contains the header names.

import sys
COUNT = True

# Substitutes words starting with $ for their corresponding value in 'values'
def subs(values, string):
	# Get a string with just letters and spaces
	# text = "".join([(x if (x.isalpha() or x.isdigit() else " ") for x in string])
	newString = ""
	start, end = 0, 0
	i = 0
	validSubs = True # Valid substitution if all variables are found and substituted
	while (i < len(string)):
		char = string[i]
		if (char == "$"):
			start = i + 1
			end = start + 1
			while string[end].isalpha():
				end += 1
			if string[start:end] in values:
				newString += str(values[string[start:end]])
			else:
				print("Unable to find '%s' in values." % (string[start:end]))
				validSubs = False
			i = end
		else:
			newString += char
			i += 1
	return [newString, validSubs]



# removes lines commented out with #'s
def stripComments(text):
	lines = text.split("\n")
	lines = [line for line in lines if (line and line[0] != "#")]
	return lines


# Loads a file from 'path' and returns a dictionary with the first column
# as the key, which holds another dictionary with each table header as a key,
# and the corresponding row entry as a value
# spread: True or False, if True then takes a set of 'length' items evenly spread through
#     throughout the database, to cover the whole list.
# key: A list of strings, eg. ["$distance > 1"] to determine if a record is included.
#     Use $ to signify variable names, and they will be replaced with the relevant values
#     when being evaluated.
def loadFile(path, length=0, spread=False, key=None, quiet=True):
	"""Loads a database from a text file.
    Designed to read settings for the load from the text file,
    Look at source code for more info.
    path: path of the text file
    lenth: Max number of entries to read
    spread: True or False, if True then takes length number of items
        spread evenly through the whole file.
    key: A string or list of strings to filter the entries, formatted using
        elements from the table, ie ['$distance > 1'], use $ to represent variables
        and they will be substituted correctly
    quiet: True or False, if False then info about item counts etc. will be shown.
"""

	try:
		global COUNT
		f = open(path, "r")
		FILE = f.read()
		f.close()

		# columnNames = ["X", "Y", "Z", "VX", "VY", "VZ", "MASS", "DENSITY"]
		columnNames = None
		lines = stripComments(FILE)

		Vars = {
			"DELIM"	  : ['\t'],
			"REQUIRED": ["ALL"],
			"KEY_COL" : [0]
		}

		for line in lines:
			if (line[0] == "~"):
				if ("=" in line and ((line[1:].split("=")[0]).strip() in Vars)):
					value = (line[1:].split("=")[1]).strip()
					if (value[0] == value[-1] and value[0] == "'"):
						Vars[(line[1:].split("=")[0]).strip()] = value[1:-1]
					else:
						print("Poor formatting of data file, line: %s" % (line))
			if (line[0] == "!" and not columnNames):
				columnNames = [x for x in line[1:].split(Vars["DELIM"][0]) if x]
			elif (line[0] == "!" and columnNames):
				print("Warning: Multiple header rows defined in file. (File: %s, line: '%s')" % (path, line))

		DELIM = Vars["DELIM"][0]
		requiredValues = (columnNames if Vars["REQUIRED"][0] == "ALL" else Vars["REQUIRED"][0].strip(","))
		if (Vars["KEY_COL"][0] == 0):
			KEY_COL = 0
		elif (Vars["KEY_COL"][0] in columnNames):
			KEY_COL = columnNames.index(Vars["KEY_COL"])
		else:
			print("Warning: Unknown header name given for KEY_COL. Must be a column name given in the header row. (File: %s, given value: %s)" % (path, Vars["KEY_COL"][0]))
			KEY_COL = 0
		# except ValueError:
		# 	KEY_COL = 0
		if requiredValues[0] == '.':
			requiredValues = None
		table = []
		data = {}
		data["$VAR"] = {}
		# gotHeadings = False
		for line in lines:
			if not line: continue
			if line[0] == "$":
				words = line[1:].split("=")
				if (words[1].strip()[0] == "'" and words[1].strip()[-1] == "'"):
					data["$VAR"][words[0].strip()] = (words[1][1:-1])
				else:
					data["$VAR"][words[0].strip()] = float(words[1])
				continue
			elif line[0] in ["!", "~"]:
				continue
			if (DELIM == ","):
				row = [x for x in line.split(DELIM)]
			else:
				row = [x for x in line.split(DELIM) if x]
			table.append(row)

		# The table is now stored as a 2D list
		rowCounter = 0
		if length:
			if spread:
				iterTable = table[::int(len(table)/length)]
			else:
				iterTable = table[:length + 1]
		else:
			iterTable = table
		for row in iterTable:
			# Iterates through the rows
			newRow = {}
			newRow["$valid"] = True
			ignoreRow = False
			for name in columnNames:
				newRow[name.strip()] = None
			for i, col in enumerate(row[1:]):
				# iterates through the columns or words in a row
				name = columnNames[i + 1].strip()
				try:
					value = float(col)
				except ValueError:
					value = col
					if not value: value = None
					if (value == None and requiredValues and name in requiredValues):
						data[row[KEY_COL]]["$valid"] = False
				newRow[name] = value
			if key:
				nextKey = False
				if type(key) != list:
					key = [key]
				for k in key:
					testString, validSubs = subs(newRow, k)
					if not validSubs:
						continue
					if (not eval(testString)):
						ignoreRow = True
			if ignoreRow:
				ignoreRow = False
				continue
			else:
				rowCounter += 1
				if COUNT and not quiet:
					print("\rItem count: %d " % (rowCounter), end = "id: {}                    ".format(row[0]))
					sys.stdout.flush()
				data[row[KEY_COL]] = newRow
				if (length and rowCounter >= length):
					break
			if not data[row[KEY_COL]]["$valid"] and not quiet:
				print("Not enough data for '%s'." % (row[KEY_COL]))
		print()
	except KeyboardInterrupt:
		print("Stopping loadFile")
		exit()
	return data

# Testing:
# print(Test)
# Test = loadFile("SolSystem.txt", 5)
#
# for r in Test:
# 	print("%s: [" % (r), end = "")
# 	for t in Test[r]:
# 		print("%s = %s, " % (t, Test[r][t]), end = "")
# 	print("]")
