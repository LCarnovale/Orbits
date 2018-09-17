# Author       : Leo Carnovale
# Last Updated : 30/09/2017
#
# LoadFile - loads data from a .txt file that is laid out as a table
#
# In the text file:
#  - Lines *BEGINNING* with '#' will be ignored
#  - Lines beginning with '$' will be parsed in as variables to the data dictionary.
#    The variables will be stored as either floats (first preference) or strings
#    in a dictionary within the main data dictionary under the key '$VAR'.
#  - Lines beginning with '~' are used to tell the program how to read the file. (Example values are given.)
#    - ~DELIM = ',' , this will tell the program that each term in the rows and header
#      are separated by commas. For tabs, use '\t', or leave the command out, as tab is the default.
#    - ~REQUIRED = '.' / 'X,Y' , this parameter tells the program which of the names is
#      required for an entry to be valid. Each row has an additional value under '$valid',
#      if a row is missing values from the designated required columns then that value will be False,
#      otherwise True. '.' indicates there are no required values. The default is to require all values.
#    - ~KEY_COL = '2' , Designates which column will be used as the key in the final data dictionary.
#    - ~NULL_VAL = 'NULL' / '---' /... These values will be read as NoneType ('None') values.
#    - ~AUTO_ID = 'True' / 'False', Must be true or false. Default false. If true,
#      then a new field is created called $ID and each entry is given a unique ID, instead of using
#      one of the given fields as an ID.
#  - There must always be 1 line beginning with '!' that contains the header names.
#  - When the actual data table is being read, the values will be attempted to be converted
#    into floats then stored, if they can't then they will be stored as strings, except for
#    the null values as described above.

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



# removes lines commented out with #'s (Only removes lines with '#' at the start)
def stripComments(text):
	lines = text.split("\n")
	lines = [line for line in lines if (line and line[0] != "#")]
	return lines

