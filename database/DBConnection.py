import psycopg2

class DBConnection:

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def connect(self):
        conn = psycopg2.connect(user = self.user,
                                password = self.password,
                                host = self.host,
                                port = self.port,
                                database = self.database)

        return conn

    def disconnect(self, conn):
        conn.close()