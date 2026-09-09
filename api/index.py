# api/index.py
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Tambahkan path ke parent agar bisa import moss_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moss_core import create_account

app = FastAPI(title="Moss API - Free Fire Account Generator")

executor = ThreadPoolExecutor(max_workers=5)

@app.get("/")
async def root():
    return {"message": "Moss API is running. Use /generate endpoint."}

@app.get("/generate")
async def generate(
    region: str = Query(..., description="Region: ME, IND, ID, VN, TH, BD, PK, TW, CIS, SAC"),
    name_prefix: str = Query("moss", description="Nama depan akun"),
    pass_prefix: str = Query("moss", description="Prefiks password"),
    target: int = Query(1, ge=1, le=5, description="Jumlah akun (max 5 karena timeout)"),
    ghost: bool = Query(False, description="Mode Ghost (akun tanpa region)"),
):
    """
    Generate akun Free Fire.
    """
    if target > 5:
        raise HTTPException(status_code=400, detail="Maksimal 5 akun per request (batas Vercel)")

    results = []
    errors = []

    def create_one():
        return create_account(region, name_prefix, pass_prefix, ghost)

    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, create_one) for _ in range(target)]
    done = await asyncio.gather(*tasks)

    for acc in done:
        if acc:
            results.append(acc)
        else:
            errors.append("Gagal membuat akun")

    return {
        "status": "success" if results else "failed",
        "total_requested": target,
        "total_success": len(results),
        "accounts": results,
        "errors": errors if errors else None
    }