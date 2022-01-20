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
    sde = r'J:\GISDATA\GIS_USER_DATA\GIS\Whittlesea_website\MyNeighbourhood\ArcGIS_Local_Information_On_Map\cowgis_GIS_2020.sde'
    
##    layers = {"Places of Interest" : {"featureclass": r"J:\GISDATA\GIS_USER_DATA\GIS\geodatabases\ArcSDE_Update.gdb\Facilities\Attractions","where": "",
##                                      "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##
##              "Schools" : {"featureclass": "J:\GISDATA\GIS_USER_DATA\GIS\geodatabases\ArcSDE_Update.gdb\Facilities\SchoolTypes", "where": "",
##                             "outfields" : "Full_Name, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"}}
    
##    layers = {"Places of Interest" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.Attractions","where": "",
##                                      "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##              
##              "Playgrounds" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Playground", "where": "",
##                               "outfields" : "NAME, Functional_Location_Name_L1, Address, LAST_MODIFIED"},
##              
##              "Swimming pools" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.SportingFacilities", "where": "SERVICE='Swimming Pool'",
##                                  "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##              
##              "Maternal and child health centres" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.MCH", "where": "",
##                                                     "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##              
    layers = { "Major parks" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Site",
                               "where": "Asset_Subtype = 'Major Community Parks' or Functional_Location_Name_L1 LIKE '%Recreation Reserve'",
                               "outfields" : "Functional_Location_Name_L1, Address, FACILITY, LAST_MODIFIED"},
##              
##              "Off-leash dog parks" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.DogOff_Leash", "where": "",
##                                       "outfields" : "NAME, ADDRESS, MELWAY, LAST_MODIFIED"},
##              
##              "Halls for hire" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.Hall", "where": "",
##                                  "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##              
##              "Kindergartens" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.Kindergarten", "where": "",
##                                  "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED, KINDERGARTEN_ENROLMENT"},
##              
              "Local parks" : {"featureclass": "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Site",
                               "where": "Asset_Subtype = 'Neighbourhood & Local Open Space' and Functional_Location_Name_L1 like '%Park%'",
                               "outfields" : "Functional_Location_Name_L1, Address, FACILITY, LAST_MODIFIED"}}
