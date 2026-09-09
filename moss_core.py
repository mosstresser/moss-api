# moss_core.py - Final dengan perbaikan
import os, sys, json, time, random, string, hashlib, base64, codecs, re, hmac
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import urllib3
urllib3.disable_warnings()

# ================== KONSTANTA ==================
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur","TW":"zh","CIS":"ru","SAC":"es","BR":"pt"}

# ================== IP SPOOFER & UA ==================
class FastIPSpoofer:
    _IP_POOL = [f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(5000)]
    _IP_INDEX = 0
    @classmethod
    def get_ip(cls):
        ip = cls._IP_POOL[cls._IP_INDEX % len(cls._IP_POOL)]
        cls._IP_INDEX += 1
        return ip

def get_ua():
    versions = ["4.0.19P8","4.0.39","4.0.40"]
    android = ["11","12","13","14"]
    devices = ["SM-A325M","SM-A525F","SM-A536B","SM-A736B","SM-A715F","SM-A725F","SM-A515F","SM-A127F","SM-A226B","SM-A326B","SM-M325F","SM-M515F","SM-G991B","SM-G996B","SM-G998B","SM-S901B","SM-S906B","SM-S908B","SM-G781B","SM-G770F","SM-G973F","SM-G960F","SM-N986B","SM-N976B","SM-F711B","SM-F926B","SM-F731B","SM-F936B","M2012K11AG","M2101K7AG","MZB08A","Redmi Note 9","Redmi Note 10","Redmi Note 11","Redmi Note 12","Redmi 8","Redmi 9","Redmi 10","Poco X3","Poco X3 Pro","POCO F3","POCO F4","POCO M3","POCO M4 Pro","11T Pro","Mi 11","Mi 11 Lite","Mi 12","Mi 13","CPH2249","CPH2333","CPH2025","OPPO A74","OPPO A96","OPPO A77","OPPO Reno5","OPPO Reno6","OPPO Reno7","OPPO Reno8","OPPO F19","OPPO F21 Pro","V2046","V2050","V2024","vivo 1906","vivo V21","vivo V23","vivo V25","vivo Y72","vivo Y20","vivo Y75","vivo Y55","vivo X60","vivo T1","RMX3370","RMX3392","RMX2020","RMX3081","realme 7","realme 8","realme 9","realme GT","realme GT Neo","realme 9 Pro","realme 9i","realme C25","realme C31","realme C35","Pixel 4a","Pixel 5","Pixel 6","Pixel 6a","Pixel 7","Pixel 7 Pro","OnePlus 8","OnePlus 8T","OnePlus 9","OnePlus 10 Pro","OnePlus Nord","OnePlus Nord 2","Nokia 8.1","Nokia 7.2","Nokia 6.2","Nokia X20","Nokia X10","Nokia G50","ASUS_Z01QD","Asus ZenFone 8","Asus ZenFone 9","Asus ROG Phone 5","Asus ROG Phone 6","Infinix X6815","Infinix X6831","Infinix Zero 5G","TECNO KI5q","TECNO CK8n","Tecno Camon 19","Nothing Phone (1)"]
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(devices)};Android {random.choice(android)};en;ID;)"

# ================== ENKRIPSI & PROTOBUF ==================
def encode_varint(n):
    if n < 0: return b''
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n: byte |= 0x80
        result.append(byte)
        if not n: break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, dict):
        nested = create_proto_field(field_num, value)
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(nested)) + nested
    elif isinstance(value, int):
        header = (field_num << 3) | 0
        return encode_varint(header) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(encoded_val)) + encoded_val
    return b''

def build_proto(fields):
    return b''.join(create_proto_field(k, v) for k, v in fields.items())

def aes_encrypt(hex_data):
    data = bytes.fromhex(hex_data)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(plain_hex):
    plain = bytes.fromhex(plain_hex)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plain, AES.block_size)).hex()

# ================== NAMA RANDOM ==================
WRAPPING_PAIRS = [('꧁','꧂'),('『','』'),('【','】'),('《','》'),('〈','〉'),('〔','〕'),('〖','〗'),('〘','〙'),('〚','〛'),('❬','❭'),('❮','❯'),('⦅','⦆'),('⟦','⟧'),('⟨','⟩'),('⫷','⫸')]
SINGLE_SYMBOLS = ['☆','★','✧','✦','✩','✪','✫','✬','✭','✮','✯','✰','♡','♥','❤','❥','❦','❧','ゝ','々','〆','⁂','※','⁑']

