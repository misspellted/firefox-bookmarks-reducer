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

class HtmlBookmarkFile(object):
    def __init__(self):
        self.lines = list()
        self.bookmarks = list()

    def asXml(self):
        return None if len(self.lines) == 0 else ET.fromstring("\n".join(self.lines))

    @staticmethod
    def toBookmark(htmlBookmark):
        bookmark = None

        try:
            element = ET.fromstring(htmlBookmark)
            if "HREF" in element.attrib:
                bookmark = Bookmark(element.attrib["HREF"], element.text)
        except ET.ParseError as pe:
            # Attempt a manual string extraction.
            link = None
            text = None
            hrefMatch = re.search(r"HREF=\".*?\"", htmlBookmark)
            if not hrefMatch is None:
                link = hrefMatch.group()[6:-1]
            tagMatch = re.search(r">.*?</A>", htmlBookmark)
            if not tagMatch is None:
                text = tagMatch.group()[1:-4]

            if not link is None and not text is None:
                bookmark = Bookmark(link, text)
            else:
                # Fallback to reporting the error message.
                bookmark = pe.message if hasattr(pe, "message") else str(pe)

        return bookmark

    @staticmethod
    def fromFile(filePath):
        hbf = HtmlBookmarkFile()

        with open(filePath, "r") as bookmarks:
            for line in bookmarks:
                stripped = line.strip()

                if stripped.startswith("<DT>"):
                    stripped = stripped[4:]

                    if stripped.startswith("<A "):
                        bookmark = HtmlBookmarkFile.toBookmark(stripped)

                        if isinstance(bookmark, Bookmark):
                            hbf.bookmarks.append(bookmark)
                        else:
                            hbf.lines.append((stripped, bookmark))

        return hbf

def filePaths():
    filePaths = list()

    for (directory, subdirectories, files) in os.walk("."):
        for file in files:
            filePaths.append(os.path.sep.join([directory, file]))

    return filePaths

def main():
    bookmarks = list()

    for filePath in filePaths():
        print(filePath)
        if filePath.endswith("html"):
            hbf = HtmlBookmarkFile.fromFile(filePath)
            failures = hbf.lines
            print(f"\tScraped %d bookmarks successfully, %d unsuccessfully." % (len(hbf.bookmarks), len(failures)))
            bookmarks.extend(hbf.bookmarks)
            bookmarks.sort()
            if 0 < len(failures):
                for line, error in failures:
                    print(f"\t\t%s\n\t\t\t%s" % (line, error))
        elif filePath.endswith("json"):
            print("\t...// TODO: Import JSON bookmark files...")

    for bookmark in bookmarks:
        print(bookmark)

if __name__ == "__main__":
    main()
