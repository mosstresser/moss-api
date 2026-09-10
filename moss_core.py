# moss_core.py - FINAL dengan dual signature dan hardcode password
import json, time, random, string, hashlib, base64, codecs, hmac
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import urllib3
urllib3.disable_warnings()

# ================== KONSTANTA ==================
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th",
    "BD": "bn", "PK": "ur", "TW": "zh", "CIS": "ru", "SAC": "es", "BR": "pt"
}
INDIAN_CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
INDIAN_CARRIERS = ["Jio", "Airtel", "Vodafone Idea", "BSNL", "MTNL"]
INDIAN_DEVICES = ["Asus ASUS_AI2401_A", "Samsung SM-G998B", "OnePlus 9 Pro", "Xiaomi Mi 11", "Google Pixel 6"]

def sUs():
    return "GarenaMSDK/4.0.39(FRL-AN00a ;Android 10;nu;HK;)"

def bRuH():
    return "okhttp/3.12.1"

def yEet(length=6, chars=string.ascii_uppercase + string.digits + "-_."):
    return ''.join(random.choice(chars) for _ in range(length))

# ================== PROTOBUF ==================
def FF(value):
    out = []
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)

def GayRena(field_num, value):
    if isinstance(value, int):
        tag = (field_num << 3) | 0
        return FF(tag) + FF(value)
    elif isinstance(value, str):
        data = value.encode('utf-8')
        tag = (field_num << 3) | 2
        return FF(tag) + FF(len(data)) + data
    elif isinstance(value, bytes):
        tag = (field_num << 3) | 2
        return FF(tag) + FF(len(value)) + value
    elif isinstance(value, dict):
        sub_payload = xPro(value)
        tag = (field_num << 3) | 2
        return FF(tag) + FF(len(sub_payload)) + sub_payload
    else:
        raise TypeError(f"Unsupported type for field {field_num}: {type(value)}")

def xPro(fields_dict):
    payload = b''
    for key, value in fields_dict.items():
        field_num = int(key)
        if isinstance(value, list):
            if value and all(isinstance(v, int) for v in value):
                packed = b''.join(FF(v) for v in value)
                tag = (field_num << 3) | 2
                payload += FF(tag) + FF(len(packed)) + packed
            else:
                for elem in value:
                    payload += GayRena(field_num, elem)
        else:
            payload += GayRena(field_num, value)
    return payload

def Noob(packet):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    pad_len = 16 - (len(packet) % 16)
    if pad_len == 0:
        pad_len = 16
    plaintext_padded = packet + bytes([pad_len]) * pad_len
    return cipher.encrypt(plaintext_padded)

def Pro(data):
    from google.protobuf.internal.decoder import _DecodeVarint, _DecodeVarint32
    pos = 0
    length = len(data)
    fields = {}
    while pos < length:
        key, pos = _DecodeVarint(data, pos)
        field_num = key >> 3
        wire_type = key & 7
        if wire_type == 0:
            value, pos = _DecodeVarint(data, pos)
        elif wire_type == 2:
            size, pos = _DecodeVarint32(data, pos)
            raw = data[pos:pos+size]
            pos += size
            try:
                value = Pro(raw)
            except:
                try:
                    value = raw.decode('utf-8')
                except:
                    value = raw.hex()
        elif wire_type == 5:
            value = int.from_bytes(data[pos:pos+4], "little")
            pos += 4
        elif wire_type == 1:
            value = int.from_bytes(data[pos:pos+8], "little")
            pos += 8
        else:
            raise Exception(f"Unsupported wire type: {wire_type}")
        if field_num in fields:
            if not isinstance(fields[field_num], list):
                fields[field_num] = [fields[field_num]]
            fields[field_num].append(value)
        else:
            fields[field_num] = value
    return fields

# ================== FUNGSI DARI APP.PY ==================
def fInE(original):
    keystream = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
                 0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
    encoded = ""
    for i in range(len(original)):
        orig_byte = ord(original[i])
        key_byte = keystream[i % len(keystream)]
        result_byte = orig_byte ^ key_byte
        encoded += chr(result_byte)
    return encoded

