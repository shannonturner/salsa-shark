import cookielib, re, urllib, urllib2

# This was my first major Python program I wrote - I was very new to Python at the time.  Looking over it now, there are a LOT of refinements and code-tightening that *could* be done.

# I wrote this because we needed to upload several thousand objects (mostly events) into Salsa in a highly customized way such that a regular import wouldn't be enough.
# Since you can't use the built-in import to import customizations that span multiple tables (such as reminder emails for mass-imported events), I had to create this program.

# This program can be used for any type of Salsa object, whether the object spans one or multiple tables.

# Common uses are:  upload a large number of events with customized reminder emails set for each event
#                   upload campaign managers with roles created (passwords need to be set manually)
#                   upload chapters

def SalsaNewObject(baseurl, api_fields):

    apihandle = base_handle.open(baseurl + '/save',urllib.urlencode(api_fields))
    
    source = apihandle.read()
    
    return source

def SalsaGetObjects(baseurl, object_fields):

    apihandle = base_handle.open(baseurl + '/api/getObjects.sjs',urllib.urlencode(object_fields))

    source = apihandle.read()

    return source

def SalsaSaveObject(baseurl, parameters):

    # pass parameters as a string formatted like this:
    # &object=event&param1=value1&param2=value2

    apihandle = base_handle.open(baseurl + '/save?xml' + parameters)

    source = apihandle.read()

    return source

def CSVParse(one_row):

    ' CSVParse: Not called directly; helper function called by GetObjectsFromCSV() '

    spreadsheet_values = []

    for m in re.finditer("(.+?)$", one_row):
        spreadsheet_values.append(m.group(1))

    return spreadsheet_values

def GetObjectsFromCSV(filename):

    with open(filename) as spreadsheet_file:
        spreadsheet = spreadsheet_file.read()
        spreadsheet = spreadsheet.split("\n")

    spreadsheet_values = []
    objects = {}
    object_details = []

    for line in spreadsheet:
        
        spreadsheet_values.extend(CSVParse(line))

    header_row = spreadsheet_values.pop(0)
    header_row = header_row.split(",")

    num_rows = len(spreadsheet_values)
    num_cols = len(header_row)

    for row_iter in range(num_rows):

        one_set = spreadsheet_values[row_iter].split(",")

        for col_iter in range(num_cols):

            object_details.append((header_row[col_iter], one_set[col_iter]))

        objects["row" + str(row_iter)] = dict(object_details)

    return objects

def SalsaDictToString(row_number, objects, main_object_type): 

    parameters = ""

    salsa_list = dict.items(objects)

    try:
        object_type = salsa_list.pop(salsa_list.index(("object", main_object_type)))
        object_type = "&" + object_type[0] + "=" + object_type[1]

    except ValueError, e:
        print e

    for (key, value) in salsa_list:
        parameters += "&" + key + "=" + value

    parameters = row_number + "__" + object_type + parameters 

    parameters = parameters.replace(" ","+")

    return parameters

def ParseSalsaMessages(source):

    if re.search('<success.*key="(\d+)">', source):
        m = re.search('<success.*key="(\d+)">', source)
        object_key = m.group(1)
    else:
        print "Match for success object key failed.  Reason:", source
        object_key = "err"

    return object_key

def SalsaImportSingleTable(objects_from_csv, uploaded_objects_file, object_type, baseurl): 

    objects = GetObjectsFromCSV(objects_from_csv)

    objects_as_list = []

    uploaded_objects = open(uploaded_objects_file, "a")
    uploaded_objects.write("From " + objects_from_csv + ":\r\n")

    for row in objects:
        objects_as_list.append(SalsaDictToString(row, objects[row], object_type))

    objects_as_list.sort()

    for x in xrange(len(objects_as_list)):
        for y in xrange(len(objects_as_list)):
            objects_as_list[x] = objects_as_list[x].replace("row" + str(y) + "__","")

    for parameters in objects_as_list:

        source = SalsaSaveObject(baseurl, parameters)
        object_key = ParseSalsaMessages(source)

        uploaded_objects.write(str(object_key) + "\r\n")

        print object_type + ":" + str(object_key) + " created (" + parameters + ")"

    uploaded_objects.close()

    return

