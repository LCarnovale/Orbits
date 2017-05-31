# removes lines commented out with #'s
def stripComments(text):
	lines = text.split("\n")
	lines = [line for line in lines if (line and line[0] != "#")]
	return lines

def loadFile(path):
	f = open(path, "r")
	FILE = f.read()
	f.close()

	# The first line must contain the column titles matching the following names
	columnNames = ["X", "Y", "Z", "VX", "VY", "VZ", "MASS", "DENSITY"]
	requiredValues = columnNames # Currently all fields must contain values

	lines = stripComments(FILE)
	table = []
	for line in lines:
		if not line: continue
		row = [x for x in line.split("\t") if x]
		table.append(row)

	# The table is now stored as a 2D list
	data = {}
	for row in table[1:]:
		data[row[0]] = {}
		data[row[0]]["valid"] = True
		for i, col in enumerate(row[1:]):
			# table[0] is the row containing the header names
			name = table[0][i + 1]
			try:
				value = float(col)
			except ValueError:
				value = None
				if name in requiredValues:
					# enoughData = False
					data[row[0]]["valid"] = False

			data[row[0]][name] = value
		if not data[row[0]]["valid"]:
			print("Not enough data for '%s'." % (row[0]))
	# print("Done.")
	return data
