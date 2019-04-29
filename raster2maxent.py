##=========================================================================
## Process raster data and prepare it for use with MAXENT
## 
## Script written by Bradley T. Martin, University of Arkansas
## Please submit any bug reports to: Bradley Martin, btm002@email.uark.edu
##=========================================================================

# Import necessary modules.
import arcpy
import argparse
import os
import sys

def main():
	
	# Parse command-line arguments
	args = parseArgs()
	
	# Set working directory
	arcpy.env.workspace = args.ws	
	
	# Get all raster layer filenames in directory.
	rasters = getRasterList(args.pattern)
	
	# Make a new directory to store output.
	prjFolder = os.path.join(args.ws, args.prj)

	# If the args.reprj has not been toggled off. Default is True.
	if args.reprj:
		# Makes new directory to store output from reprojection.
		# Can be toggled off if already have files in correct coordinate projection.
		createFolder(prjFolder)
		reproject(rasters, args.epsg, args.datum, args.resampling, prjFolder)
	
	# Set directory for clipped output.
	clipFolder = os.path.join(args.ws, args.clipped)

	# If the args.clip_off has not been toggled (i.e., it is set to True by default).
	if args.clip_off:
		# Make a new directory to store output.
		
		# Change workspace.
		arcpy.env.workspace = prjFolder
		
		# Get all raster layer filenames in directory
		rasters = getRasterList(None)
				
		createFolder(clipFolder)
		
		# Clip the rasters to feature class.
		clip(rasters, args.fc, clipFolder)
		
	arcpy.env.workspace = clipFolder
	
	rasters = getRasterList(None)
	
	# Makes sure cell sizes and min/max bounds are identical between raster layers.
	validateRasters(rasters)
		

def validateRasters(rasters):
	# Validate that geographic bounds and cell 
	#sizes are identical for all raster layers;
	# MAXENT requires them to be identical.
	
	print "\n\nValidating output raster layers..."
	boundsList = list()
	cellSizes = list()
	for raster in rasters:
		cellX = arcpy.GetRasterProperties_management(raster, "CELLSIZEX")
		cellY = arcpy.GetRasterProperties_management(raster, "CELLSIZEY")
		
		cellTup = (cellX, cellY)
		cellSizes.append(cellTup)
		
		desc = arcpy.Describe(raster)
		
		xmin = desc.extent.XMin
		xmax = desc.extent.XMax
		ymin = desc.extent.YMin
		ymax = desc.extent.YMax
		
		myTup = (xmin, xmax, ymin, ymax)
		boundsList.append(myTup)
	
	if not boundsList or not all(boundsList):
		print "\nError: The geographic bounds were not identical for all of the layers\n"
		print "Terminating program\n"
		sys.exit(1)
	
	if cellSizes and all(cellSizes):
		print "Done!\nRaster layers validated\nGeographic bounds and cell sizes are identical.\n\n"
	elif not cellSizes or not all(cellSizes):
		print "\nError: The cell sizes between raster layers were not all the same.\n\n"
		sys.exit(1)
		
def remove_prefix(text, prefix):
	# Removes prefix from string
	return text[len(prefix): ]
	
def clip(rasters, fc, folder):
	# Clips the raster layers to min and max bounds of feature class.
	print "\n\nClipping raster layers to provided feature class..."
	
	# Gets the minimum and maximum X and Y values to get rectangle of feature class.
	desc = arcpy.Describe(fc)
		
	xmin = desc.extent.XMin
	xmax = desc.extent.XMax
	ymin = desc.extent.YMin
	ymax = desc.extent.YMax
		
	rect = str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax)
	
	# For each raster file in directory
	for raster in rasters:
		ras = None
		if raster.startswith("prj_"):
			# Remove the "prj_" prefix that was added previously.
			ras = remove_prefix(raster, "prj_")
			
			# Raster layer filename must be less than 9 characters + the four added below (to make 13)
			assert len(ras) <= 9, "Input and output filenames for clipping cannot be > 13 characters in length"
			outR = os.path.join(folder, "clp_" + ras)

		else:
			# If raster layer filename doesn't start with "prj_"
			# Filename must be less than 9 characters + the four added onto the new filenames below.
			assert len(raster) <= 9, "Input and output filenames for clipping cannot contain > 13 characters"
			outR = os.path.join(folder, "clp_" + raster)
		
		# Clip the raster layers
		arcpy.Clip_management(raster, rect, outR, fc,\
			"#", "NONE", "MAINTAIN_EXTENT")
	
	print "Done!"
	
