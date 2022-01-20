#
#   Run with python 3.6 install with ArcGIS Pro
#   Usage: "c:\Program Files\ArcGIS\Pro\bin\Python\Scripts\propy.bat" download_photos_1_truck.py <output_folder> <login> <password>
#
from arcgis.gis import GIS
import os
import datetime
import traceback
import sys


print("Start..")

login = sys.argv[1]
pwd = sys.argv[2]


featurelayer_ids = ['a217383770244c418bafb02bc3466278','256bc0c6be2b44c7ac0ad73ad16a0d97']  #Validation_Notes and AssetValiation_WMap_WFL1

output_folder = os.path.dirname(os.path.abspath(__file__))+os.sep+'photos'
if not os.path.isdir(output_folder):
    os.mkdir(output_folder) 

try:

    print("\nScript Started @  " +datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p"))   

    gis = GIS("https://www.arcgis.com", login, pwd)

    for fid in featurelayer_ids:

        flyr = gis.content.get(fid)
        
        for lyr in flyr.layers:
            lyrname = lyr.properties.name
            print(lyrname)

            if lyr.properties["hasAttachments"]!=True:
                print("Layer does not have attachments enabled!")
                continue

            rows = lyr.query(where="1=1",out_fields='*',return_geometry=False)
            
            for row in rows:

                oid = row.attributes['OBJECTID']
                if 'Asset_ID' in row.attributes:
                    assetid = row.attributes['Asset_ID']
                else:
                    assetid = "{0}_OBJECTID_{1}".format(row.attributes['Asset_Type'], oid)
                    
                photos = lyr.attachments.get_list(oid)
                n=0
                for p in photos:
                    n=n+1
                    photo_id = p['id']
                    photo_name = p['name']
                    filename = output_folder +os.sep +photo_name
                    new_filename = output_folder +os.sep +lyrname+ '_'+ assetid+"_" +str(n) +'.jpg'
                    if not os.path.exists(new_filename):
                        lyr.attachments.download(oid=oid, attachment_id=photo_id, save_path=output_folder)
                        print('downloading {0}'.format(new_filename))
                        os.rename(filename ,new_filename)
                    else:
                        print('{0} already exist!'.format(new_filename))
                        
                    if n == len(photos):
                        n=0
        
        
except:
    errors = traceback.format_exc()
    print(traceback.format_exc())

print("Script ended @  " +datetime.datetime.now().strftime("%d-%m-%Y %H:%M %p"))