def yAy(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

def pWe():
    try:
        return requests.get('https://api.ipify.org', timeout=3).text
    except:
        return "0.0.0.0"

# ---------- RoFl dengan dua metode signature ----------
def RoFl(session, password, use_hmac=False):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
    json_body = json.dumps(payload, separators=(',', ':'))
    
    if use_hmac:
        # Metode HMAC (dicoba jika concat gagal)
        signature = hmac.new(CLIENT_SECRET.encode(), json_body.encode(), hashlib.sha256).hexdigest()
    else:
        # Metode app.py (concat + sha256)
        data_to_sign = CLIENT_SECRET + json_body
        signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
    
    headers = {
        "User-Agent": sUs(),
        "Authorization": f"Signature {signature}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    }
    resp = session.post(url, data=json_body, headers=headers, timeout=10, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            return str(data["data"]["uid"])
        else:
            raise Exception(f"Register failed: {data}")
    else:
        try:
            error_body = resp.json()
        except:
            error_body = resp.text
        raise Exception(f"HTTP {resp.status_code} | Body: {error_body} | Method: {'HMAC' if use_hmac else 'CONCAT'} | Sig: {signature}")

# ---------- lMaO ----------
def lMaO(session, uid, password):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
    payload = {
        "client_id": 100067,
        "client_secret": CLIENT_SECRET,
        "client_type": 2,
        "password": password,
        "response_type": "token",
        "uid": uid
    }
    headers = {"User-Agent": sUs(), "Content-Type": "application/json", "Accept": "application/json"}
    resp = session.post(url, json=payload, headers=headers, timeout=10, verify=False)
    if resp.status_code != 200:
        try:
            error_body = resp.json()
        except:
            error_body = resp.text
        raise Exception(f"Token grant HTTP {resp.status_code}: {error_body}")
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Token grant failed: {data}")
    return data["data"]["access_token"], data["data"]["open_id"]

def get_base_url(region):
    if region.upper() in ["ME", "TH"]:
        return "https://loginbp.common.ggbluefox.com"
    else:
        return "https://loginbp.ggpolarbear.com"

# ---------- gG ----------
def gG(session, name, access_token, open_id, region, is_ghost=False):
    base = get_base_url(region)
    url = f"{base}/MajorRegister"
    host = base.replace("https://", "")
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1,99999)
    exp = ''.join(exp_digits[d] for d in f"{num:05d}")
    name = name[:7] + exp
    lang_code = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
    encoded_result = fInE(open_id)
    field_unicode = yAy(encoded_result)
    field_bytes = codecs.decode(field_unicode, 'unicode_escape').encode('latin1')
    fields_dict = {
        "1": name, "2": access_token, "3": open_id,
        "5": 102000007, "6": 4, "7": 1, "13": 1,
        "14": field_bytes, "15": lang_code, "16": 2
    }
    plaintext = xPro(fields_dict)
    encrypted_payload = Noob(plaintext)
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
        "Host": host, "ReleaseVersion": "OB54",
        "User-Agent": bRuH(), "X-GA": "v1 1", "X-Unity-Version": "2018.4."
    }
    resp = session.post(url, headers=headers, data=encrypted_payload, timeout=15, verify=False)
    if resp.status_code != 200:
        try:
            error_body = resp.json()
        except:
            error_body = resp.text
        raise Exception(f"MajorRegister HTTP {resp.status_code}: {error_body}")
    return Pro(resp.content)

# ---------- nIcE ----------
def nIcE(session, access_token, open_id, region, lang_code):
    base = get_base_url(region)
    url = f"{base}/MajorLogin"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = pWe()
    if region.upper() == "IND":
        device_model = random.choice(INDIAN_DEVICES)
        carrier = random.choice(INDIAN_CARRIERS)
        city = random.choice(INDIAN_CITIES)
    else:
        device_model = "Asus ASUS_AI2401_A"
        carrier = "GrameenPhone"
        city = "Dhaka"
    gpu = "Adreno (TM) 640"
    
    def qT(n):
        out = []
        while True:
            b = n & 0x7F
            n >>= 7
            if n: b |= 0x80
            out.append(b)
            if not n: break
        return bytes(out)
    
    def zZ(f, v):
        return qT((f << 3) | 0) + qT(v)
    
    def xX(f, v):
        data = v.encode() if isinstance(v, str) else v
        return qT((f << 3) | 2) + qT(len(data)) + data
    
    fields = {
        3: now_str,
        4: "free fire",
        5: 1,
        7: "1.126.5",
        8: "Android OS 5.1.1 / API-22 (LMY48Z/rel.se.infra.20220128.171448)",
        9: "Handheld",
        10: carrier,
        11: "WIFI",
        17: gpu,
        18: "OpenGL ES 3.0",
        19: "Google|4645e530-e790-4be2-ae7c-6f64d1259603",
        20: ip,
        21: lang_code,
        22: open_id,
        23: 4,
        24: "Handheld",
        25: device_model,
        26: region.upper(),
        29: access_token,
        33: carrier,
        34: "WIFI",
        37: "7428b253defc164018c604a1ebbfebdf",
        73: "/data/app/com.dts.freefireth-1/lib/arm",
        75: "H4c322aeb56444feaa151d1ea91a8f7f2|/data/app/com.dts.freefireth-1/base.apk",
        76: 2,
        78: 2,
        79: 2,
        83: "OpenGLES2",
        85: city,
        87: "android",
        88: "KqsHTywQqGHMgPbDY9P2mhkxXj/beObk/TFNpmgaucQwxyLu9hA478WEQCV0Mgaz9UivYUPpKNwPzgZhvDhSsUDMAFY=",
        90: '{"cur_rate":null,"support_etc2":false}',
        97: 1,
        98: 1,
        99: "4",
        100: "4"
    }
    
    packet = b''
    for f, v in fields.items():
        if isinstance(v, int): 
            packet += zZ(f, v)
        elif isinstance(v, str): 
            packet += xX(f, v)
        elif isinstance(v, bytes): 
            packet += xX(f, v)
    
    encrypted = Noob(packet)
    headers = {
        "Accept-Encoding": "gzip", 
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded", 
        "Expect": "100-continue",
        "ReleaseVersion": "OB54", 
        "User-Agent": bRuH(),
        "X-GA": "v1 1", 
        "X-Unity-Version": "2018.4."
    }
    resp = session.post(url, headers=headers, data=encrypted, timeout=15, verify=False)
    if resp.status_code != 200:
        try:
            error_body = resp.json()
        except:
            error_body = resp.text
        raise Exception(f"MajorLogin HTTP {resp.status_code}: {error_body}")
    decoded = Pro(resp.content)
    jwt_token = decoded.get(8)
    if isinstance(jwt_token, list):
        jwt_token = jwt_token[0] if jwt_token else None
    return decoded, jwt_token

# ---------- dUdE ----------
def dUdE(session, region_code, jwt_token):
    base = get_base_url(region_code)
    url = f"{base}/ChooseRegion"
    if region_code.upper() == "CIS":
        region_code = "ru"
    else:
        region_code = region_code.upper()
    fields_dict = {"1": region_code}
    plaintext = xPro(fields_dict)
    encrypted_payload = Noob(plaintext)
    headers = {
        "Accept-Encoding": "gzip", "Authorization": f"Bearer {jwt_token}",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "ReleaseVersion": "OB54",
        "User-Agent": bRuH(), "X-GA": "v1 1", "X-Unity-Version": "2018.4."
    }
    resp = session.post(url, headers=headers, data=encrypted_payload, timeout=10, verify=False)
    if resp.status_code != 200:
        try:
            error_body = resp.json()
        except:
            error_body = resp.text
        raise Exception(f"ChooseRegion HTTP {resp.status_code}: {error_body}")
    return True

# ================== FUNGSI UTAMA ==================
def create_account(region, account_name, password_prefix, is_ghost=False):
    session = requests.Session()
    try:
        # 1. Hardcode password dari contoh di app.py (untuk debugging)
        # password = "SPIDY_R5R6N1-VAIBHAVXYZABC"
        # 2. Atau generate dengan format yang sama
        r1 = yEet(6)
        r2 = yEet(6)
        password = f"{password_prefix.upper()}_{r1}-VAIBHAV{r2}"
        
        # Coba metode CONCAT dulu
        try:
            uid = RoFl(session, password, use_hmac=False)
        except Exception as e:
            # Jika gagal, coba metode HMAC
            try:
                uid = RoFl(session, password, use_hmac=True)
            except Exception as e2:
                # Jika keduanya gagal, lemparkan error terakhir
                raise Exception(f"CONCAT failed: {e} | HMAC failed: {e2}")
        
        access_token, open_id = lMaO(session, uid, password)
        
        name_prefix = account_name[:7]
        reg_resp = gG(session, name_prefix, access_token, open_id, region, is_ghost)
        account_id = str(reg_resp.get(3))
        if not account_id:
            raise Exception("No account_id")
        
        lang_code = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        login_resp, jwt_token = nIcE(session, access_token, open_id, region, lang_code)
        if not jwt_token:
            raise Exception("No JWT")
        
        if not is_ghost and jwt_token and region.upper() != "BR":
            try:
                dUdE(session, region, jwt_token)
            except:
                pass
        
        exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
        num = random.randint(1,99999)
        exp = ''.join(exp_digits[d] for d in f"{num:05d}")
        final_name = name_prefix + exp
        
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