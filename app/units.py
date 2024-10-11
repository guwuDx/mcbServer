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


def freq_pattern_parse(freqSet):
    """
    Parse the frequency from the frequency setting logic 
    into the actual frequency range, 
    which will be represented as [NIR, MIR, FIR]
    """

    terms = []
    crr_term_intervals = []
    N_M_F = [0, 0, 0]   # 1: query 0: not query

    for item in freqSet:
        if item['parameter'] == 3:
            logic       = item['logic']
            isInvert    = item['isInvert']
            rangeEnd    = item['rangeEnd']
            rangeMode   = item['rangeMode']
            rangeStart  = item['rangeStart']
            val         = item['value']

            interval = get_interval(rangeMode, val, isInvert, rangeStart, rangeEnd)

    return N_M_F


def get_interval(rangeMode, val, isInvert, rangeStart, rangeEnd):
    """
    """

    if isInvert:
        if rangeMode == 1: # x != val
            return [(0, val), (val, float('inf'))]
        elif rangeMode == 2: # x < val
            return [(0, val)]
        elif rangeMode == 3: # x > val
            return [(val, float('inf'))]
        elif rangeMode == 4: # x NOT BETWEEN rangeStart AND rangeEnd
            return [(0, rangeStart), (rangeEnd, float('inf'))]
    else:
        if rangeMode == 1: # x = val
            return [(val, val)]
        elif rangeMode == 2: # x >= val
            return [(val, float('inf'))]
        elif rangeMode == 3: # x <= val
            return [(0, val)]
        elif rangeMode == 4: # x BETWEEN rangeStart AND rangeEnd
            return [(rangeStart, rangeEnd)]