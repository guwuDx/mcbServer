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
            if generic.logic == 1:
                sql_pt_generic += "AND "
            elif generic.logic == 2:
                sql_pt_generic += "OR "

        if generic.isInvert:
            sql_pt_generic += "NOT "

        if generic.parameter == 1:
            sql_pt_generic += f"cellMaterial_id = {generic.selectedMaterial}\n"
        elif generic.parameter == 2:
            sql_pt_generic += f"baseMaterial_id = {generic.selectedMaterial}\n"
        elif 3 <= generic.parameter <= 5:
            if generic.parameter == 3:
                sql_pt_generic += "period "
            elif generic.parameter == 4:
                sql_pt_generic += "height "
            elif generic.parameter == 5:
                sql_pt_generic += "thickness "

            if generic.rangeMode == 1:
                sql_pt_generic += f"= {generic.value}\n"
            elif generic.rangeMode == 2:
                sql_pt_generic += f">= {generic.value}\n"
            elif generic.rangeMode == 3:
                sql_pt_generic += f"<= {generic.value}\n"
            elif generic.rangeMode == 4:
                if generic.rangeStart == generic.rangeEnd:
                    sql_pt_generic += f"= {generic.rangeStart}\n"
                elif generic.rangeStart > generic.rangeEnd:
                    sql_pt_generic += f"BETWEEN {generic.rangeEnd} AND {generic.rangeStart}\n"
                else:
                    sql_pt_generic += f"BETWEEN {generic.rangeStart} AND {generic.rangeEnd}\n"

    return sql_pt_generic


def query_freq_gen(freqSet, target_table):
    sql_pt_freq = ""

    for freq in freqSet:
        if sql_pt_freq:
            if freq.logic == 1:
                sql_pt_freq += "AND "
            elif freq.logic == 2:
                sql_pt_freq += "OR "

        if freq.isInvert:
            sql_pt_freq += "NOT "

        if freq.parameter == 1:
            sql_pt_freq += f""

    return sql_pt_freq