# Web-crawler

Web-crawler is a Python program that browses a vendor website, downloads
firmware files, and fetches their metadata.The program collects metadata for 
each firmware file and stored it in MongoDB. The tool can run multiple times
and check if the information on the website is changed and in that case,
update the new information in the database. Otherwise, the information in
the database will not be changed. By default, files are not downloaded. 
in case you wish to, you can do it easily (explained later).


## Prerequisites
Beautifulsoup
Requests
Pymonogo
Make sure that a MongoDB instance is running on the default host and port (in bash: 'sudo mongod') and that you have an internet connection.


## Usage
program input: 
1)website_url - to start crawling from.
2)options [d, downloand_folder]
d- for downloading all firmware files.
downloand_folder - directory where the files will be downloaded to.
if the argument is not set by the user , the value is the default download directory in Linux: $HOME/download

You should invoke this program from a Unix command line, like so:
python3 main.py [options] website_url

examples:
if you wish to Download  all firmware files, you should invoke the program like so: 
python3 main.py website_url d

in case you want different saving folder (for example: 'desktop/myfolder'), you should invoke the program like so: 
python3 main.py website_url d 'desktop/myfolder'

