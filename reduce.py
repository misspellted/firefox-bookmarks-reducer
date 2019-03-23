import os
import re

from xml.etree import ElementTree as ET

class Bookmark(object):
    def __init__(self, link, text):
        self.link = link
        self.text = text

    def __repr__(self):
        return f"Bookmark(link=%s, text=%s)" % (self.link, self.text)

    def __lt__(self, other):
        return self.link < other.link

class BookmarkFileReader(object):
    def extension(self):
        return None

    def extractBookmarks(self, filePath):
        return None

class HtmlBookmarkFileReader(BookmarkFileReader):
    def extension(self):
        return ".html"

    def extractBookmarks(self, filePath):
        htmlBookmarks = list()

        with open(filePath, "r") as htmlFile:
            for line in htmlFile:
                stripped = line.strip()

                if stripped.startswith("<DT>"):
                    stripped = stripped[4:]

                    if stripped.startswith("<A "):
                        htmlBookmarks.append(stripped)

        return htmlBookmarks

class HtmlBookmarkParser(object):
    def extension(self):
        return ".html"

    def parseBookmarkText(self, bookmarkText):
        # Return the "not implemented" tuple (failure to parse a link).
        return (None, None)

class XmlHtmlBookmarkParser(HtmlBookmarkParser):
    def parseBookmarkText(self, bookmarkText):
        link, text = None, None

        try:
            element = ET.fromstring(bookmarkText)
            if "HREF" in element.attrib:
                link = element.attrib["HREF"]
                text = element.text

                # Copy the link as the text, if no contents between end of opening tag and opening of end tag.
                text = text if len(text) == 0 else link
            else:
                # Report the error message in the text field.
                text = "HREF attribute missing in HTML anchor element."
        except ET.ParseError as pe:
            # Report the error message in the text field.
            text = pe.message if hasattr(pe, "message") else str(pe)

        return (link, text)

class RgxHtmlBookmarkParser(HtmlBookmarkParser):
    def parseBookmarkText(self, bookmarkText):
        link, text = None, None

        hrefMatch = re.search(r"HREF=\".*?\"", bookmarkText)
        if not hrefMatch is None:
            link = hrefMatch.group()[6:-1]
        else:
            # Reporting the error message in the text field.
            text = "HREF attribute missing in HTML anchor element."

        tagMatch = re.search(r">.*?</A>", bookmarkText)
        if not tagMatch is None:
            firstMatch = tagMatch.group()

            # Copy the link as the text, if no contents between end of opening tag and opening of end tag.
            text = firstMatch[1:-4] if 5 <= len(firstMatch) else link
        else:
            # Reporting the error message in the text field.
            text = "Unable to match end of opening tag and opening of end tag of HTML anchor element."

        return (link, text)

def addReader(readers, reader):
    extension = reader.extension()

    if not extension in readers:
        readers[extension] = list()

    readers[extension].append(reader)

def addParser(parsers, parser):
    extension = parser.extension()

    if not extension in parsers:
        parsers[extension] = list()

    parsers[extension].append(parser)

def main():
    # Ready the available readers and parsers.
    readers = dict()

    addReader(readers, HtmlBookmarkFileReader())

    parsers = dict()

    addParser(parsers, XmlHtmlBookmarkParser())
    addParser(parsers, RgxHtmlBookmarkParser())

    # Generate a list of files that contain bookmarks.
    filePaths = list()

    for (directory, subdirectories, files) in os.walk("."):
        for file in files:
            filePaths.append(os.path.sep.join([directory, file]))

    # Import the bookmarks from each file.
    allBookmarks = list()
    allFailures = list()

    for filePath in filePaths:
        print(filePath)

        ignored, extension = os.path.splitext(filePath)

        if extension in parsers and extension in readers:
            fileReaders = readers[extension]
            fileParsers = parsers[extension]

            bookmarks = list()
            failures = list()

            # Use the first file reader (for now) to extract the bookmarks in the format of the file.
            fileBookmarks = fileReaders[0].extractBookmarks(filePath)

            for fileBookmark in fileBookmarks:
                link, text = None, None

                for fileParser in fileParsers:
                    link, text = fileParser.parseBookmarkText(fileBookmark)

                    if not link is None:
                        break

                if link is None:
                    failures.append((text, fileBookmark))
                else:
                    bookmarks.append(Bookmark(link, text))

            print(f"\tScraped %d bookmarks successfully, %d unsuccessfully." % (len(bookmarks), len(failures)))

            allBookmarks.extend(bookmarks)
            allFailures.extend(failures)

        else:
            print(f"\t...// TODO: Add support for %s bookmark files." % extension)

    # Display any errors encountered.
    for error, unparsed in allFailures:
        print(f"!!! Failed to parse bookmark text \"%s\": %s" % (unparsed, error))

if __name__ == "__main__":
    main()
