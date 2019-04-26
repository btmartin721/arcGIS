##==================================================================
## Process Global Climate Model (GCM) data from worldclim.org
## 


import arcpy
import argparse
import os
import sys




def main():
	
	args = parseArgs()

	arcpy.env.workspace = args.ws	
	
	rasters = getRasterList(args.pattern)
	
	prjFolder = os.path.join(args.ws, args.prj)

	if args.reprj:
		# Makes new directory to store output from reprojection.
		# Can be toggled off if already have files in correct coordinate projection.
		createFolder(prjFolder)
		reproject(rasters, args.epsg, args.datum, args.resampling, prjFolder)
	
	
	if args.clip_off:
		clipFolder = os.path.join(args.ws, args.clipped)
		arcpy.env.workspace = prjFolder
		rasters = getRasterList(None)
		createFolder(clipFolder)
		
		clip(rasters, args.fc, clipFolder)
		
	
	
def clip(rasters, fc, folder):
	
	desc = arcpy.Describe(fc)
		
	xmin = desc.extent.XMin
	xmax = desc.extent.XMax
	ymin = desc.extent.YMin
	ymax = desc.extent.YMax
		
	rect = str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax)
	
	for raster in rasters:
		outR = os.path.join(folder, "clip_" + raster)
		arcpy.Clip_management(raster, rect, outR, )
	
def reproject(rasters, epsg, datum, resamp, folder):
	for raster in rasters:
		outR = os.path.join(folder, "prj_" + raster)
		arcpy.ProjectRaster_management(raster, 
									outR, 
									arcpy.SpatialReference(epsg), 
									resamp, 
									"#", 
									datum, 
									"#", 
									"#")
	
def createFolder(optdir):
	try:
		if not os.path.exists(optdir):
			os.makedirs(optdir)
	except OSError:
		print "Error creating directory " + directory
	
def getRasterList(wildcard):
	
	if wildcard:
		r = arcpy.ListRasters(wildcard)
	else:
		r = arcpy.ListRasters()
	return r
	
	
def parseArgs():
	parser = argparse.ArgumentParser(description="This is a Python2.7 script to process bioclim raster data")
	
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
	
