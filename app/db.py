import mysql.connector
from app.units import get_cnf


def get_db_connection():
    db_config = get_cnf("conf/server.cnf", "database")

    if db_config["base"] == "mysql":
        pass
    else:
        raise Exception("Unsupported database type")
    
    if not db_config.get("user"):
        raise Exception("Database user not specified")
    if not db_config.get("password"):
        raise Exception("Database password not specified")
    if not db_config.get("database"):
        raise Exception("Database name not specified")

    return mysql.connector.connect(
        host=db_config.get("host", "localhost"),
        port=db_config.get("port", 3306),
        charset=db_config.get("charset", "utf8mb4"),
        collation=db_config.get("collation", "utf8_general_ci"),
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
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

    for generic in genericSet:
        if sql_pt_generic:
            if generic['logic'] == 1:
                sql_pt_generic += "AND "
            elif generic['logic'] == 2:
                sql_pt_generic += "OR "

        sql_pt_generic

    return sql_pt_generic


def query_freq_gen(freqSet, target_table):
    sql_pt_freq = ""
    return sql_pt_freq