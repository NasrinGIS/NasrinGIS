"""
Modified by Andrew Ringeri 22-Mar-2021

Script to setup as a toolbox script in ArcGIS Pro.
Will query visible (check boxed) map layers and create assets in Assetic for assets that have empty Asset_ID attributes.
This example assumes a versioned geodatabase
Requires asset_esri v1.0.1.4 or later
"""
import arcpy
import sys
# check if this is first time the script has been run in this arcPro session
# it's a bit crass, but effective.
if 'assetic_esri' not in sys.modules:
    initiate = True
else:
    # The script has been run previously so the config is already loaded
    initiate = False
import assetic_esri
import os


def main(layer):
    """
    For the given layer's selected features
    create a corresponding asset in Assetic and update the feature with
    the asset friendly asset id, or the assetic internal asset guid.
    Versioned editing is assumed.  A new edit session is opened for the layer
    edit
    Assumes the xml config file has the layer name (as appears in the TOC)
    :param layer: the layer to process
    """
    # Initialise the assetic_esri library.  It will read the config files etc
    if initiate == True:
        # Script running for first time this session so get settings
        arcpy.AddMessage("Initiating Assetic ESRI configuration and logging")
        if not initasseticesri():
            return  
 
    # initialise assetic esri tools for layers
    tools = assetic_esri.LayerTools()
 
    # get workspace
    featuredesc = None
    desc = arcpy.Describe(layer)
    featuredesc = desc.featureClass
    count = len(layer.getSelectionSet())
    arcpy.env.workspace = featuredesc.path
    # create edit session
    edit = arcpy.da.Editor(arcpy.env.workspace)
    edit.startEditing(False,True)
    edit.startOperation()
    # execute asset creation
    arcpy.AddMessage("Processing layer: {0}, {1} Selected Features".format(
        layer.name,count))
    tools.create_asset(layer)
    # finalise
    edit.stopOperation()
    edit.stopEditing(True)


def initasseticesri():
    """
    initialise the helper module assetic_esri
    sets the paths to the xml config and ini files
    """
    appdata = os.environ.get("APPDATA")
    inifile = os.path.abspath(appdata + "\\Assetic\\assetic_sandbox.ini")
    logfile = os.path.abspath(appdata + "\\Assetic\\addin.log")
    xmlfile = os.path.abspath(appdata + "\\Assetic\\arcmap_edit_config.xml")
    try:
        ae = assetic_esri.Initialise(xmlfile,inifile,logfile,"Debug")
    except Exception as ex:
        print("Error initialising Addin: {0}".format(ex))
        return False
    return True
 
 
if __name__ == "__main__":

    fieldname = 'Asset_ID'
    project = arcpy.mp.ArcGISProject("CURRENT")
    projectmap = project.listMaps("Map")[0]

    for lyr in projectmap.listLayers():
        whereclause = """{0} = ''""".format(arcpy.AddFieldDelimiters(lyr, fieldname))  # empty Asset_ID
        arcpy.AddMessage(f"{lyr.name} is {lyr.visible}")

        if lyr.visible:  # run only layers that are visible (checkbox)
            
            try:
                arcpy.SelectLayerByAttribute_management(in_layer_or_view=lyr, selection_type="NEW_SELECTION",
                                                where_clause=whereclause)
                main(lyr)

            except TypeError:
                arcpy.AddMessage(f"{lyr.name} does not contain assets with empty {fieldname}")
