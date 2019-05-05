import sys
from processor import processor

# Checks and creates required tables
processor = processor()

if len(sys.argv) < 3:
    raise Exception("Please provide domain name and .env path. ex: setup_env.py domainname /var/www/html/domain/.env")

processor.setup_env(sys.argv[1], sys.argv[2])

print "Done!"
