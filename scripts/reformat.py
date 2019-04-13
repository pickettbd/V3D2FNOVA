
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
		vgrf = [ [] for x in range(0,num_trials,1) ]
		sagang = [ [] for x in range(0,num_trials,1) ]
		frontang = [ [] for x in range(0,num_trials,1) ]
		sagmom = [ [] for x in range(0,num_trials,1) ]
		frontmom = [ [] for x in range(0,num_trials,1) ]

		ifn = f"{infdir}/{condition}/{sample}/{sample}_{condition}_normalized.txt"

		with open(ifn, 'r') as ifd:
			ifd.readline() # skip first line
			data_types = ifd.readline().rstrip('\n').upper().replace(' ', '').split('\t')
			ifd.readline() # skip third line
			ifd.readline() # skip fourth line
			xyzs = ifd.readline().rstrip('\n').upper().split('\t')

			# vGRF
			field = "FP1" # demdict[sample]["inv_limb"] == 0 (right)
			if demdict[sample]["inv_limb"] == 1: # left
				field = "FP2"

			vgrf_col_indices = [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == "Z"]

			# sagang & frontang
			field = "RIGHTKNEEANGLE" # demdict[sample]["inv_limb"] == 0 (right)
			if demdict[sample]["inv_limb"] == 1: # left
				field = "LEFTKNEEANGLE"

			sagang_col_indices = [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == "Y"]
			frontang_col_indices = [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == "X"]
				
			# sagmom & frontmom
			field = "RIGHTKNEEMOMENT" # demdict[sample]["inv_limb"] == 0 (right)
			if demdict[sample]["inv_limb"] == 1: # left
				field = "LEFTKNEEMOMENT"

			sagmom_col_indices = [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == "Y"]
			frontmom_col_indices = [i for i,data_type,xyz in zip(range(0,len(data_types),1),data_types,xyzs) if data_type == field and xyz == "X"]

			# test if enough trials
			if len(vgrf_col_indices) < num_trials or len(sagang_col_indices) < num_trials or len(frontang_col_indices) < num_trials or len(sagmom_col_indices) < num_trials or len(frontmom_col_indices) < num_trials:
				print(f"ERROR: Insufficient data for {num_trials} trials. At least one variable has less.", file=sys.stderr)
				sys.exit(1)

			# cut out uneeded trials
			vgrf_col_indices = vgrf_col_indices[:num_trials]
			sagang_col_indices = sagang_col_indices[:num_trials]
			frontang_col_indices = frontang_col_indices[:num_trials]
			sagmom_col_indices = sagmom_col_indices[:num_trials]
			frontmom_col_indices = frontmom_col_indices[:num_trials]

			# parse the actual data
			mass = float(demdict[sample]["mass"])
			denom = mass * demdict[sample]["height"]

			for line in ifd:
				fields = line.rstrip('\n').split('\t')

				# vgrf
				if vgrf_col_indices[-1] >= len(fields):
					print("ERROR: missing data in at least one vgrf column", file=sys.stderr)
					sys.exit(1)
				for i,j in enumerate(vgrf_col_indices):
					if not fields[j]:
						print("ERROR: missing data in at least one vgrf column", file=sys.stderr)
						sys.exit(1)
					vgrf[i].append(float(fields[j]) / mass)

				# angs
				#	sagang
				if sagang_col_indices[-1] >= len(fields):
					print("ERROR: missing data in at least one sagang column", file=sys.stderr)
					sys.exit(1)
				for i,j in enumerate(sagang_col_indices):
					if not fields[j]:
						print("ERROR: missing data in at least one sagang column", file=sys.stderr)
						sys.exit(1)
					sagang[i].append(float(fields[j]))


				#	frontang
				if frontang_col_indices[-1] >= len(fields):
					print("ERROR: missing data in at least one frontang column", file=sys.stderr)
					sys.exit(1)
				for i,j in enumerate(frontang_col_indices):
					if not fields[j]:
						print("ERROR: missing data in at least one frontang column", file=sys.stderr)
						sys.exit(1)
					frontang[i].append(float(fields[j]))

				# moms
				# 	sagmom
				if sagmom_col_indices[-1] >= len(fields):
					print("ERROR: missing data in at least one sagmom column", file=sys.stderr)
					sys.exit(1)
				for i,j in enumerate(sagmom_col_indices):
					if not fields[j]:
						print("ERROR: missing data in at least one sagmom column", file=sys.stderr)
						sys.exit(1)
					sagmom[i].append(float(fields[j]) / denom)

				#	frontmom
				if frontmom_col_indices[-1] >= len(fields):
					print("ERROR: missing data in at least one frontmom column", file=sys.stderr)
					sys.exit(1)
				for i,j in enumerate(frontmom_col_indices):
					if not fields[j]:
						print("ERROR: missing data in at least one frontmom column", file=sys.stderr)
						sys.exit(1)
					frontmom[i].append(float(fields[j]) / denom)

		# load data from this file into the larger data structures
		output["vgrf"].extend(vgrf)
		output["sagang"].extend(sagang)
		output["frontang"].extend(frontang)
		output["sagmom"].extend(sagmom)
		output["frontmom"].extend(frontmom)

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
				ofd.write(','.join(list(map(str, row))) + '\n')
	
	# exit
	sys.exit(0)


