# removes lines commented out with #'s
def stripComments(text):
	lines = text.split("\n")
	lines = [line for line in lines if (line and line[0] != "#")]
	return lines


# Loads a file from 'path' and returns a dictionary with the first column
# as the key, which holds another dictionary with each table header as a key,
# and the corresponding row entry as a value
def loadFile(path, length=0, spread=False):
	f = open(path, "r")
	FILE = f.read()
	f.close()

	# The first line must contain the column titles matching the following names
	# columnNames = ["X", "Y", "Z", "VX", "VY", "VZ", "MASS", "DENSITY"]
	columnNames = None
	lines = stripComments(FILE)

	Vars = {
		"DELIM"	  : ['\t'],
		"REQUIRED": ["ALL"]
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
		data[row[0]] = {}
		data[row[0]]["valid"] = True
		for i, col in enumerate(row[1:]):
			# table[0] is the row containing the header names
			name = columnNames[i + 1]
			try:
				value = float(col)
			except ValueError:
				value = None
				if (requiredValues and name in requiredValues):
					# enoughData = False
					data[row[0]]["valid"] = False

			data[row[0]][name] = value
		if not data[row[0]]["valid"]:
			print("Not enough data for '%s'." % (row[0]))
		rowCounter += 1
		if (length and rowCounter >= length):
			break
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