def SalsaImportMultiTables(objects_from_csv, child_objects_from_csv, uploaded_objects_file, object_type, child_object_type, baseurl):

    objects = GetObjectsFromCSV(objects_from_csv)
    child_objects = GetObjectsFromCSV(child_objects_from_csv)

    objects_as_list = []
    child_objects_as_list = []

    for row, child_row in zip(objects, child_objects):

        objects_as_list.append(SalsaDictToString(row, objects[row], object_type))
        child_objects_as_list.append(SalsaDictToString(child_row, child_objects[child_row], child_object_type))
    
    objects_as_list.sort()
    child_objects_as_list.sort()

    for x in xrange(len(objects_as_list)):
        for y in xrange(len(objects_as_list)):
            objects_as_list[x] = objects_as_list[x].replace("row" + str(y) + "__","")

    for x in xrange(len(child_objects_as_list)):
        for y in xrange(len(child_objects_as_list)):
            child_objects_as_list[x] = child_objects_as_list[x].replace("row" + str(y) + "__","")

    uploaded_objects = open(uploaded_objects_file, "a")
    uploaded_objects.write("From " + objects_from_csv + ":\r\n")
    
    for parameters, child_parameters in zip(objects_as_list, child_objects_as_list):

        child_parameters = child_parameters.split("&")
        
        for x in xrange(0, child_parameters.count("object=" + child_object_type)):
            child_parameters[child_parameters.index("object=" + child_object_type)] = str(x) + "-SVT-" + child_parameters[child_parameters.index("object=" + child_object_type)]

        child_parameters.sort()
        
        child_parameters = '&'.join(child_parameters)

        for x in xrange(0, 10):
            child_parameters = child_parameters.replace(str(x) + "-SVT-","")

        source = SalsaSaveObject(baseurl, parameters)
        object_key = ParseSalsaMessages(source)

        print str(object_key) + " saved."

        uploaded_objects.write(str(object_key) + "\r\n")

        if ('SVT-OBJECT-KEY' in child_parameters):
            child_parameters = child_parameters.replace("SVT-OBJECT-KEY", object_key)
        
        source = SalsaSaveObject(baseurl, child_parameters)

    uploaded_objects.close()

    return

###############################
### Configuration Variables ###
###############################

jar = cookielib.CookieJar()

username = '' # your Salsa Login Username
password = '' # your Salsa Login Password

authentication = {'email': username,
                  'password': password }

base_handle = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

# Dev / Live Toggle
baseurl = 'https://hq-salsa.wiredforchange.com' # production / live
#baseurl = 'https://sandbox.salsalabs.com' # dev / sandbox

apihandle = base_handle.open(baseurl + '/api/authenticate.sjs',urllib.urlencode(authentication))


## Important things to keep in mind (Most of these are specific to Salsa, NOT specific to the SalsaShark - but they've been helpful to keep in mind while using this program so I thought they were worth including):

## You can only upload one type of object at a time; if you're using a child object, make sure it matches.

## Make sure there aren't any commas, ampersands, carriage returns, or newlines in the values of your CSVs; the first breaks the CSV matching and Salsa gets confused by the latter three

## If the objects you upload are part of a chapter, make sure you've assigned it to the right one.
## If you need to change the chapter for any reason, you'll need to have explicit chapter privileges on the campaign_manager you're logged in as to change the chapter.  Otherwise, it won't work and won't say why.

## If you need to make edits to already-uploaded objects, you only have to include the fields you want to edit.
## You won't ever change an object (ex: changing an event to a chapter), but you still need to include the object type so that the program can tell Salsa which table to save to.
## Saving a new objects uses key 0; editing an already-existing object uses that object key

## Excel behaves badly:
## Make sure you delete the final (blank) row in TextPad (not Excel!) before runtime
## If you're including javascript in an object's footer, Excel will put single quotes around these.  Be sure to remove them in TextPad before runtime or it won't be saved properly. 

##################################
# Example How to Use SalsaShark: #
##################################

#objects_from_csv = "events.csv"
#child_objects_from_csv = "event_email_triggers.csv"
#uploaded_objects_file = "log.txt"
#object_type = "event"
#child_object_type = "event_email_trigger"

#SalsaImportSingleTable(objects_from_csv, uploaded_objects_file, object_type, baseurl)
#SalsaImportMultiTables(objects_from_csv, child_objects_from_csv, uploaded_objects_file, object_type, child_object_type, baseurl)

#print "All done"
