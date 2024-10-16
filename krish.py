import pyodbc
from sqlalchemy import true,False_
"""connection_string = (
    'DRIVER=ODBC Driver 18 for SQL Server;'
    'SERVER=98.71.140.253,1434;'
    'DATABASE=master;'
    'UID=sa_admin;'
    'PWD=AzureAI@123;'
    'TrustServerCertificate=yes'
)"""
connection_string = (
    'DRIVER=ODBC Driver 18 for SQL Server;'
    'SERVER=98.71.140.253,1434;'
    'DATABASE=master;'
    'UID=sa_admin;'
    'PWD=AzureAI@123;'
    'TrustServerCertificate=yes'
)
connection = pyodbc.connect(connection_string)


sql_query = "select name, database_id from sys.databases"
connection.autocommit = true
cursor = connection.cursor()

cursor.execute(sql_query)
columns = [column[0] for column in cursor.description]
print(cursor.fetchall())
print(columns)

#print(cursor.messages)
#print(cursor.description)