salsa-shark
===========

Python script to mass import objects into Salsa while preserving internal table structure.  Example: Allows you to mass create events and their corresponding reminder emails.

(You must have an account at http://www.salsalabs.com/ to use this.)

The import tool standard to Salsa is buggy and doesn't allow you to create child objects at the time of creation; a big problem if you need to create over 1000 events, each with their own customized thank-you and reminder emails.

This was my first major Python program I wrote - I was very new to Python at the time.  Looking over it now, there are a LOT of refinements and code-tightening that *could* be done.

This program can be used for any type of Salsa object, whether the object spans one or multiple tables.

Common uses are:  upload a large number of events with customized reminder emails set for each event
                  upload campaign managers with roles created (passwords need to be set manually)
                  upload chapters

Before using this, you should have at least some knowledge about Salsa's table structure and how everything works.
Their documentation isn't amazing by any stretch, but it's good enough: http://www.salsalabs.com/p/salsa/website/public2/commons/dev/docs/api/?_u
Be sure to request a sandbox/developer account so you can test everything before you go live.

Important things to keep in mind (Most of these are specific to Salsa, NOT specific to the SalsaShark - but they've been helpful to keep in mind while using this program so I thought they were worth including):

You can only upload one type of object at a time; if you're using a child object, make sure it matches.

Make sure there aren't any commas, ampersands, carriage returns, or newlines in the values of your CSVs; the first breaks the CSV matching and Salsa gets confused by the latter three

If the objects you upload are part of a chapter, make sure you've assigned it to the right one.
If you need to change the chapter for any reason, you'll need to have explicit chapter privileges on the campaign_manager you're logged in as to change the chapter.  Otherwise, it won't work and won't say why.

If you need to make edits to already-uploaded objects, you only have to include the fields you want to edit.
You won't ever change an object (ex: changing an event to a chapter), but you still need to include the object type so that the program can tell Salsa which table to save to.
Saving a new objects uses key 0; editing an already-existing object uses that object key

Excel behaves badly:
Make sure you delete the final (blank) row in TextPad (not Excel!) before runtime
If you're including javascript in an object's footer, Excel will put single quotes around these.  Be sure to remove them in TextPad before runtime or it won't be saved properly. 

### Example How to Use SalsaShark:

objects_from_csv = "events.csv"
child_objects_from_csv = "event_email_triggers.csv"
uploaded_objects_file = "log.txt"
object_type = "event"
child_object_type = "event_email_trigger"

## Use only one of the following functions at a time depending on which one you need: 

### Use this for when you just need to add/make changes to just one Salsa table.
SalsaImportSingleTable(objects_from_csv, uploaded_objects_file, object_type, baseurl)

### Use this when you need to add to two Salsa tables, for example events and event_email_triggers.
SalsaImportMultiTables(objects_from_csv, child_objects_from_csv, uploaded_objects_file, object_type, child_object_type, baseurl)
