import sys
from processor import processor


# Checks and creates required tables
processor = processor()

if len(sys.argv) < 2:
    raise Exception("Please provide domain name. ex: setup_mysql.py domainname")

# sys.argv[1] example: /var/www/*.domain.com
processor.create_table().create_database_from_all_customers_envs(sys.argv[1])

print "Done!"