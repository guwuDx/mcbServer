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

def query_header_gen(shape, shapeInfo):
    sql_header = f"SELECT {shapeInfo[0]['colnames'][0]}.*, " \
                 f"{shapeInfo[shape.id]['colnames'][0]}.*, " \
                 f"{shapeInfo[shape.id]['colnames'][1]}.*\n"
    sql_header += f"FROM {shapeInfo[0]['colnames'][0]}\n"
    sql_header += f"JOIN {shapeInfo[shape.id]['colnames'][0]} " \
                  f"ON {shapeInfo[shape.id]['colnames'][0]}.gup_id = {shapeInfo[0]['colnames'][0]}.id\n"

    return sql_header

def query_freq_gen(freq):
    sql_pt_freq = ""
    return sql_pt_freq