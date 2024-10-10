import mysql.connector
from app.units import get_cnf

def get_db_connection():
    db_config = get_cnf("conf/server.cnf", "database")

    if db_config["base"] == "mysql":
        pass
    else:
        raise Exception("Unsupported database type")

    return mysql.connector.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset=db_config["charset"],
        collation=db_config["collation"]
    )