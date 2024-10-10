import configparser
import os
import ast

def get_cnf(filename, section):
    """
    Read the configuration file and return a dictionary object

    :param filename: name of the configuration file
    :param section: section of the configuration
    :return: a dictionary of the configuration
    """

    parser = configparser.ConfigParser()

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file '{filename}' not found")
    
    parser.read(filename)

    config = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f"Section '{section}' not found in the {filename} file")

    return config


def get_shapeInfo(conn):
    """
    Get the shape information from the database

    :param conn: the database connection
    :return: a Object containing the shape information
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ShapeDef")
    rows = cursor.fetchall()

    shapeInfo = []
    for row in rows:
        shapeInfo.append({
            "id": row[0],
            "name": row[1],
            "colnames": ast.literal_eval(row[5])
        })

    return shapeInfo