# def count(path, key=None):
# 	if (key == None):
# 		print("Usage: count(<path>, <key (string)>)")
# 		return
# 	try:
# 		f = open(path)



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
	except FileNotFoundError:
		print("Error in loadSystem.py: Unable to find file '{}'".format(path))
	try:
		columnNames = None
		lines = stripComments(FILE)

		Vars = {
			"DELIM"	   : ['\t'],
			"REQUIRED" : ["ALL"],
			"KEY_COL"  : [0],
			"NULL_VAL" : ["NONE", "NULL"],
			"AUTO_ID"  : "False"
		}
		for line in lines:
			# Finds the variable declarations (lines beginning with '~').
			# Sets the relevant variable in the above dictionary 'Vars'
			if (line[0] == "~"):
				if ("=" in line and ((line[1:].split("=")[0]).strip() in Vars)):
					value = (line[1:].split("=")[1]).strip()
					if (value[0] == value[-1] and value[0] == "'"):
						Vars[(line[1:].split("=")[0]).strip()] = value[1:-1]
					else:
						print("Poor formatting of data file, line: %s" % (line))
			# Lines beginning with '!' are column header lines, there should be exactly one.
			if (line[0] == "!" and not columnNames):
				columnNames = [x for x in line[1:].split(Vars["DELIM"][0]) if x]
			elif (line[0] == "!" and columnNames):
				print("Warning: Multiple header rows defined in file. (File: %s, line: '%s')" % (path, line))

		# Variable-specific checks:
		if type(Vars["NULL_VAL"]) == str: Vars["NULL_VAL"] = [Vars["NULL_VAL"]]
		try:
			temp = eval(Vars["AUTO_ID"])
		except Exception:
			print("Warning: Invalid value given for ~AUTO_ID. (File %s, given value: %s)" % (path, Vars["AUTO_ID"]))
		else:
			Vars["AUTO_ID"] = temp

		# DELIM = Vars["DELIM"]
		REQUIRED = Vars["REQUIRED"]
		KEY_COL = Vars["KEY_COL"]
		NULL_VAL = Vars["NULL_VAL"]
		AUTO_ID = Vars["AUTO_ID"]

		DELIM = Vars["DELIM"][0]

		# If the required values are 'ALL' (The default) then simply make them equal to the column header names.
		# Otherwise, the required fields should be the header names of the relevant columns.
		requiredValues = (columnNames if REQUIRED[0] == "ALL" else REQUIRED[0].strip(","))
		# Alternatively, the required values can be given as '.', where none are required.
		if requiredValues[0] == '.':
			requiredValues = None

		# The key_col is by default 0 but otherwise can be given as a column header name.
		if (AUTO_ID):
			KEY_COL = -1 # No key column exists if AUTO_ID is true. A key column will be made later.
		elif (KEY_COL[0] == 0):
			KEY_COL = 0
		elif (KEY_COL[0].isnumeric()):
			tempKEY_COL = int(KEY_COL[0])
			if (KEY_COL >= len(columnNames)):
				print("Error: Given KEY_COL value column index outside range of columns. (File: %s)" % (path))
				tempKEY_COL = 0
			KEY_COL = tempKEY_COL
		elif (KEY_COL[0] in columnNames):
			KEY_COL = columnNames.index(KEY_COL)
		else:
			print("Warning: Unknown header name given for KEY_COL. Must be a column name given in the header row. (File: %s, given value: %s)" % (path, Vars["KEY_COL"][0]))
			KEY_COL = 0


		table = []                        # Table: A temporary list containing all the data rows in the table.
		data = {}                         # data : The final data dictionary to be returned by this function
		data["$VAR"] = {}                 # data["$VAR"] contains a dictionary with variables defined in the data file
		# gotHeadings = False
		for line in lines:
			if not line: continue         # Ignore empty lines
			if line[0] == "$":            # This line will define a variable
				words = line[1:].split("=")
				if (words[1].strip()[0] == "'" and words[1].strip()[-1] == "'"):
					data["$VAR"][words[0].strip()] = (words[1][1:-1])
				else:
					data["$VAR"][words[0].strip()] = float(words[1])
				continue
			elif line[0] in ["!", "~"]:   # This line is either a load function variable definition or a header row
				continue
			if (DELIM == ","):
				# Empty values can be seen and distinguished if the delimiter
				# is a non-whitespace character, hence the check '... if x]'
				# is not necessary.
				row = [x for x in line.split(DELIM)]
			else:
				row = [x for x in line.split(DELIM) if x]
			table.append(row)

		# The (whole) table is now stored as a 2D list
		rowCounter = 0
		# We make a list 'iterTable' which contains the rows that we wish to iterate through
		# If a length is defined (a specific number of records to read)
		# Then we assign a fixed number of rows to iterTable, otherwise we
		# make it the whole table.
		if length:
			if (length > len(table)):
				print("Specified length greater than the length of the table.")
				print("(Table length: %d, given length: %d.)" % (len(table), length))
			elif spread:
				iterTable = table[::int(len(table)/length)]
			else:
				iterTable = table[:length + 1]
		else:
			iterTable = table
		for row in iterTable:
			newRow = {}
			newRow["$valid"] = True
			ignoreRow = False
			for name in columnNames:
				newRow[name.strip()] = None

			# iterates through the columns or words in a row
			for i, col in enumerate(row):
				if (col == KEY_COL or i == KEY_COL):
					if (col == KEY_COL): KEY_COL = i # If KEY_COL is a string, turn it into the corresponding index for later use
					continue  # Don't include the key column
				name = columnNames[i].strip()          # The name of the field
				try:
					value = float(col)                 # First try making it a float
				except ValueError:
					value = col                        # If can't, give up and leave it as a string.
					if not value or (value in NULL_VAL): value = None
					if ((value == None) and ((requiredValues) and (name in requiredValues))):
						newRow["$valid"] = False
				newRow[name] = value
			if key:                                    # key is an argument, either False or a string.
				if type(key) != list:
					key = [key]                        # The key can contain a list of strings
				for k in key:
					testString, validSubs = subs(newRow, k)
					if not validSubs:
						continue                       # This could be an error.
					try:
						tempEval = eval(testString)    # After substituting in the relevant values, evaluate the string.
					except Exception:
						print("Error in key string evaluation. Aborting.")
						exit()
					if (not tempEval):
						ignoreRow = True
			if ignoreRow:
				ignoreRow = False
				continue
			else:
				rowCounter += 1
				if COUNT and not quiet:
					print("\rItem count: {}, id: {}                ".format(rowCounter, row[0]), end = "")
					sys.stdout.flush()
				if AUTO_ID:
					data[rowCounter] = newRow
					keyCol = rowCounter
				else:
					data[row[KEY_COL]] = newRow
					keyCol = row[KEY_COL]
				if (length and rowCounter >= length):
					break
			if not data[keyCol]["$valid"] and not quiet:
				print("Not enough data for '%s'." % (row[keyCol]))
		print()
	except KeyboardInterrupt:
		print("\nStopping loadFile. (File: %s)" % (path))
		exit()
	except Exception:
		print("\nUnkown exception occured. (File: %s)" % (path))
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
