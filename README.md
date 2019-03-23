# firefox-bookmarks-reducer
Came across some HTML and JSON bookmark exports on my external drive. Wanted to combine them. This is that effort.

## Instructions
1. Clone the repository.
1. Copy the reduce.py file into the directory containing multiple HTML and JSON files that have been created when exporting bookmarks from Firefox.
1. Not yet done, so when I figure that out, I'll update the instructions.

## Current Behavior
The reduce.py script scans the current directory, including subdirectories of the directory it is run in. However, only the bookmarks in HTML files
are subject to ingestion. JSON files being recognized by name only, and a // TODO output line generated.

The bookmarks that can be imported using xml.etree.ElementTree.fromstring() or brute forced on failing the ElementTree approach, are then combined
and sorted at the end, with a final output of those joined bookmarks. No duplicates are removed yet. Yes, this duplicate removal is a // TODO item.

## // TODO
1. Ingest JSON file bookmarks.
1. Reduce HTML + JSON bookmarks list.
1. Export reduced list to external file (or standard output).
   1. Format (HTML, JSON, CSV, ???) not determined. So... determine that.
