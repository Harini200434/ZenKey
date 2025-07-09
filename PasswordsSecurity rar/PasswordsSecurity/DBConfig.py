import mysql.connector

class DBConnection:
    @staticmethod
    def getConnection():
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="SH@34@v1p2j3s4h5",
            db='password_security'
        )
        return database

if __name__ == "__main__":
    print(DBConnection.getConnection())



