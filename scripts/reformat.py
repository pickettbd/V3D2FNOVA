
import sys

def handleArgs():
	
	if len(sys.argv) != 8:
		print("ERROR: Incorrect usage.", file=sys.stderr)
		sys.exit(1)
	
	samples_file_name = sys.argv[1]
	demographics_file_name = sys.argv[2]
	condition = sys.argv[3]
	input_file_directory = sys.argv[4]
	output_file_name_prefix = sys.argv[5]
	output_file_name_suffix = sys.argv[6]
	num_trials = int(sys.argv[7])

	return samples_file_name, demographics_file_name, condition, input_file_directory, output_file_name_prefix, output_file_name_suffix, num_trials

def transpose2Dlist(rows):
	# we assume this is not a sparse matrix

	if len(rows) == 0:
		return []
	elif len(rows) > 1:
		firstlen = len(rows[0])
		for row in rows[1:]:
			if len(row) != firstlen:
				print("ERROR: transpose2Dlist function assumes non-sparse matrix", file=sys.stderr)
				sys.exit(1)
	
	x = [ [] for _ in rows[0] ]

	for c in range(0, len(rows[0]), 1):
		for r in range(0,len(rows), 1):
			x[c].append(rows[r][c])

	return x

def parseDemographicsFile(ifn):
	dem = {}
	
	# 1	  2   3   4 	 5    6        7        8     9          10         11      12        13       14
	# subject,sex,age,height,mass,dom_limb,inv_limb,graft,speed_shod,speed_bare,control,underload,overload,symm

	with open(ifn, 'r') as ifd:
		ifd.readline() # skip headerline
		for line in ifd:
			fields = line.rstrip('\n').split(',')
			sample = fields[0]
			height = float(fields[3])
			mass = float(fields[4])
			inv_limb = int(fields[6])

			dem[sample] =  {"height": height, "mass": mass, "inv_limb": inv_limb}

	return dem

def parseListFileAsList(ifn):
	l = []

	with open(ifn, 'r') as ifd:
		for line in ifd:
			l.append(line.strip())
	
	return l

def parseSamplesFile(sample_fn):
	l = parseListFileAsList(sample_fn)

	return sorted(l, key=lambda x: int(x[1:]))

def extractIndicesAndInversionDecision(measurement,inv_limb,data_types,xyzs):

	direction = ""
	field = ""

	if measurement == "vgrf":
		direction = "Z"

		field = "FP1" # inv_limb == 0 (right)
		if inv_limb == 1: # left
			field = "FP2"

	elif measurement == "sagang" or measurement == "frontang":
		direction = "Y" # measurement == "sagang"
		if measurement == "frontang":
			direction = "X"

		field = "RIGHTKNEEANGLE" # inv_limb == 0 (right)
		if inv_limb == 1: # left
			field = "LEFTKNEEANGLE"

	elif measurement == "sagmom" or measurement == "frontmom":
		direction = "Y" # measurement == "sagmom"
		if measurement == "frontmom":
			direction = "X"

		field = "RIGHTKNEEMOMENT" # inv_limb == 0 (right)
		if inv_limb == 1: # left
			field = "LEFTKNEEMOMENT"
	
	# decide inversion
	invert = False
	if ( measurement == "frontang" and field == "RIGHTKNEEANGLE" ) or ( measurement == "frontmom" and field == "RIGHTKNEEMOMENT" ):
		invert = True

	return [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == direction], invert


def stringify(x):
	if not x is None:
		return str(x)
	else:
		return "NA"

if __name__ == "__main__":
	
	# handle the arguments to the script
	samplefn, demfn, condition, infdir, outfnpre, outfnsuf, num_trials = handleArgs()

	# parse the samples file, save as list of samples
	samples = parseSamplesFile(samplefn)

	# parse the demographics file, save in nested dictionary structure
	demdict = parseDemographicsFile(demfn)

	# loop through input files
	measurements = [ "vgrf", "sagang", "frontang", "sagmom", "frontmom" ]
	output = {}
	for measurement in measurements:
		output[measurement] = []

	for sample in samples:
		for measurement in measurements:
			output[measurement].extend( [ [] for x in range(0,num_trials,1) ] )

		ifn = f"{infdir}/{condition}/{sample}/{sample}_{condition}_normalized.txt"

		with open(ifn, 'r') as ifd:
			ifd.readline() # skip first line
			data_types = ifd.readline().rstrip('\n').upper().replace(' ', '').split('\t')
			ifd.readline() # skip third line
			ifd.readline() # skip fourth line
			xyzs = ifd.readline().rstrip('\n').upper().split('\t')

			indices = {}
			inversions = {}

			for measurement in measurements:
				indices[measurement], inversions[measurement] = extractIndicesAndInversionDecision(measurement,demdict[sample]["inv_limb"],data_types,xyzs)

				# test if enough trials
				if len(indices[measurement]) >= num_trials:
					indices[measurement] = indices[measurement][:num_trials]
				else:
					print(f"WARNING: Insufficient trials for {condition} {sample} {measurement}. {len(indices[measurement])} present, {num_trials} expected. Missing trials added and filled with NAs.", file=sys.stderr)

			# parse the actual data
			mass = float(demdict[sample]["mass"])
			massxheight = mass * demdict[sample]["height"]

			row_num = 6 # the main data starts at row #6 because of 5 header lines
			for line in ifd:
				fields = line.rstrip('\n').split('\t')

				for measurement in measurements:
					invert = 1
					if inversions[measurement]:
						invert = -1

					denom = 1 # angs
					if measurement == "vgrf":
						denom = mass
					elif measurement == "sagmom" or measurement == "frontmom":
						denom = massxheight

					for i,j in enumerate(indices[measurement]):
						k = len(output[measurement]) - num_trials + i
						if fields[j]:
							output[measurement][k].append(float(fields[j]) / denom * invert)
						else:
							print(f"WARNING: missing data in {condition} {sample} {measurement} column #{i+1} (csv row,column: {row_num},{j+1}). This cell is filled with an \"NA\" in the output.", file=sys.stderr)
							output[measurement][k].append(None)

					for i in range(len(indices[measurement]), num_trials, 1):
						k = len(output[measurement]) - num_trials + i
						output[measurement][k].append(None)

			row_num += 1

	# flip orientation (make it a list of rows instead of a list of columns)
	for measurement in measurements:
		output[measurement] = transpose2Dlist(output[measurement])

	# write the output files
	for measurement in measurements:

		outfn = f"{outfnpre}{condition}_{measurement}{outfnsuf}"

		with open(outfn, 'w') as ofd:

			# header lines
			# 	condition
			ofd.write(','.join([condition] * (num_trials * len(samples))) + '\n')

			# 	sample
			outstrs = []
			for sample in samples:
				outstrs.append(','.join([sample] * num_trials))
			ofd.write(','.join(outstrs) + '\n')

			# 	trial number
			outstrs = []
			for i in range(1,len(samples) + 1,1):
				outstrs.append(','.join(list(map(str, range(1, num_trials + 1, 1)))))
			ofd.write(','.join(outstrs) + '\n')

			# data
			for row in output[measurement]:
				ofd.write(','.join(list(map(stringify, row))) + '\n')
	
	# exit
	sys.exit(0)


