#!/usr/bin/python

#
# Quick tool to download VS Code Extention package offline,
#
# refer: https://code.visualstudio.com/docs/editor/extension-gallery?pub=HookyQR&ext=beautify#_common-questions
# usage: 
#        1. search the package from Market: https://marketplace.visualstudio.com/
#        2. Copy the 'url' from browser bar
#        3. run this command: python vsix_downloader.py -u <url>         
#
# Author: Rock Li(howardoer@gmail.com) 2017
#

import urllib, re, os, sys, getopt

def process_bar_helper(downloaded, chunk_size, full_size):
    process = 100.0*downloaded*chunk_size/full_size
    process = 100 if process > 100 else process
    sys.stdout.write("\r%.2f%%: [%-50s]" % (process, "*"*int(process/2)))

class VsixDownloader():
    VSIX_PATH_TEMPLATE = "http://${publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/${publisher}/extension/${extension name}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

    def __init__(self, url, outpath=None):
        self.org_url = url
        self.outpath = outpath if output else "./"

        self.publisher = ""
        self.extension_name = ""
        self.version = ""
    
    def get_version(self):
        print "get version..."

        version_pt = re.compile(r"\"version\":\"(?P<version>[.\w]*)\"")

        for line in urllib.urlopen(self.org_url).readlines():
            m = version_pt.search(line)
            if m:
                return m.groupdict()["version"]
        else:
            raise LookupError("No version found")
    
    def make_vsix_download_url(self):
        url_pt = re.compile(r"https://marketplace\.visualstudio\.com/items\?itemName=(?P<publisher>\S*)\.(?P<extension_name>\S*)")
        m = url_pt.search(self.org_url)
        if m:
            self.version = self.get_version()
            self.publisher = m.groupdict()['publisher']
            self.extension_name = m.groupdict()['extension_name']
            return self.VSIX_PATH_TEMPLATE.replace("${publisher}", self.publisher) \
                                          .replace("${extension name}", self.extension_name) \
                                          .replace("${version}", self.version)
        else:
            print "wrong input url of VS Extention package, please copy full address string from exploror"
            raise ValueError("Invalid url")

    def download(self):
        vsix_size = 0
        
        url = self.make_vsix_download_url()
        print "Exten package full url:"
        print url
        print "start to download..."
        
        vsix_name = "-".join([self.publisher, self.extension_name, self.version]) + ".vsix"
        download_path = os.path.join(self.outpath, vsix_name)
        
        urllib.urlretrieve(url, download_path, process_bar_helper)
        print "\nFile downloaded to %s" % os.path.abspath(download_path)

if __name__ == "__main__":
    help_string = "%s -u <VS Code Extention URL> [-o <output path>]" % sys.argv[0]
    url = None
    output = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:o:", ["help", "url=", "output="])
    except getopt.GetoptError:
        print help_string
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helpstring
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-o", "--output"):
            output = arg
        else:
            print "Invalid option"
            sys.exit()
    
    if url:
        vd = VsixDownloader(url, output)
        vd.download()
    else:
        print help_string