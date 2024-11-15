import numpy as np
import hashlib
import glob
import os

from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.utils.db import get_db_connection
from app.utils.db import query_generic_gen
from app.utils.db import query_freq_gen
from app.utils.db import query_cat
from app.utils.db import query_exec
from app.utils.queries import get_shapeInfo
from app.utils.queries import freq_range_parse
from app.utils.queries import result_text_gen
from app.utils.queries import get_cnf

from app.schemas import queryRequest

query_router = APIRouter(prefix="/query")

@query_router.post("/api/")
def query_api(request: queryRequest):
    now = datetime.now()
    fid = (hashlib.sha256(request.model_dump_json().encode('utf-8')))
    fid = fid.hexdigest()
    fileName = f"{fid}{now.strftime('%Y%m%d%H%M%S')}.txt"

    N_M_F = freq_range_parse(request.freqSet)
    if N_M_F == [False, False, False]:
        N_M_F = [True, True, True]
    freqRange = ["_nir", "_mir", "_fir"]
    conn = get_db_connection("db_official")
    shapeInfo = get_shapeInfo(conn)
    sql = [["" for _ in range(3)] for _ in range(shapeInfo.__len__())]
    query_result = [[] for _ in range(shapeInfo.__len__())]

    for shape in request.shapeSet:
        sql_pt_generic = query_generic_gen(request.genericSet)
        generic_table = shapeInfo[0]['tables'][0]
        shape_tables = shapeInfo[shape.id]['tables']
        paramNum = shapeInfo[shape.id]['paramNum']

        for j in range(3):
            if N_M_F[j]:
                sql_pt_freq = query_freq_gen(request.freqSet, shape_tables[1]+freqRange[j])
                sql[shape.id][j] = query_cat(sql_pt_generic, sql_pt_freq, generic_table, shape_tables[0], shape_tables[1]+freqRange[j])
                query_result_tmp = query_exec(conn, sql[shape.id][j])

                if query_result_tmp: # Remove the id, foreign key, hash columns
                    query_result_tmp = np.delete(query_result_tmp, [0, 8, 9, 6+paramNum, 7+paramNum, 12+paramNum], axis=1)
                else:
                    print(f"[WARN][mcbq] No data was found in {shape.name} about the range of {freqRange[j]}")

                # stack the query results for each shape
                if not query_result[shape.id]:
                    query_result[shape.id] = query_result_tmp
                else:
                    query_result[shape.id] = np.vstack((query_result[shape.id], query_result_tmp))
            else:
                print(f"[INFO][mcbq] No data was requested for {shape.name} about {freqRange[j]}")
    conn.close()

    # check if the query result is empty at all
    for i, arr in enumerate(query_result):
        if len(arr) != 0:
            break
        else:
            i = shapeInfo.__len__() - 1
    if i == shapeInfo.__len__() - 1 and len(arr) == 0:
        return {"status":4, "message": "[WARN][mcbq] No data was found in the database"}

    delivered_file = result_text_gen(query_result, shapeInfo, sql, fileName)

    # block the download if the file larger than 1GB
    if os.path.getsize(delivered_file) > 1024*1024*1024:
        return {"status":3, "message": "[WARN][mcbq] The file is too large to download"}

    return {"status":0, "message": "[OK][mcbq] Query was successful", "file": fileName[:64]}



@query_router.get("/download/")
async def download_file(file: str):
    now = datetime.now()
    time = now.strftime('%Y%m%d%H%M%S')
    if not len(file) == 64:
        return {"status":2, "message": "[ERROR][mcbq] illegal file name"}

    result_dir = get_cnf("conf/server.cnf", "server")["result_path"]
    if result_dir[-1] != '/' or result_dir[-1] != '\\':
        result_dir += '/'
    if not os.path.exists(result_dir):
        return {"status":1, "message": "[ERROR][mcbq] Server Internal Error"}

    pattern = os.path.join(result_dir, file + '*')
    matching_files = glob.glob(pattern)
    filtered_files = [f for f in matching_files if os.path.basename(f)[:64] == file]

    # return the latest file, file name is time
    if filtered_files:
        return FileResponse(filtered_files[-1], 
                            media_type='text/plain', 
                            filename=f"mcbq_{time}.txt",
                            headers={"Content-Disposition": f"attachment; filename={time}.txt"})
    else:
        return {"status":1, "message": "[ERROR][mcbq] Server Internal Error"}