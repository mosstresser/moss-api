# api/index.py
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moss_core import create_account

app = FastAPI(title="Moss API")
executor = ThreadPoolExecutor(max_workers=5)

@app.get("/")
async def root():
    return {"message": "Moss API running"}

@app.get("/generate")
async def generate(
    region: str = Query(..., description="ME, IND, ID, VN, TH, BD, PK, TW, CIS, SAC"),
    name_prefix: str = Query("moss"),
    pass_prefix: str = Query("moss"),
    target: int = Query(1, ge=1, le=5),
    ghost: bool = Query(False),
):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, create_account, region, name_prefix, pass_prefix, ghost) for _ in range(target)]
    results = await asyncio.gather(*tasks)
    
    success = []
    errors = []
    for acc in results:
        if isinstance(acc, dict) and "error" in acc:
            errors.append(acc["error"])
        else:
            success.append(acc)
    
    return {
        "status": "success" if success else "failed",
        "total_requested": target,
        "total_success": len(success),
        "accounts": success,
        "errors": errors if errors else None
    }