__author__ = "Brandon Pickett"

# ----------- IMPORTS ---------------------------- ||
import sys

# ----------- CLASSES ---------------------------- ||

# ---------- FUNCTIONS --------------------------- ||
def handleArgs():
	
	if len(sys.argv) == 1: # if no arguments are provided, display help intead of using all defaults
		sys.argv.append("-h")

	import argparse

	parser = argparse.ArgumentParser(prog="reformat.py", usage="%(prog)s [-d demo.csv] [-s sample.list] [-i data/input] [-op data/output/] [-os .csv] [-c data/conditions.list] [-C control] [-n 5] [-glNThv]", description="Prepare Visual 3D (V3D) data for FNOVA at UNC-CH", add_help=False)

	input_group = parser.add_argument_group("Input Files")
	input_group.add_argument("-d", "-df", "--demo-file", dest="demo_fn", metavar="demo.csv", type=str, action="store", help="The name of the CSV file containing demographics information. Column 1 must be the sample/subject id. Columns 4, 5, and 7 must be height (cm), mass (kg), and involved limb (0=Right, 1=Left), respectively. [default: data/demographics.csv]", default="data/demographics.csv", required=False)
	input_group.add_argument("-i", "-id", "--input-dir", dest="input_dir", metavar="/path/to/input/dir", type=str, action="store", help="The directory where the input data files are located. This directory MUST contain one directory per condition. Each condition directory must contain one directory per sample/subject. Each of those directories, in turn, must have a file named after the pattern ${sample}_${condition}_normalized.txt. [default: data/input]", default="data/input", required=False)
	input_group.add_argument("-s", "-sf", "--samples-file", dest="samples_fn", metavar="samples.list", type=str, action="store", help="The name of the file containing sample/subject identifiers. One id per line. [default: data/samples.list]", default="data/samples.list", required=False)

	output_group = parser.add_argument_group("Output Files")
	output_group.add_argument("-op", "--output-prefix", dest="output_fn_pfx", metavar="/out/dir/out_file_", type=str, action="store", help="The prefix of the output file name. This includes the path and filename. The actual output file will have the the condition and measurements sandwiched between this prefix and the suffix, like so: ${prefix}${condition}_{measurement}${suffix}. If the prefix is just a directory, be sure to include the trailing slash. [default: data/output/", default="data/output/", required=False)
	output_group.add_argument("-os", "--output-suffix", dest="output_fn_sfx", metavar=".csv", type=str, action="store", help="The suffix of the output file name. This includes the leading period, if desired. The actual output file will have the the condition and measurements sandwiched between the prefix and this suffix, like so: ${prefix}${condition}_{measurement}${suffix}. [default: .csv", default=".csv", required=False)

	options_group = parser.add_argument_group("Options")
	#options_group.add_argument("-c", "--condition", dest="condition", metavar="cond1|cond2|...|condN", type=str, action="store", help="The experimental condition of the provided data, e.g., control, overload, etc. [default: control]", default="control", required=False)
	options_group.add_argument("-c", "-cf", "--conditions-file", dest="conditions_fn", metavar="data/conditions.list", type=str, action="store", help="The file name for the experimental conditions of the provided data, e.g., control, overload, etc. One condition is listed per line. [default: data/conditions.list]", default="data/conditions.list", required=False)
	options_group.add_argument("-C", "-cc", "-Cc", "-CC", "--control-condition", dest="control_condition", metavar="control", type=str, action="store", help="The condition that is to be treated as the control. [default: control]", default="control", required=False)
	options_group.add_argument("-g", "-dg", "--downgrade", "--downhill", dest="downgrade", action="store_true", help="When the grade is zero (level ground) or positive (uphill), the LEFT knee values need to be negated. When the grade is negative (downhill), the RIGHT knee values need to be negated. By default, the grade is assumed to be non-negative.")
	options_group.add_argument("-l", "--last", dest="last_not_first", action="store_true", help="By default, the first n trials are used. Instead, use the last n trials.")
	options_group.add_argument("-n", "-nt", "--num-trials", dest="num_trials", metavar="int", type=int, action="store", help="The number of trials (stances) to use. [default: 5]", default=5, required=False)
	options_group.add_argument("-N", "-NC", "-nc", "-Nc", "--no-concatenate", dest="concatenate", action="store_false", help="By default, the output files for each condition are combined into an extra output file all horizontally concatenated together, with the control condition occuring twice. Specify this option and the concatenated files will be skipped. You need not specify --control-condition when using this option because it (--control-condition) will be ignored.")
	options_group.add_argument("-T", "--not-treadmill", dest="treadmill", action="store_false", help="vGRF values are pulled from columns FP1 (right foot) and FP2 (left foot) when collected on a treadmill. If overground (i.e., not treadmill) data is collected, the columns are FP3 (right foot) and FP2 (left foot). Specifying this option will cause the program to search for FP3 columns instead of FP1 columns.")
	
	misc_group = parser.add_argument_group("Misc", )
	misc_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
	misc_group.add_argument("-v", "--version", action="version", version="%(prog)s 0.9.0-beta", help="Show version number and exit")

	args = parser.parse_args()

	# validate number of trials
	if args.num_trials < 1:
		sys.stderr.write(f"ERROR: It makes sense to analyze one ore more trials. {args.num_trials} is not a sane choice.\n")
		sys.exit(1)
	
	# ensure input sample, demo, and conditions files exist
	from pathlib import Path,PurePath
	if not Path(args.demo_fn).is_file():
		print(f"ERROR: {args.demo_fn} either does not exist or is not a regular file.", file=sys.stderr)
		sys.exit(1)

	if not Path(args.samples_fn).is_file():
		print(f"ERROR: {args.samples_fn} either does not exist or is not a regular file.", file=sys.stderr)
		sys.exit(1)

	if not Path(args.conditions_fn).is_file():
		print(f"ERROR: {args.conditions_fn} either does not exist or is not a regular file.", file=sys.stderr)
		sys.exit(1)
	
	# ensure input sample and conditions files have unique entries
	l = parseListFileAsList(args.samples_fn)
	if len(l) != len(set(l)):
		print(f"ERROR: {args.samples_fn} has duplicate entries.", file=sys.stderr)
		sys.exit(1)

	l = parseListFileAsList(args.conditions_fn)
	if len(l) != len(set(l)):
		print(f"ERROR: {args.conditions_fn} has duplicate entries.", file=sys.stderr)
		sys.exit(1)

	# ensure control condition is in the conditions file
	if args.concatenate:
		control_in_conditions_file = False
		for condition in l:
			if condition == args.control_condition:
				control_in_conditions_file = True
				break
		if not control_in_conditions_file:
			print(f"ERROR: control condition ({control}) was not in {args.condition_fn}.", file=sys.stderr)
			sys.exit(1)

	# ensure output suffix directory exists
	parent = ''
	if len(args.output_fn_pfx) > 0 and args.output_fn_pfx[-1] == '/':
		parent = Path(args.output_fn_pfx).resolve()
	else:
		parent = Path(PurePath(Path(args.output_fn_pfx).resolve()).parent)

	if not parent.is_dir():
		print(f"ERROR: {parent} either does not exist or is not a directory. The path was extracted from \"{args.output_fn_pfx}\".", file=sys.stderr)
		sys.exit(1)
	
	return args.samples_fn, args.demo_fn, args.conditions_fn, args.input_dir, args.output_fn_pfx, args.output_fn_sfx, args.num_trials, args.downgrade, args.last_not_first, args.concatenate, args.control_condition, args.treadmill

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

