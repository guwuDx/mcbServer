import numpy as np

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.db import get_db_connection
from app.db import query_generic_gen
from app.db import query_freq_gen
from app.db import query_cat
from app.db import query_exec
from app.units import get_shapeInfo
from app.units import freq_range_parse


app = FastAPI()

class Shape(BaseModel):
    id: int
    name: str

class Generic(BaseModel):
    logic: int
    parameter: int
    rangeMode: int
    showRange: bool
    rangeStart: Optional[float]
    rangeEnd: Optional[float]
    value: Optional[float]
    dispSwitch: int
    selectedMaterial: Optional[int]
    isInvert: bool

class Freq(BaseModel):
    logic: int
    parameter: int
    rangeMode: int
    showRange: bool
    rangeStart: Optional[float]
    rangeEnd: Optional[float]
    value: Optional[float]
    dispSwitch: int
    selectedSparam: Optional[int]
    isInvert: bool

class queryRequest(BaseModel):
    shapeSet: List[Shape]
    genericSet: List[Generic]
    freqSet: List[Freq]



@app.post("/query/api/")
def query_api(request: queryRequest):
    N_M_F = freq_range_parse(request.freqSet)
    freqRange = ["_fir", "_mir", "_nir"]
    conn = get_db_connection()
    shapeInfo = get_shapeInfo(conn)
    sql = [["" for _ in range(3)] for _ in range(shapeInfo.__len__())]
    query_result = [[[] for _ in range(3)] for _ in range(shapeInfo.__len__())]

    for shape in request.shapeSet:
        generic_table = shapeInfo[0]['colnames'][0]
        shape_tables = shapeInfo[shape.id]['colnames']
        sql_pt_generic = query_generic_gen(request.genericSet)

        for j in range(3):
            if N_M_F[j]:
                sql_pt_freq = query_freq_gen(request.freqSet, shape_tables[1]+freqRange[j])
                sql[shape.id][j] = query_cat(sql_pt_generic, sql_pt_freq, generic_table, shape_tables[0], shape_tables[1]+freqRange[j])
                query_result[shape.id][j] = query_exec(conn, sql[shape.id][j])

    return {"message": "OK"}