def generate_exponent():
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1, 9999)
    return ''.join(exp_digits[d] for d in f"{num:04d}")

def generate_random_name(base):
    exponent = generate_exponent()
    rand = random.random()
    if rand < 0.4:
        left, right = random.choice(WRAPPING_PAIRS)
        return f"{left}{base}{right}{exponent}"
    elif rand < 0.7:
        return f"{base}{random.choice(SINGLE_SYMBOLS)}{exponent}"
    else:
        return f"{base}_{exponent}"

# ================== FUNGSI DARI MOSS.PY ASLI ==================
def get_base_url(region):
    if region.upper() in ["ME", "TH"]:
        return "https://loginbp.common.ggbluefox.com"
    else:
        return "https://loginbp.ggpolarbear.com"

def RoFl(session, password):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
    json_body = json.dumps(payload, separators=(',', ':'))
    data_to_sign = HEX_KEY.hex() + json_body
    signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
    headers = {
        "User-Agent": get_ua(),
        "Authorization": f"Signature {signature}",
        "Content-Type": "application/json; charset=utf-8",
        "X-Forwarded-For": FastIPSpoofer.get_ip(),
        "X-Real-IP": FastIPSpoofer.get_ip(),
    }
    resp = session.post(url, data=json_body, headers=headers, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            return str(data["data"]["uid"])
        else:
            raise Exception(f"Register failed: {data}")
    else:
        raise Exception(f"Register HTTP {resp.status_code}: {resp.text}")

def lMaO(session, uid, password):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
    payload = {
        "client_id":100067, "client_secret":HEX_KEY.hex(), "client_type":2,
        "password":password, "response_type":"token", "uid":uid
    }
    headers = {"User-Agent": get_ua(), "Content-Type": "application/json",
               "X-Forwarded-For": FastIPSpoofer.get_ip(),
               "X-Real-IP": FastIPSpoofer.get_ip()}
    resp = session.post(url, json=payload, headers=headers, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"Token grant HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Token grant failed: {data}")
    return data["data"]["access_token"], data["data"]["open_id"]

def gG(session, name, access_token, open_id, region, is_ghost=False):
    base = get_base_url(region)
    url = f"{base}/MajorRegister"
    keystream = [0x30]*32
    encoded = "".join(chr(ord(open_id[i]) ^ keystream[i % len(keystream)]) for i in range(len(open_id)))
    field_unicode = ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in encoded)
    field_bytes = codecs.decode(field_unicode, 'unicode_escape').encode('latin1')
    lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
    fields_dict = {
        "1": name, "2": access_token, "3": open_id,
        "5": 102000007, "6": 4, "7": 1, "13": 1,
        "14": field_bytes, "15": lang, "16": 2
    }
    plaintext = build_proto(fields_dict)
    encrypted_payload = aes_encrypt(plaintext.hex())
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer", "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
        "Host": base.replace("https://", ""), "ReleaseVersion": "OB54",
        "User-Agent": get_ua(), "X-GA": "v1 1", "X-Unity-Version": "2018.4.",
        "X-Forwarded-For": FastIPSpoofer.get_ip(),
        "X-Real-IP": FastIPSpoofer.get_ip(),
    }
    resp = session.post(url, headers=headers, data=encrypted_payload, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"MajorRegister HTTP {resp.status_code}: {resp.text}")
    # Tidak perlu parse, asal sukses
    return True