def reproject(rasters, epsg, datum, resamp, folder):
	# Reprojects the raster layers to the specified epsg.
	
	print "\nReprojecting raster layers..."

	# For each raster layer file
	for raster in rasters:
	
		# Add "prj_" prefix to filename for output
		outR = os.path.join(folder, "prj_" + raster)
				
		# Project Raster tool.
		arcpy.ProjectRaster_management(raster, 
						outR, 
						arcpy.SpatialReference(epsg), 
						resamp, 
						"#", 
						datum, 
						"#", 
						"#")
	
	print "Done!\n\n"
		
def createFolder(optdir):
	# Create directory if it doesn't already exist.
	try:
		if not os.path.exists(optdir):
			os.makedirs(optdir)
	except OSError:
		print "Error creating directory " + directory
	
def getRasterList(wildcard):
	# Get list of all raster filenames in directory.
	# Wildcard can be used to select subset of raster files.
	if wildcard:
		r = arcpy.ListRasters(wildcard)
	else:
		r = arcpy.ListRasters()
	return r
	
	
def parseArgs():
	# Set command-line arguments.
	parser = argparse.ArgumentParser(description="This is a Python2.7 script to prepare raster data for use with MAXENT")
	
	requiredArgs = parser.add_argument_group("Required arguments")
	optionalArgs = parser.add_argument_group("Optional arguments")
	
	requiredArgs.add_argument("-w", "--ws",
					required=True,
					type=str,
					help="Set the path to the workspace")
	requiredArgs.add_argument("-f", "--fc",
					required=True,
					type=str,
					help="Specify feature class file (e.g., shapefile) to clip raster layers to")
								
	optionalArgs.add_argument("-p", "--pattern",
					required=False,
					type=str,
					default=None,
					help="Specify search pattern for raster files in ws directory")
	optionalArgs.add_argument("-d", "--datum",
					required=False,
					type=str,
					default="NAD_1983_To_WGS_1984_5",
					help="Set the datum for the geographic transformation; default = NAD_1983_To_WGS_1984_5")
	optionalArgs.add_argument("-e", "--epsg", 
					required=False,
					type=int,
					default=4269,
					help="Set the spatial reference (epsg #) for the output coordinate system; "
					"default = 4269 (NAD83)")
	optionalArgs.add_argument("-r", "--resampling",
					required=False,
					type=str,
					default="CUBIC",
					help="Set the resampling type. Options: [ NEAREST || BILINEAR || CUBIC || MAJORITY ] "
					"default = CUBIC; CUBIC & BILINEAR are for conintuous data; others are for categorical")
	optionalArgs.add_argument("-j", "--prj",
					required=False,
					type=str,
					default="reprj",
					help="Specify output directory for reprojected rasters")
	optionalArgs.add_argument("--reprj",
					action="store_false",
					default=True,
					help="Boolean; Toggles off the Project Raster function")
	optionalArgs.add_argument("-c", "--clipped",
					required=False,
					type=str,
					default="clipped",
					help="Specify output directory for clipped rasters")
	optionalArgs.add_argument("--clip_off",
					action="store_false",
					default=True,
					help="Boolean; Toggles off clip raster function if used")

	a = parser.parse_args()
	return a

if __name__ == "__main__":
	main()
	sys.exit(0)
	
