import sys

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
def loadFile(path, length=0, spread=False, key=None):
	f = open(path, "r")
	FILE = f.read()
	f.close()

	# The first line must contain the column titles matching the following names
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

	# print("Column names:", columnNames)
	DELIM = Vars["DELIM"][0]
	requiredValues = (columnNames if Vars["REQUIRED"][0] == "ALL" else Vars["REQUIRED"][0].strip(",")) # Currently all fields must contain values
	KEY_COL = Vars["KEY_COL"][0]

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
			iterTable = table[1::int(len(table)/length)]
		else:
			iterTable = table[1:length + 1]
	else:
		iterTable = table[1:]
	for row in iterTable:
		# print(row)
		# data[row[KEY_COL] = {}
		# data[row[KEY_COL]["valid"] = True
		newRow = {}
		newRow["$valid"] = True
		ignoreRow = False
		for i, col in enumerate(row[1:]):
			# table[0] is the row containing the header names
			name = columnNames[i + 1].strip()
			try:
				value = float(col)
			except ValueError:
				value = col
				if not value: value = None
				if (value == None and requiredValues and name in requiredValues):
					# enoughData = False
					data[row[KEY_COL]]["$valid"] = False
			# except NameError:
			# 	print("Name error with row %d" % (i))
			newRow[name] = value
		if key:
			nextKey = False
			if type(key) != list:
				key = [key]
			for k in key:
				testString, validSubs = subs(newRow, k)
				if not validSubs:
				# 	nextKey = True
				# if nextKey:
				# 	nextKey = False
					continue
				# print("testString:", testString)
				if (not eval(testString)):
					ignoreRow = True
		if ignoreRow:
			ignoreRow = False
			continue
		else:
			rowCounter += 1
			print("\rItem count: %d " % (rowCounter), end = "id: {}                    ".format(row[0]))
			sys.stdout.flush()
			data[row[KEY_COL]] = newRow
			if (length and rowCounter >= length):
				break
		if not data[row[KEY_COL]]["$valid"]:
			print("Not enough data for '%s'." % (row[KEY_COL]))
	print()
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
