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

    gen_table = shapeInfo[0]['colnames'][0]
    target_shape = shapeInfo[shape.id]['colnames']

    sql_header = f"SELECT {gen_table}.*, " \
                 f"{target_shape[0]}.*, " \
                 f"{target_shape[1]}.*\n"
    sql_header += f"FROM {gen_table}\n"
    sql_header += f"JOIN {target_shape[0]} " \
                  f"ON {target_shape[0]}.gup_id = {gen_table}.id\n"

    return sql_header


def query_generic_gen(genericSet):
    sql_pt_generic = ""
    return sql_pt_generic


def query_freq_gen(freqSet, target_table):
    sql_pt_freq = ""
    return sql_pt_freq