import glob
import os
import functions
import pymongo
from libraries import envparser, template
from wrappers import sqlite, mysql
from urlparse import urlparse

class processor:
    rds = None
    mysql = None
    mongo = None

    mapping = {
        'name': 'APP_DOMAIN',
        'api_secret': 'API_KEY',
        'domain': 'APP_DOMAIN',
        'url': 'APP_URL',
        'mysql_username': 'DB_USERNAME',
        'mysql_password': 'DB_PASSWORD',
        'mysql_database': 'DB_DATABASE',
        'mongodb_username': 'MONGODB_USERNAME',
        'mongodb_password': 'MONGODB_PASSWORD',
        'mongodb_database': 'MONGODB_DATABASE',
        'queue_name': 'APP_DOMAIN',
    }

    def __init__(self):
        env = functions.envs()
        self.rds = mysql(env['RDS_HOST'], env['RDS_USERNAME'], env['RDS_PASSWORD'], env['RDS_DATABASE'])
        self.mysql = mysql(env['MYSQL_HOST'], env['MYSQL_ROOT_USERNAME'], env['MYSQL_ROOT_PASSWORD'])

        mongo_connection_string = "mongodb://%s:27017/" % (env['MONGO_HOST'], )
        if env['MONGO_ROOT_PASSWORD'] is not '':
            mongo_connection_string = "mongodb://%s:%s@%s:27017/" % (
            urlparse(env['MONGO_ROOT_USERNAME']), urlparse(env['MONGO_ROOT_PASSWORD']), env['MONGO_HOST'])

        self.mongo = pymongo.MongoClient(mongo_connection_string)

    def create_table(self):
        # Create required table scheme
        schema_query = """CREATE TABLE IF NOT EXISTS customers (
                     id INTEGER PRIMARY KEY AUTO_INCREMENT,
                     name varchar(255) NOT NULL UNIQUE,
                     api_secret varchar(255) NOT NULL,
                     domain varchar(255) NOT NULL,
                     url varchar(255) NOT NULL,
                     mysql_username varchar(255) NOT NULL,
                     mysql_password varchar(255) NOT NULL,
                     mysql_database varchar(255) NOT NULL,
                     mongodb_username varchar(255) NOT NULL,
                     mongodb_password varchar(255) NOT NULL,
                     mongodb_database varchar(255) NOT NULL,
                     queue_name varchar(255) NOT NULL
                )"""

        self.rds.execute(schema_query)

        returned_tables = self.rds.fetch('SHOW TABLES LIKE "customers"')

        if len(returned_tables) is 0:
            raise Exception("Unable to create table, please validate permissions")

        return self

    def insert_into_sqlite (self, parameters):
        insert_query = """
        INSERT INTO customers (name, api_secret, domain, url, mysql_username, mysql_password, mysql_database, mongodb_username, mongodb_password, mongodb_database, queue_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.rds.execute(insert_query, parameters)

    def insert_into_customer_db(self, env, force_delete_from_db = False):
        if force_delete_from_db:
            self.rds.execute("delete from customers where name='%s'" % (env[self.mapping["name"]]))

        # Check if it already exists
        fetch_query = self.rds.fetch("select * from customers where name='%s'" % (str(env[self.mapping["name"]])))

        if len(fetch_query) is not 0:
            return

        parameters = (
            env[self.mapping["name"]],
            env[self.mapping["api_secret"]],
            env[self.mapping["domain"]],
            env[self.mapping["url"]],
            env[self.mapping["mysql_username"]],
            env[self.mapping["mysql_password"]],
            env[self.mapping["mysql_database"]],
            env[self.mapping["mongodb_username"]],
            env[self.mapping["mongodb_password"]],
            env[self.mapping["mongodb_database"]],
            env[self.mapping["queue_name"]],
        )

        self.insert_into_sqlite(parameters)

        del env

    def create_database_from_all_customers_envs(self, pattern):
        directories = glob.glob(pattern)

        for directory in directories:
            # Checking if .env exists
            src = '%s/.env' % (directory)
            if os.path.exists(src):
                env = envparser.parse_file(src)

                self.insert_into_customer_db(env)
            else:
                continue

        return self

    def setup_mysql(self, domain, app_url):
        self.create_table()

        # Check if it already exists
        fetch_query = self.rds.fetch("select id, mysql_password from customers where name='{0}'".format(domain))

        exists_in_rds = False
        if len(fetch_query) is not 0:
            print "User found in RDS:"
            mysql_password = fetch_query[0][1]

            exists_in_rds = True
        else:
            mysql_password = functions.random_string(16)

            parameters = (
                domain,
                '',
                domain,
                app_url,
                # Mysql Credentials
                domain,
                mysql_password,
                domain,
                # Mongo Credentials
                domain,
                mysql_password,
                domain,
                # Queue Name
                domain,
            )

            self.insert_into_sqlite(parameters)

        # All well, now create a database with this name
        self.mysql.execute("CREATE DATABASE IF NOT EXISTS %s" % (domain))

        # Checking if user exists
        existing_users = self.mysql.fetch("select * from user where user=\"%s\"" % (domain, ))

        if len(existing_users) is 0:
            # Create User
            self.mysql.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (domain, '%%', mysql_password))

        #self.mysql.execute("GRANT ALL PRIVILEGES ON %s . * TO '%s'@'%s'" % (domain, domain, functions.env('MYSQL_HOST')))

        self.mysql.execute("GRANT SELECT ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT INSERT ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT DELETE ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT CREATE ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT UPDATE ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT ALTER ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT DROP ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT INDEX ON %s.* TO %s@'%s'" % (domain, domain, '%%'))
        self.mysql.execute("GRANT PROCESS ON *.* TO %s@'%s'" % (domain, '%%'))
        self.mysql.execute("GRANT REFERENCES ON %s.* TO %s@'%s'" % (domain, domain, '%%'))

        self.mysql.execute("FLUSH PRIVILEGES")

        db = self.mongo[domain]
        db.add_user(domain, mysql_password, roles=[{"role": "readWrite", "db": domain}])

        return self

    def remove_mysql_setup(self, domain):
        # Revoke all privileges
        # self.mysql.execute("REVOKE ALL PRIVILEGES, GRANT OPTION FROM %s" % (domain))

        # Drop user
        try:
            self.mysql.execute("DROP USER '%s'@'%s'" % (domain, functions.env('MYSQL_HOST')))
            print 'User Dropped'
        except Exception, e:
            print e
            pass

        try:
            # Drop database
            self.mysql.execute("DROP DATABASE %s" % (domain))
            print 'Database Dropped'
        except Exception, e:
            print e
            pass

        try:
            # Flush privileges
            self.mysql.execute("FLUSH PRIVILEGES")
            print 'Privileges flushed'
        except:
            pass

        try:
            db = self.mongo[domain]
            db.remove_user(domain)

            print 'Mongo User Deleted'
        except Exception, e:
            print "Deletion of Mongo user failed due to the reason %s" % e
            pass

        # Now delete from sqlite
        self.rds.execute("delete from customers where name='%s'" % (domain))
        print 'Removed from customers RDS'

        return self

    def setup_env(self, domain, path):
        # Check if customer with this domain exists in sqlite
        customer = self.rds.fetch("select name, mysql_username, mysql_password, url from customers where name='%s'" % (domain))

        if not os.path.exists(path):
            raise Exception("Unable to find env path %s" % (path))

        if len(customer) is 0:
            raise Exception("Unable to find domain in DB. Please create domain first")

        customer = customer[0]

        parameters = {
            'APP_DOMAIN': customer[1],
            'DB_USERNAME': customer[1],
            'DB_PASSWORD': customer[2],
            'DB_DATABASE': customer[0],
            'MONGODB_USERNAME': customer[1],
            'MONGODB_PASSWORD': customer[2],
            'MONGODB_DATABASE': customer[0],
            'APP_URL': customer[3]
        }

        envparser.update_parameters_in_file(path, parameters)

        # Sync with customers table  now

        env = envparser.parse_file(path)
        env['APP_DOMAIN'] = customer[0]

        self.insert_into_customer_db(env, True)

        return self
