# Works with Python 2.7.8
import logging
import traceback
import sys, os
import json
import os
import datetime
import requests
import csv
import arcpy

# Defines the entry point into the script
def main(argv=None):



    #Parameters
    output_gdb = r'J:\GISDATA\GIS_USER_DATA\GIS\ArcGISEnterpriseWebApps\Trees_Audit\Trees_Audit.gdb'

    sde = r'J:\GISDATA\GIS_USER_DATA\GIS\ArcGISEnterpriseWebApps\Trees_Audit\cowgis.sde'
    sde_layers = {}
    sde_layers = {"Trax_Whit_Trees" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace\GIS_2020.SDE.TRAX_Whit_Trees", "outfields" : "Asset_ID, Asset_Name, Asset_Type"},
                 "SignificantTree" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace\GIS_2020.SDE.SignificantTree", "outfields" : "Assetic_Id, Asset_Sub, Species"}}  
  
    layers = {"V4_Park_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V4.gdb\Park_Tree", "outfields" : "Asset_ID, Asset_Subtype, Species, Street, Suburb"},
              "V4_Significant_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V4.gdb\Significant_Tree", "outfields" : "Asset_ID, Asset_Type, Species"},
              "V4_Street_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V4.gdb\Street_Tree", "outfields" : "Asset_ID, Asset_Subtype, Species"},
              "V5_Park_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V5.gdb\Park_Tree", "outfields" : "Asset_ID, Asset_Subtype, Species"},
              "V5_Significant_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V5.gdb\Significant_Tree", "outfields" : "Asset_ID, Asset_Type, Species"},
              "V5_Street_Tree" : {"featureclass": r"J:\GISDATA\GIS_ASSET_DATA\P&G_AssetNew\CITYWIDE_Tree_V5.gdb\Street_Tree", "outfields" : "Asset_ID, Asset_Subtype, Species"},
              "Rural_Roadside_2018" : {"featureclass": r"J:\GISDATA\GIS_USER_DATA\GIS\ArcGISEnterpriseWebApps\Trees_Audit\data\4459_180730_All_Data.shp", "outfields" : "ID, ID2, GenusSpeci, CommonName"},
                }  
    #Start log
    _setupLogging()
    arcpy.env.overwriteOutput = True
    logging.info("\nScript Started @  " +datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p"))

    #SDE Layers
    for layer in sde_layers:
        details = sde_layers[layer]
        fc = details["featureclass"]
        outfields = details["outfields"].upper()
        
        print("Creating {0} from  {1}".format(layer, fc))
        name = layer.replace(' ','_').replace('-','') #remove spaces and dashes
        arcpy.FeatureClassToFeatureClass_conversion(sde+os.sep+fc, output_gdb, name)

        logging.info("... Projecting {0} from GDA2020 back to GDA94".format(os.path.basename(fc)))
        in_sr =arcpy.Describe(output_gdb+os.sep+name).spatialReference.name
        logging.info("Featureclass is coordinates in: {0})".format(in_sr))
        if in_sr=='GDA2020_MGA_Zone_55':
            GDA_94 = arcpy.SpatialReference("GDA 1994 MGA Zone 55")
            TRANS_METHOD = "GDA_1994_To_GDA2020_NTv2_2_Conformal_and_Distortion"
            arcpy.Project_management(output_gdb+os.sep+name, output_gdb+os.sep+name+"_GDA94", GDA_94, TRANS_METHOD)
        else:
            logging.error("Featureclass not in GDA2020_MGA_Zone_55")

        fieldnames = []
        for fld in arcpy.ListFields(output_gdb+os.sep+name+"_GDA94"):
            if (not fld.editable) or (fld.type in ("Geometry", "OID")): continue
            fieldnames.append(str(fld.name.upper()))
        outfieldsnames = outfields.replace(' ','').split(',')

        #Delete fields that are not required
        drop_fields = list(set(fieldnames) - set(outfieldsnames))
        arcpy.DeleteField_management(output_gdb+os.sep+name+"_GDA94", drop_fields)


    #Variation Layers
    for layer in layers:
        details = layers[layer]
        fc = details["featureclass"]
        outfields = details["outfields"].upper()
        
        print("Creating {0} from  {1}".format(layer, fc))
        name = layer.replace(' ','_').replace('-','') #remove spaces and dashes
        arcpy.FeatureClassToFeatureClass_conversion(fc, output_gdb, name)


        fieldnames = []
        for fld in arcpy.ListFields(output_gdb+os.sep+name):
            if (not fld.editable) or (fld.type in ("Geometry", "OID")): continue
            fieldnames.append(str(fld.name.upper()))
        outfieldsnames = outfields.replace(' ','').split(',')

        #Delete fields that are not required
        drop_fields = list(set(fieldnames) - set(outfieldsnames))
        arcpy.DeleteField_management(output_gdb+os.sep+name, drop_fields)

    #Close log
    logging.info("Script ended @  " +datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p"))





def _setupLogging():
    
    try:
        script_path = os.path.abspath(__file__)                                 #eg. c:\hwc_refresh\scripts\prepare_featureclass.py
        script_basename = os.path.basename(os.path.abspath(__file__))           #eg. prepare_featureclass.py
        log_basename = script_basename.replace('.py','.log')  
        log_path = os.path.dirname(os.path.abspath(__file__)) +os.sep + "log"
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file = log_path +os.sep +log_basename
        logging.getLogger("requests").setLevel(logging.WARNING)  #https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
        logging.getLogger('').handlers = []
        logging.basicConfig(filename=log_file, filemode="w", level='INFO', format='%(asctime)s %(levelname)-5s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler())
    except:
        logging.error(traceback.format_exc())
        
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
