# moss_core.py
import requests
import random
import string
from datetime import datetime

# Impor semua fungsi dari app.py
from app import (
    RoFl, lMaO, gG, nIcE, dUdE, 
    rEgIoNlAnG, yEet, sUs, bRuH,
    Noob, xPro, Pro, fInE, yAy, codecs
)

def generate_exponent():
    """Menghasilkan eksponen seperti di app.py (5 digit dengan superskrip)"""
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1, 99999)
    return ''.join(exp_digits[d] for d in f"{num:05d}")

def create_account(region, account_name, password_prefix, is_ghost=False):
    """
    Membuat satu akun Free Fire.
    Mengembalikan dict atau dict dengan key 'error' jika gagal.
    """
    session = requests.Session()  # session baru untuk setiap panggilan
    try:
        # 1. Generate password seperti di app.py
        r1 = yEet(6)
        r2 = yEet(6)
        password = f"{password_prefix.upper()}_{r1}-VAIBHAV{r2}"
        
        # 2. Register guest → dapat uid
        uid = RoFl(session, password)
        
        # 3. Dapatkan access_token dan open_id
        access_token, open_id = lMaO(session, uid, password)
        
        # 4. Siapkan nama (prefix saja, nanti di gG ditambah exponent)
        name_prefix = account_name[:7]
        
        # 5. MajorRegister → dapat account_id (field 3)
        reg_resp = gG(session, name_prefix, access_token, open_id, region, is_ghost)
        account_id = reg_resp.get(3)
        if not account_id:
            raise Exception("No account_id")
        account_id = str(account_id)
        
        # 6. MajorLogin → dapat JWT
        lang_code = "pt" if is_ghost else rEgIoNlAnG.get(region.upper(), "en")
        login_resp, jwt_token = nIcE(session, access_token, open_id, region, lang_code)
        if not jwt_token:
            raise Exception("No JWT")
        
        # 7. Force region bind (jika bukan ghost dan bukan BR)
        if not is_ghost and jwt_token and region.upper() != "BR":
            try:
                dUdE(session, region, jwt_token)
            except Exception:
                pass  # gagal bind tidak masalah
        
        # 8. Buat nama final (sama seperti yang dihasilkan gG)
        final_name = name_prefix + generate_exponent()
        
        return {
            "uid": uid,
            "password": password,
            "name": final_name,
            "region": "GHOST" if is_ghost else region.upper(),
            "account_id": account_id,
            "jwt_token": jwt_token
        }
        
    except Exception as e:
        return {"error": str(e)}