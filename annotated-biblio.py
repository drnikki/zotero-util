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
library_type = 'user'

# Import the libraries we'll need and initialize
from HTMLParser import HTMLParser
from pyzotero import zotero
import pprint # for testing because I'm bad at python.

pp = pprint.PrettyPrinter(indent=4)
zot = zotero.Zotero(library_id, library_type, api_key)
htmlparser = HTMLParser()

# This is configured to search the library for all items with a given tag.
# Every item with this tag will be included in the bibliography
# You can modify this by changing the search parameter. There is a great
# reference in the PyZotero docs: http://pyzotero.readthedocs.io/en/latest/index.html?highlight=search%20parameters#zotero.Zotero.add_parameters
items = zot.items(sort='creator',direction='asc',tag='592-ethics')

# items() returns a list of dicts, but we need a dict of dicts because we're going
# to be doing two searches and merging the results
allItems = dict()

# Put them into a dict keyed by their zotero key.
for item in items:
     # pp.pprint(item['data'])
     # item[data] entries look like this: https://gist.github.com/drnikki/483fbb3f933427b1a0af9b96237b0615
     allItems[item['data']['key']] = item['data']
     # if you want to see just item types and their keys, you can run:
     # print('Item: %s | Key: %s') % (item['data']['title'], item['data']['key'])

# Make a second API call. This time, grab all notes tagged "annotation."
# This works because in my library Items and Notes
# don't share tags, so I know that _only_ Notes will be returned.
items = zot.items(tag='annotation')

# Do the same thing so that we have a dict of notes.  These two dicts will have
# items sharing the same item key. This is how we'll match the note to the item.
allNotes = dict()
for item in items:
     allNotes[item['data']['parentItem']] = item['data']

# This is not performant, but it is effective.
# I am very sorry for the Zotero API, but these aren't _too_ big. 2 + #of item API calls per run
# For each Item, we're going to go grab the formatted citation
# and then if there's a corresponding Annotation, append that.

# At this point, we have two dicts (or associative arrays, if you come from PHP land)
# one with all items in it, and one with all notes in it.  We're going to go
# BACK to the zotero API to get a formatted citation.
bib = dict()
for key, item in allItems.iteritems():
    zot.add_parameters(limit='None',content='bib')
    bib[key] = dict()
    # this adds the formatted citation
    bib[key]['item'] = zot.item(key)
    #pp.pprint(bib[key]['item'])
    if key in allNotes:
        # this attaches the note to the item.
        bib[key]['note'] = allNotes[key]['note']

# ----- fancy HTML part -----
import dominate
from dominate.tags import *
from dominate.util import raw

doc = dominate.document(title='Annotated Bibliography')

# make an HTML document!
with doc.head:
    link(rel='stylesheet', href='styles.css')

# in the HTML document
with doc:
    # for each entry that we created above:
    for key, entry in bib.iteritems():
        # we're going to make a div to hold the whole thing
        with div(cls='one-entry'):
            # i've been having some serious encoding problems.
            temp=entry['item'][0]
            # and then print the raw html returned from Zotero
            raw(temp)
            # then, if there's a note, add that too.
            if 'note' in entry:
                with div():
                    attr(cls='note')
                    # i've been having some serious encoding problems
                    temp=entry['note']
                    raw(temp)

print(doc)
