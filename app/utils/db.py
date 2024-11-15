import mysql.connector
from app.utils.general import get_cnf


def get_db_connection(database: str):
    db_config = get_cnf("conf/server.cnf", database)

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
            sql_pt_generic += f"cellMaterial_id = {generic.selectedMaterial}\n    "
        elif generic.parameter == 2:
            sql_pt_generic += f"baseMaterial_id = {generic.selectedMaterial}\n    "
        elif 3 <= generic.parameter <= 5:
            if generic.parameter == 3:
                sql_pt_generic += "period "
            elif generic.parameter == 4:
                sql_pt_generic += "height "
            elif generic.parameter == 5:
                sql_pt_generic += "thickness "

            if generic.rangeMode == 1:
                sql_pt_generic += f"= {generic.value}\n    "
            elif generic.rangeMode == 2:
                sql_pt_generic += f">= {generic.value}\n    "
            elif generic.rangeMode == 3:
                sql_pt_generic += f"<= {generic.value}\n    "
            elif generic.rangeMode == 4:
                if generic.rangeStart == generic.rangeEnd:
                    sql_pt_generic += f"= {generic.rangeStart}\n    "
                elif generic.rangeStart > generic.rangeEnd:
                    sql_pt_generic += f"BETWEEN {generic.rangeEnd} AND {generic.rangeStart}\n    "
                else:
                    sql_pt_generic += f"BETWEEN {generic.rangeStart} AND {generic.rangeEnd}\n    "
            else:
                raise Exception("Unknown range mode")
        else:
            raise Exception("Unknown parameter")

    return sql_pt_generic


def query_freq_gen(freqSet, freq_table):
    freq_table
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
            sql_pt_freq += f"g.S_Param_id = {freq.selectedSparam}\n  "
        elif 2 <= freq.parameter <= 6:
            if freq.parameter == 2:
                sql_pt_freq += f"g.E_theta "
            elif freq.parameter == 3:
                sql_pt_freq += f"f.Frequency "
            elif freq.parameter == 4:
                sql_pt_freq += f"f.Magnitude "
            elif freq.parameter == 5:
                sql_pt_freq += f"f.Phase_in_degree "
            elif freq.parameter == 6:
                sql_pt_freq += f"f.Dispersion "
            else:
                raise Exception("Unknown parameter")

            if freq.rangeMode == 1:
                sql_pt_freq += f"= {freq.value}\n  "
            elif freq.rangeMode == 2:
                sql_pt_freq += f">= {freq.value}\n  "
            elif freq.rangeMode == 3:
                sql_pt_freq += f"<= {freq.value}\n  "
            elif freq.rangeMode == 4:
                if freq.rangeStart == freq.rangeEnd:
                    sql_pt_freq += f"= {freq.rangeStart}\n  "
                elif freq.rangeStart > freq.rangeEnd:
                    sql_pt_freq += f"BETWEEN {freq.rangeEnd} AND {freq.rangeStart}\n  "
                else:
                    sql_pt_freq += f"BETWEEN {freq.rangeStart} AND {freq.rangeEnd}\n  "
            else:
                raise Exception("Unknown range mode")
        else:
            raise Exception("Unknown parameter")

    return sql_pt_freq


def query_cat(sql_pt_generic, sql_pt_freq, gen_table, shape_param_table, freq_table):
    sql_expr = "SELECT g.*, s.*, f.*\nFROM "
    if sql_pt_generic:
        sql_expr += f"(\n"
        sql_expr += f"  SELECT * \n"
        sql_expr += f"  FROM {gen_table}\n"
        sql_expr += f"  WHERE {sql_pt_generic}) g\n"
    else: # No generic filter
        sql_expr += f"{gen_table} g\n"

    sql_expr += f"JOIN {shape_param_table} s ON s.gup_id = g.id\n"
    sql_expr += f"JOIN {freq_table} f ON f.up_id = s.id\n"

    if sql_pt_freq:
        sql_expr += f"WHERE {sql_pt_freq};\n"
    else: # No frequency filter
        sql_expr += f";\n"

    return sql_expr


def query_exec(conn, sql):
    """
    Execute the query

    :param conn: the database connection
    :param sql: the query
    :return: the result of the query
    """

    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    return rows