##              
##    layers = {"Public toilets" : {"featureclass": "GIS_2020.SDE.Infrastructure\GIS_2020.SDE.PublicToilets_NPTM", "where": "ManagedBy='COW'",
##                                  "outfields" : "Name, Address1, Town, URL_Modified, ManagedBy, LAST_MODIFIED"}}
##              
##              "Libraries" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.Library", "where": "",
##                             "outfields" : "NAME, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"},
##              
##              "Schools" : {"featureclass": "GIS_2020.SDE.Facilities\GIS_2020.SDE.SchoolTypes", "where": "",
##                             "outfields" : "Full_Name, ADDRESS, SUBURB, POSTCODE, MELWAY, WEBLINK, LAST_MODIFIED"}}

    park_facilities = {"BBQ" : "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.BBQ",
                       "Drinking Fountain" : "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Drinking_Fountain",
                       "Playground" : "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Playground",
                       "Seat" : "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Seats",
                       "Shelter" : "GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Shelter"}

    fc_site = r"GIS_2020.SDE.ParksOpenSpace_Assetic\GIS_2020.SDE.Site"    
    output_gdb = r'J:\GISDATA\GIS_USER_DATA\GIS\Whittlesea_website\MyNeighbourhood\ArcGIS_Local_Information_On_Map\ArcGIS_Local_Information_On_Map.gdb'

    #Start log
    _setupLogging()
    arcpy.env.overwriteOutput = True
    assetTypefields = []
    logging.info("\nScript Started @  " +datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p"))


    for layer in layers:
        details = layers[layer]
        fc = details["featureclass"]
        where = details["where"]
        outfields = details["outfields"].upper()
        print("Creating {0} from  {1} where clause -> {2}".format(layer, fc, where))
        name = layer.replace(' ','_').replace('-','') #remove spaces and dashes
        arcpy.FeatureClassToFeatureClass_conversion(sde+os.sep+fc, output_gdb, name, where)
#        arcpy.FeatureClassToFeatureClass_conversion(fc, output_gdb, name, where)

        fieldnames = []
        for fld in arcpy.ListFields(output_gdb+os.sep+name):
            if (not fld.editable) or (fld.type in ("Geometry", "OID")): continue
            fieldnames.append(str(fld.name.upper()))
        outfieldsnames = outfields.replace(' ','').split(',')
        #Layer-specific column values
        if layer=="Kindergartens":   #Add KINDERGARTEN_ENROLMENT URL column
            arcpy.AddField_management(output_gdb+os.sep+name, "KINDERGARTEN_ENROLMENT", "TEXT", "", "", 200)
            url = r"'https://www.whittlesea.vic.gov.au/community-support/children-and-families/kindergarten-applications'"
            arcpy.CalculateField_management(output_gdb+os.sep+name, "KINDERGARTEN_ENROLMENT", url, "PYTHON_9.3")
        if layer=="Off-leash dog parks":
            arcpy.management.JoinField(output_gdb+os.sep+name, "Functional_Location_Id_L1", sde+os.sep+fc_site, "Functional_Location_Id_L1", ["Address"])
            fields = [f.name for f in arcpy.ListFields(output_gdb+os.sep+name)]
            arcpy.CalculateField_management(output_gdb+os.sep+name, "ADDRESS", '!Address_1!', "PYTHON_9.3")
            arcpy.DeleteField_management(output_gdb+os.sep+name, ["Address_1"])  #remove join field
        #Add facilities for parks
        if layer=="Major parks" or layer=="Local parks":
  
            for facility in park_facilities:
                print("Adding {0} subtype field...".format(facility))

                fc = park_facilities[facility]
                
##                print("fc: " +sde+os.sep+fc)
##                a1 = [f2.name for f2 in arcpy.ListFields(sde+os.sep+fc)]
##                print(a1)
##                print("layer: +"+output_gdb+os.sep+name)
##                a2 = [f3.name for f3 in arcpy.ListFields(output_gdb+os.sep+name)]
##                print(a2)
                
                arcpy.JoinField_management(output_gdb+os.sep+name, "Functional_Location_Id_L1", sde+os.sep+fc, "Functional_Location_Id_L1", ["Asset_Type"])

            print("Add Facilities column")
            arcpy.AddField_management(output_gdb+os.sep+name, "FACILITY", "TEXT", "", "", 300)
            assetTypefields = [f.name for f in arcpy.ListFields(output_gdb+os.sep+name) if "Asset_Type_" in f.name]
            str_fieldnames = ",".join(assetTypefields)
            codeblock = '''def GetFacilities(values):
                output = []
                for v in values:
                    if v is not None:
                        if "shelter" in v.lower():
                            output.append("shelter")
                        else:
                            output.append(v.lower())
                s = ", ".join(output) 
                return s  '''
            str_fields = "!,!".join(assetTypefields)
            expression = "GetFacilities([!"+str_fields+"!])"
            arcpy.CalculateField_management(output_gdb+os.sep+name, "FACILITY", expression, "PYTHON_9.3", codeblock)
            arcpy.DeleteField_management(output_gdb+os.sep+name, assetTypefields)  #Remove Asset_Types columns

        #Delete fields that are not required
        drop_fields = list(set(fieldnames) - set(outfieldsnames)) + assetTypefields
        arcpy.DeleteField_management(output_gdb+os.sep+name, drop_fields)
                
        #Add last_modified column
        arcpy.AddField_management(output_gdb+os.sep+name, "LAST_MODIFIED", "TEXT", "", "", 20)
        today = "'{0}'".format(datetime.datetime.now().strftime("%d/%m/%Y"))
        arcpy.CalculateField_management(output_gdb+os.sep+name, "LAST_MODIFIED", today, "PYTHON_9.3")

        #Create point featureclass if polygon
        desc = arcpy.Describe(output_gdb+os.sep+name)
        if desc.shapeType=="Polygon":
            arcpy.CreateFeatureclass_management(output_gdb, name+"_point", "POINT", output_gdb+os.sep+name, "", "", desc.spatialReference)
            s_flds = ["SHAPE@XY"]
            i_flds = ["SHAPE@"]
            for f in arcpy.ListFields(output_gdb+os.sep+name):
                if (not f.editable) or f.type in ("Geometry", "OID"):
                    continue
                else:
                    s_flds.append(str(f.name))
                    i_flds.append(str(f.name))
                
            with arcpy.da.SearchCursor(output_gdb+os.sep+name, s_flds) as s_cursor:
                with arcpy.da.InsertCursor(output_gdb+os.sep+name+"_point",i_flds) as i_cursor:
                    for row in s_cursor:
                        i_cursor.insertRow(row)       


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