def nIcE(session, access_token, open_id, region, is_ghost=False):
    base = get_base_url(region)
    url = f"{base}/MajorLogin"
    lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
    ip = FastIPSpoofer.get_ip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_model = "Asus ASUS_I005DA"
    carrier = "ATM Mobils"
    city = "Dhaka"
    gpu = "Adreno (TM) 640"
    fields = {
        3: now_str,
        4: "free fire",
        5: 1,
        7: "1.126.5",
        8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)",
        9: "Handheld",
        10: carrier,
        11: "WIFI",
        17: gpu,
        18: "OpenGL ES 3.2",
        19: "Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f",
        20: ip,
        21: lang,
        22: open_id,
        23: 4,
        24: "Handheld",
        25: device_model,
        26: region.upper(),
        29: access_token,
        33: carrier,
        34: "WIFI",
        37: "7428b253defc164018c604a1ebbfebdf",
        73: "/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm",
        75: "2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk",
        76: 2,
        78: 2,
        79: 2,
        83: "OpenGLES2",
        85: city,
        87: "android",
        88: "KqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2",
        90: '{"cur_rate":null,"support_etc2":false}',
        97: 1,
        98: 1,
        99: "4",
        100: "4"
    }
    proto = build_proto(fields)
    encrypted = encrypt_api(proto.hex())
    headers = {
        "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded", "Expect": "100-continue",
        "ReleaseVersion": "OB54", "User-Agent": get_ua(),
        "X-GA": "v1 1", "X-Unity-Version": "2018.4.",
        "X-Forwarded-For": FastIPSpoofer.get_ip(),
        "X-Real-IP": FastIPSpoofer.get_ip(),
    }
    resp = session.post(url, headers=headers, data=bytes.fromhex(encrypted), timeout=20)
    if resp.status_code != 200:
        raise Exception(f"MajorLogin HTTP {resp.status_code}: {resp.text}")
    text = resp.text
    jwt_start = text.find("eyJ")
    if jwt_start == -1:
        raise Exception("No JWT found in response")
    jwt_token = text[jwt_start:]
    second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
    if second_dot == -1:
        raise Exception("Invalid JWT format")
    jwt_token = jwt_token[:second_dot + 44]
    try:
        parts = jwt_token.split('.')
        if len(parts) < 2:
            raise Exception("JWT missing parts")
        payload_part = parts[1]
        padding = 4 - len(payload_part) % 4
        if padding != 4:
            payload_part += '=' * padding
        decoded = base64.urlsafe_b64decode(payload_part)
        data = json.loads(decoded)
        account_id = data.get('account_id') or data.get('external_id')
        if not account_id:
            raise Exception("account_id not found in JWT")
        return {"account_id": str(account_id), "jwt_token": jwt_token}
    except Exception as e:
        raise Exception(f"Failed to parse JWT: {e}")

def dUdE(session, region_code, jwt_token):
    base = get_base_url(region_code)
    url = f"{base}/ChooseRegion"
    if region_code.upper() == "CIS":
        region_code = "ru"
    else:
        region_code = region_code.upper()
    fields_dict = {"1": region_code}
    plaintext = build_proto(fields_dict)
    encrypted_payload = encrypt_api(plaintext.hex())
    headers = {
        "Accept-Encoding": "gzip", "Authorization": f"Bearer {jwt_token}",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "ReleaseVersion": "OB54",
        "User-Agent": get_ua(), "X-GA": "v1 1", "X-Unity-Version": "2018.4.",
        "X-Forwarded-For": FastIPSpoofer.get_ip(),
        "X-Real-IP": FastIPSpoofer.get_ip(),
    }
    resp = session.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=20)
    if resp.status_code != 200:
        raise Exception(f"ChooseRegion HTTP {resp.status_code}: {resp.text}")
    return True

# ================== FUNGSI UTAMA ==================
def create_account(region, account_name, password_prefix, is_ghost=False):
    session = requests.Session()
    try:
        password = f"{password_prefix}_{''.join(random.choices('0123456789ABCDEF', k=16))}"
        uid = RoFl(session, password)
        access_token, open_id = lMaO(session, uid, password)
        name = generate_random_name(account_name)
        gG(session, name, access_token, open_id, region, is_ghost)
        login_result = nIcE(session, access_token, open_id, region, is_ghost)
        account_id = login_result['account_id']
        jwt = login_result['jwt_token']
        if not is_ghost and jwt and region.upper() != "BR":
            try:
                dUdE(session, region, jwt)
            except Exception as e:
                # Gagal force region tidak masalah
                pass
        return {
            "uid": uid,
            "password": password,
            "name": name,
            "region": "GHOST" if is_ghost else region.upper(),
            "account_id": account_id,
            "jwt_token": jwt
        }
    except Exception as e:
        return {"error": str(e)}