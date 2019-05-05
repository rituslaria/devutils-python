# Devutils Python
Very useful in automation where we need to create mysql database with same name as user and assign him a random password. Specially in SAAS based products where instances are created for different users.

## Module Dependencies
- Python 2.7.x
- Python pip (latest)
- mysqlclient (Install using pip)
- pymongo (Install using pip)

## How to setup
First of all you need to add mysql and sql file credentials in .env file

```
SQLITE_FILE_NAME=sqlite.db

MYSQL_HOST=localhost
MYSQL_ROOT_USERNAME=root
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=mysql
```

## What are the scripts available
 - create_database_from_all_customers_envs.py
 - setup_mysql.py {domain} {app_url}
 - remove_mysql.py {domain}
 - setup_env.py {domain} {path_to_env}

## create\_database\_from_all\_customers\_envs.py
This command is used to create sqlite db for all customers. We create a table called `customers` in sqlite. Below query runs to create sqlite table.

```
CREATE TABLE IF NOT EXISTS customers (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL UNIQUE,
                     api_secret TEXT NOT NULL,
                     domain TEXT NOT NULL,
                     url TEXT NOT NULL,
                     mysql_username TEXT NOT NULL,
                     mysql_password TEXT NOT NULL,
                     mysql_database TEXT NOT NULL,
                     mongodb_username TEXT NOT NULL,
                     mongodb_password TEXT NOT NULL,
                     mongodb_database TEXT NOT NULL,
                     queue_name TEXT NOT NULL
```

So, below information is stored in this table

```
 - Name
 - API Secret
 - Domain
 - URL
 - Mysql Username
 - Mysql Password
 - Mysql Database
 - MongoDB Username
 - MongoDB Password
 - MongoDB Database
 - Queue Name
```

Example

```
$> python create_database_from_all_customers_envs.py
$> Done!
```


## setup_database.py
 
This command is used to setup Mysql Database and user for an instance. Here is the list of tasks done by this command

```
 - Create Mysql User
 - Create Mysql Database with same name as User
 - Generate Random Mysql Password
 - Grant Access to the created user to the database we just created
 - Create Mongo User
 - Create Mongo Database with same name as User
 - Sets same password which is iset for Mysql
 - Grant Access to the created user to the database we just created
 - Writes database, mongo details along with password and domain details in sqlite database customers table
```

Example

```
$> python setup_mysql.py mydomain
$> Done!
```

Above command will create a mysql user and database named `mydomain` and will give access to `mydomain` for `mydomain` database.

### remove_database.py
This command is used to remove Mysql Setup for an instance. Use this very carefully
```
 - Removes Mysql User
 - Removes Mysql Database with same name as User
 - Revokes Accesses
 - Removes details from SQLite
```

Example

```
$> python remove_mysql.py mydomain
$> Done!
```

## setup_env.py
This command is used to write database detils to env file provided in argument

```
 - Checks if domain exists in sqlite db 
 - Checks if .env file exists where to write data
 - Fetches data from sqlite
 - Writes data to .env file and overrides that
 
```

Example

```
$> python setup_env.py mydomain /var/www/mydomain/.env
$> Done!
```

## What are the areas of exception
 - When System is unable to locate `.env` file.
 - When system is unable to connect to sqlite db
 - When system is unable to connect to mysql db
 - When system is unable to store sqlite file on disk
 - When system is unable to read sqlite file
 - When system is unable to create mysql user
 - When system is unable to create mysql DB
 - When system is unable to grant required preivileges (If logged in user has no permissions)