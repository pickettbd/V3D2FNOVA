#! /usr/bin/env awk -f

BEGIN {
	split("", xyz_tfrm); # creates empty xyz transform map
	split("", mult_tfrm); # create empty mult transform map
	split("", files); # create empty files map

	for (i=1; i<ARGC; i++)
	{
		if (i in ARGV && ARGV[i] ~ /^[XYZ]=>-?[XYZ]$/)
		{
			arg = ARGV[i]
			before = substr(arg, 1, 1)
			after = "";
			mult = 1;

			if (length(arg) == 4)
			{
				after = substr(arg, 4, 1);
			}
			else if (length(arg) == 5)
			{
				after = substr(arg, 5, 1);
				mult = -1;
			}

			xyz_tfrm[before] = after;
			mult_tfrm[before] = mult;
		}
		else if (ARGV[i] ~ /^-{1,2}h(elp)?$/)
		{
			print "\n\nawk -f reorient.awk -- transformation1 [another_transformation | an_input_file]...\n\n\tYou may provide transformations and input files in any order.\n\tYou should provide at least one transformation, otherwise this will simply copy the input to the output.\n\tIf no input files are provided, stdin will be assumed.\n\tTo specify stdin or use stdin with one more files, specify '-'.\n\tTransformations must meet this regex: /^[XYZ]=>-?[XYZ]$/.\n\tDon't forget to put single quotes around the transformation(s), else bash will think you're trying to perform redirection.\n\tExamples (all equivalent):\n\t\tawk -f reorient.awk -- 'X=>-Y' a.csv 'Y=>X' b.csv c.csv > d.csv\n\t\tawk -f reorient.awk -- 'X=>-Y' 'Y=>X' a.csv b.csv c.csv > d.csv\n\t\tawk -f reorient.awk -- a.csv 'X=>-Y' b.csv 'Y=>X' c.csv > d.csv\n\t\tcat b.csv | awk -f reorient.awk -- a.csv 'X=>-Y' - 'Y=>X' c.csv > d.csv\n\n" > "/dev/stdout";
			exit 0;
		}
		else
		{
			files[length(files)] = ARGV[i];
		}

		delete ARGV[i];
	}

	for (i=0; i<length(files); i++)
	{
		ARGV[i+1] = files[i];
	}
	ARGC = length(ARGV);

	FS="\t";
	OFS="\t";
	ORS="\n";
}

{
	if (NR > 5) # non-header lines
	{
		# negate
		for (i=1; i <= NF; i++)
		{
			if (i > 1)
			{
				printf OFS;
			}

			if (i in mult_tfrm)
			{
				printf $i * mult_tfrm[i];
			}
			else
			{
				printf $i;
			}
		}
		printf ORS;
	}
	else if (NR != 5) # header lines other than xyz
	{
		print $0;
	}
	else # if (NR == 5) # xyz header line
	{
		# xyz transform
		for (i=1; i <= NF; i++)
		{
			if (i > 1)
			{
				printf OFS;
			}

			if ($i in xyz_tfrm)
			{
				printf  xyz_tfrm[$i];
				mult_tfrm[i] = mult_tfrm[$i];
			}
			else
			{
				printf $i;
			}
		}
		printf ORS;

		for (k in xyz_tfrm)
		{
			delete mult_tfrm[k];
		}
	}
}
