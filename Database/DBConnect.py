"""DBConnect requires pymysql to be installed"""
import pymysql
import base64


class DbConnection():
    """Class to connect to the database and execute queries"""
    def __init__(self):
        self.__conn = None

    def connect(self):
        """Open the connection to the database"""
        try:
            self.__conn = pymysql.connect(host='localhost', port=3306, user='powermonitor',
                                          passwd=str(base64.b64decode(bytes('cDB3M3JtMG4xdDBy', 'utf-8')))[2:-1],
                                          db='powermonitor')
        except (pymysql.DatabaseError, pymysql.MySQLError):
            # TODO: Handle errors correctly
            print("Can't connect")
            pass

    def disconnect(self):
        """Disconnect from the database"""
        try:
            self.__conn.close()
        except (pymysql.DatabaseError, pymysql.MySQLError):
            # TODO: Handle errors correctly
            pass

    def execute_query(self, statement):
        """Execute a query that returns a result"""
        try:
            query = self.__conn.cursor()
            query.execute(statement)
            query.close()
            return query
        except (pymysql.DatabaseError, pymysql.MySQLError):
            # TODO: Handle errors correctly
            return None

    def execute_non_query(self, statement):
        """Execute a SQL statement that does not return a result"""
        try:
            query = self.__conn.cursor()
            query.execute(statement)
            query.close()
        except (pymysql.DatabaseError, pymysql.MySQLError):
            # TODO: Handle errors correctly
            pass