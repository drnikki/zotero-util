# This script uses the zotero API to retrieve all notes in my library that
# have a certain tag. It then loads some parent data and writes the content of the
# note to the markdown file.

# export PYTHONIOENCODING=UTF-8
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# ^ https://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte#21190382

# Replace this string with your API key.
api_key = 'Jjxjxjxjxjxjxjxjxjxjxjxjxj'
# Replace this number with your Library ID
library_id = 12345678
# Replace this with the path of where you want the files to be saved.
path='/Users/your/path/to/wherever'

library_type = 'user' # leave this one alone unless you're sure

# Import the libraries we'll need
from pyzotero import zotero
import pprint # for testing because I'm bad at python.
import re  # for regex
# initialize some things
pp = pprint.PrettyPrinter(indent=4)
zot = zotero.Zotero(library_id, library_type, api_key)

# Grab all notes tagged "annotation."
# This works because in my library Items and Notes
# don't share tags, so I know that _only_ Notes will be returned.
# And these are all the annotations in the entire system. This does not include
# automatically extracted annotations because I haven't tagged them as such.
items = zot.items(tag='annotation')
# alternatively, you could pull everything that has itemType = 'note'
# items = zot.items(itemType='note')

# We are going to make a dict of notes, tagged by the key of the PARENT item
allNotes = dict()
for item in items:
     allNotes[item['data']['parentItem']] = item['data']
     # here are some testing outputs if you want to see what's happening:
     # pp.pprint(item['data'])
     # print('Item: %s | Key: %s') % (item['data']['title'], item['data']['key'])

# This is not terribly performat, really, but I haven't hit any API limits.
# I am very sorry for the Zotero API, but these aren't _too_ big. 1 + #of item API calls per run
# For each Item, we're going to go grab the formatted citation
# and then if there's a corresponding Note tagged annotation, append that.

# At this point, we have a dict (or associative array, if you come from another language)
# with all notes in it.  We're going to go back to
# the zotero API to get information about all the parent items.
bib = dict()
for key, note in allNotes.iteritems():
    zot.add_parameters(limit='None')
    # make a dict for this item
    bib[key] = dict()
    # this fetches the item data
    bib[key]['item'] = zot.item(key)
    # grab the title
    title = bib[key]['item']['data']['title']
    # do stuff to the title to get the filename
    # The title pattern is such that an item called "The Governance and Control of Open Source Software Projects"
    # will be saved as 'bib-The-Governance-and-Control-of-Open-Source-Software-Projects.md'
    filename = re.sub('[^a-zA-Z]+', '-', title)
    bib[key]['title'] = title
    bib[key]['filename'] = filename
    bib[key]['note'] = allNotes[key]['note']

    # generate the markdown file.
    # Open the filename (note you can change the type of file by replacing the .md below)
    # if this filename already exists, it will open it (I have not tested this!), otherwise it will create it.
    markdownFile = open(path + "/" + "bib-" + filename + ".md", 'w')
    # and then in the file:
    # the name of the item, the note
    markdownFile.write(bib[key]['title'])
    markdownFile.write('\n')
    # this is the arbitrary heading indicator that I use.
    # you can put any other characters that you want to in here.
    markdownFile.write('=============================')
    markdownFile.write('\n\n')
    markdownFile.write(bib[key]['note'])
    markdownFile.close()
