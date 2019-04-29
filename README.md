# arcGIS
Scripts for processing arcGIS files.


## raster2maxent.py  

raster2maxent.py batch processes a directory of raster files (e.g., from worldclim.org).  
First, it reprojects them to a user-specified coordinate system (--epsg option).  
Then, it clips them to the min/max bounds of a feature class.  
Finally, it validates that all layers have the same dimensions and cell sizes (a reqiurement of MAXENT).  

### Usage: 
```raster2maxent.py [--ws path\to\workspace] [--fc path\to\featureClass] [optional_arguments...]```  

```
python raster2maxent.py -h

Required arguments:  
-w, --ws [path\to\workspace]: Specify path to workspace containing raster files.  Uses windows paths. E.g., C:\Users\$USER\Desktop  
-f, --fc [path\to\featureClass]: Specify path to feature class shapefile to clip to. E.g., C:\Users\$USER\Desktop\myFC.shp  

Optional Arguments:  
-p, --pattern [STRING]: Specify a wildcard to subset certain raster files in the ws for analysis (default = None).  E.g., *wgs84.tiff  
-d, --datum [STRING]: Set the datum for the geographic transformation during Project Raster (default = NAD_1983_To_WGS_1984_5)  
-e, --epsg [INTEGER]: Set the spatial reference (epsg #) for the output coordinate system during Project Raster. Default = 4269 (NAD83)  
-r, --resampling [ NEAREST || BILINEAR || CUBIC || MAJORITY ]: Set the resampling type when reprojecting raster (default = CUBIC)  
-j, --prj [path\to\outputPRJdir]: Set the output directory for reprojected raster layers (default = reprj)  
-c, --clipped [path\to\outputClipped]: Specify output directory for clipped rasters (default = clipped). DON'T USE ABSOLUTE PATHS HERE!  
--reprj BOOLEAN: Toggles off the Project Raster function. Toggle this if you don't want to reproject the raster layers.  
--clip_off BOOLEAN: Toggles off the clip raster function. For debugging/testing only. 
-h, --help BOOLEAN: Shows this help menu and exits.  
```  

### Dependencies  

```
Python 2.7  
Also must have ArcGIS 10 and the arcpy module installed.  
```  




