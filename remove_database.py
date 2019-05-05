import sys
from processor import processor

# Checks and creates required tables
processor = processor()

if len(sys.argv) < 2:
    raise Exception("Please provide domain name. ex: setup_mysql.py domainname")

processor.remove_mysql_setup(sys.argv[1])

print "Done!"