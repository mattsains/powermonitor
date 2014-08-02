"""
DBConnect: connect to database and perform queries

Requires: pymysql (https://github.com/PyMySQL/PyMySQL)
"""
import pymysql
import base64
import logging
from Decorators import Singleton


class DbConnection:
    """Class to connect to the database and execute queries"""
    def __init__(self, auto_commit=1):
        self.__conn = None
        self.connect(auto_commit)

    def connect(self, auto_commit=1):
        """Open the connection to the database"""
        """Connects to a mysql database called powermonitor with username 'powermonitor'"""
        try:
            self.__conn = pymysql.connect(host='192.168.1.5', port=3306, user='powermonitor',
                                          passwd=str(base64.b64decode(bytes('cDB3M3JtMG4xdDBy'))),
                                          db='powermonitor')
            self.__conn.autocommit(auto_commit)   # Automatically commit queries
        except (pymysql.DatabaseError, pymysql.MySQLError) as e:
            logging.warning('Cannot connect to database. Please check connection.')
            #logging.warning('PyMSQL Message: #%d - %s' % e)

    def disconnect(self):
        """Disconnect from the database"""
        try:
            self.__conn.close()
        except (pymysql.DatabaseError, pymysql.MySQLError) as e:
            logging.warning('There was a problem disconnecting from the database.')
            #logging.warning('PyMSQL Message: #%d - %s' % e)

    def execute_query(self, statement, data=None):
        """Execute a query that returns a result
        Usage: execute_query('SELECT * FROM TEST WHERE ID=%s AND NAME=%S', (124213, 'Text'))"""
        """Prevention of SQL injection should be done before passing the statement"""
        if self.__conn is None:
            self.connect()
        try:
            query = self.__conn.cursor()
            if data is None:
                query.execute(statement)    # For internal queries, where injection doesn't need to be handled
            else:
                query.execute(statement, data)
            query.close()
            return query
        except (pymysql.DatabaseError, pymysql.MySQLError) as e:
            logging.warning('There was a problem with the SQL query. Check your syntax\n'
                            'Your query: %s' % statement)
            #logging.warning('PyMSQL Message: #%d - %s' % e)
            return None

    def execute_non_query(self, statement, data=None):
        """Execute a SQL statement that does not return a result
        Usage: execute_non_query('INSERT INTO TEST VALUES(%s, %s)', (12345, 'Text'))"""
        """Prevention of SQL injection should be done before passing the statement"""
        if self.__conn is None:
            self.connect()
        try:
            query = self.__conn.cursor()
            if data is None:
                query.execute(statement)    # For internal queries, where injection doesn't need to be handled
            else:
                query.execute(statement, data)
            query.close()
        except (pymysql.DatabaseError, pymysql.MySQLError) as e:
            logging.warning('There was a problem with the SQL query. Check your syntax: %s' % statement)
            #logging.warning('PyMSQL Message: #%d - %s' % e)

    def commit_query(self):
        """Commit all SQL statements.
        If auto_commit in the connect method was set to 0, this method must be called to ensure that all statements
        are executed."""
        try:
            self.__conn.commit()
        except pymysql.MySQLError as e:
            logging.warning('There was a problem committing all SQL statements.')
            #logging.warning('PyMSQL Message: #%d - %s' % e)