import MySQLdb
import sqlite3

class sqlite:
    db_name = 'sqlite.db'
    connection = None

    def __init__(self, db_name_updated):
        self.db_name = db_name_updated

        self.__get_connection()

    def __get_db_name(self):
        return self.db_name;

    def __get_connection(self):
        if self.connection:
            return self.connection;

        self.connection = sqlite3.connect(self.__get_db_name())

        return self.connection

    def fetch(self, query, parameters=()):
        cursor = self.__get_connection().cursor()

        cursor.execute(query, parameters)

        return cursor.fetchall()

    def execute(self, query, parameters=(), commit=True):
        connection = self.__get_connection()
        cursor = connection.cursor()
        cursor.execute(query, parameters)

        if commit:
            connection.commit()

    def disconnect(self):
        self.__get_connection().close()

    def __del__(self):
        self.disconnect();


class mysql:
    host = ''
    username = ''
    password = ''
    database = ''

    connection = None

    def __init__(self, host, username, password, database='mysql'):
        self.host = host
        self.username = username
        self.password = password
        self.database = database

        self.__get_connection()

    def __get_connection(self):
        if self.connection:
            return self.connection;

        self.connection = MySQLdb.connect(self.host, self.username, self.password, self.database)

        return self.connection

    def fetch(self, query, parameters=()):
        cursor = self.__get_connection().cursor()

        cursor.execute(query, parameters)

        return cursor.fetchall()

    def execute(self, query, parameters=(), commit=True):
        connection = self.__get_connection()
        cursor = connection.cursor()
        cursor.execute(query, parameters)

        if commit:
            connection.commit()

    def disconnect(self):
        self.__get_connection().close()

    def __del__(self):
        self.disconnect();