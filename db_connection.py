import pyodbc
from config import SERVER, DATABASE

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Authentication=ActiveDirectoryInteractive;"
    )
    return conn