def parseConditionsFile(condition_fn, control_condition, force_control_last=True):
	# extract the conditions
	l = sorted(parseListFileAsList(condition_fn))

	if force_control_last:
		# ensure control_condition is last item
		l.remove(control_condition)
		l.append(control_condition)

	# return
	return l

def extractIndicesAndInversionDecision(measurement,inv_limb,data_types,xyzs,downgrade=False,treadmill=True):

	vGRF_right_colname = "FP1" if treadmill else "FP3"
	vGRF_left_colname = "FP2" #if treadmill else "FP2"

	direction = ""
	field = ""

	if measurement == "vgrf":
		direction = "Z"

		field = vGRF_right_colname # inv_limb == 0 (right)
		if inv_limb == 1: # left
			field = vGRF_left_colname

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
	field_limb = "RIGHT" if downgrade else "LEFT"
	if ( measurement == "frontang" and field == (field_limb + "KNEEANGLE") ) or ( measurement == "frontmom" and field == (field_limb + "KNEEMOMENT") ):
		invert = True

	return [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == direction], invert

def writeConcatenatedOutput(outfnpre, outfnsuf, measurements, conditions, control_cond):

	non_control_conditions = 0
	for condition in conditions:
		if condition != control_cond:
			non_control_conditions += 1

	for measurement in measurements:
		all_input_filenames = [ f"{outfnpre}{condition}_{measurement}{outfnsuf}" for condition in conditions ]
		all_input_filehandles = [ open(input_fn, 'r') for input_fn in all_input_filenames ]
		lines = [ ifh.readline() for ifh in all_input_filehandles ]
		lines.extend( [lines[-1] * (non_control_conditions - 1)] )

		# write the concatenated output file (all non-control conditions then the control
		# conditions repeated as many times are there are non-control conditions)
		outfn = f"{outfnpre}all_{measurement}{outfnsuf}"
		with open(outfn, 'w') as ofd:
			while all(lines): # since non-empty strings are truthy, this will continue as long as all files provide lines
				ofd.write(','.join(lines).replace('\n', '') + '\n')
				lines = [ ifh.readline() for ifh in all_input_filehandles ]
				lines.extend( [lines[-1] * (non_control_conditions - 1)] )

		# close the open input files
		for ifh in all_input_filehandles:
			ifh.close()

def stringify(x):
	if not x is None:
		return str(x)
	else:
		return "NA"

# ------------- MAIN ----------------------------- ||
if __name__ == "__main__":
	
	# handle the arguments to the script
	samplefn, demfn, condfn, infdir, outfnpre, outfnsuf, num_trials, downgrade, last_not_first, write_concatenation, control_cond, treadmill = handleArgs()

	# parse the samples file, save as list of samples
	samples = parseSamplesFile(samplefn)

	# parse the demographics file, save in nested dictionary structure
	demdict = parseDemographicsFile(demfn)

	# parse the conditions file, save as list of conditions
	conditions = parseConditionsFile(condfn, control_cond, force_control_last=write_concatenation)

	# loop through input files
	measurements = [ "vgrf", "sagang", "frontang", "sagmom", "frontmom" ]

	for condition in conditions:
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
					indices[measurement], inversions[measurement] = extractIndicesAndInversionDecision(measurement,demdict[sample]["inv_limb"],data_types,xyzs,downgrade=downgrade,treadmill=treadmill)

					# test if enough trials
					if len(indices[measurement]) >= num_trials:
						if last_not_first:
							indices[measurement] = indices[measurement][-num_trials:]
						else:
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
	
	if write_concatenation:
		writeConcatenatedOutput(outfnpre, outfnsuf, measurements, conditions, control_cond)
		
	# exit
	sys.exit(0)


