import sys
from processor import processor

# Checks and creates required tables
processor = processor()

if len(sys.argv) < 3:
    raise Exception("Please provide domain name as well as app_url. ex: setup_database.py domainname https://subdomain.domain.com")

processor.setup_mysql(sys.argv[1], sys.argv[2])

print "Done!"