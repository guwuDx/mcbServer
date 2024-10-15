import numpy as np

import configparser
import re
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
            "paramNum": row[3],
            "columns": ast.literal_eval(row[4]),
            "tables": ast.literal_eval(row[5])
        })

    cursor.close()
    return shapeInfo


def freq_expression_parse(freqSet):
    """
    Parse the frequency from the frequency setting logic 
    into the actual frequency range, 
    which will be represented as [NIR, MIR, FIR]

    :param freqSet: the frequency setting logic
    :return: the frequency range
    """

    terms = []
    crr_term_intervals = []

    for item in freqSet:
        if item.parameter == 3:
            logic       = item.logic
            isInvert    = item.isInvert
            rangeEnd    = item.rangeEnd
            rangeMode   = item.rangeMode
            rangeStart  = item.rangeStart
            val         = item.value

            interval = get_interval(rangeMode, val, isInvert, rangeStart, rangeEnd)

            if logic == 1: # AND
                if not crr_term_intervals:
                    crr_term_intervals = interval
                else:
                    crr_term_intervals = intersect_intervals(crr_term_intervals, interval)
            elif logic == 2: # OR
                if crr_term_intervals:
                    terms.append(crr_term_intervals)
                crr_term_intervals = interval

    if crr_term_intervals:
        terms.append(crr_term_intervals)

    # Union all terms
    result_intervals = []
    for term in terms:
        result_intervals = union_intervals(result_intervals, term)

    return result_intervals


def get_interval(rangeMode, val, isInvert, rangeStart, rangeEnd):
    """
    Get the interval of the frequency range

    :param rangeMode: the mode of the range
    :param val: the value of the range (only for mode 1, 2, 3)
    :param isInvert: whether the range is inverted
    :param rangeStart: the start of the range (only for mode 4)
    :param rangeEnd: the end of the range (only for mode 4)
    :return: the interval of the range
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


def intersect_intervals(interval1, interval2):
    """
    Intersect two intervals

    :param interval1: the first interval
    :param interval2: the second interval
    :return: the intersected interval
    """

    result = []
    for start1, end1 in interval1:
        for start2, end2 in interval2:
            start = max(start1, start2)
            end = min(end1, end2)
            if start < end:
                result.append((start, end))
            elif start == end: 
                # If intervals are singal points
                if start == start1 == end1 == start2 == end2:
                    result.append((start, end))
    return result


def union_intervals(interval1, interval2):
    """
    Union two intervals

    :param interval1: the first interval
    :param interval2: the second interval
    :return: the unioned interval
    """

    intervals = interval1 + interval2
    intervals.sort()
    merged = []
    for interval in intervals:
        if not merged: # First interval
            merged.append(interval)
        else:
            prev_start, prev_end = merged[-1]
            curr_start, curr_end = interval
            if prev_end >= curr_start: # Merge overlapping intervals
                merged[-1] = (prev_start, max(prev_end, curr_end))
            else:
                merged.append(interval)
    return merged


def N_M_F_judge(result_intervals):
    """
    Judge the frequency range is NIR, MIR or FIR

    :param result_intervals: the frequency range
    :return: the type of the frequency range
    """

    constants = get_cnf("conf/server.cnf", "constants")
    N_MIR = constants.get("N_MIR", 119.9170)
    M_FIR = constants.get("M_FIR", 59.9585)
    N_M_F = [0, 0, 0]

    for start, end in result_intervals:
        if start < M_FIR: # Overlapping with NIR: [0, M_FIR]
            N_M_F[2] = 1
        if start < N_MIR < end: # Overlapping with MIR: [N_MIR, M_FIR]
            N_M_F[1] = 1
        if end > N_MIR: # Overlapping with FIR: [N_MIR, inf)
            N_M_F[0] = 1
    return N_M_F


def freq_range_parse(freqSet):
    """
    Parse the frequency from the frequency setting logic
    into the actual frequency range

    :param freqSet: the frequency setting logic
    :return: the frequency range
    """

    return N_M_F_judge(freq_expression_parse(freqSet))


def result_text_gen(query_result, shapeInfo, sql, fileName):
    """
    Generate the result text from the query result

    :param query_result: the query result
    :param shapeInfo: the shape information
    :param sql: the SQL query array
    :param fileName: the name of the result file
    """

    # check the sql witch is not empty
    break_flag = False
    for i in range(shapeInfo.__len__()):
        for j in range(3):
            if sql[i][j]:
                raw_sql = sql[i][j]
                text_head = []
                for line in raw_sql.strip().split('\n'):
                    line = line.lstrip()
                    if line.startswith(('AND', 'OR', 'WHERE')):
                        line = re.sub(r'(?<= )[a-z]*\.', '', line, count=1).replace('WHERE', '')
                        text_head.append(line)

                text_head = '# ' + '    '.join(text_head)

                print(text_head)
                break_flag = True
                break
        if break_flag:
            break

    result_path = get_cnf("conf/server.cnf", "server")["result_path"] + fileName
    with open(result_path, "a") as f:
        pass