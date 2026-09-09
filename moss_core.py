# moss_core.py
import os, sys, json, time, random, string, hashlib, base64, codecs, re, hmac
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import urllib3
urllib3.disable_warnings()

# ---------- Konfigurasi ----------
OPT = {'timeout': 10, 'retries': 1, 'backoff': 0.5}
session = requests.Session()

HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])

REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur","TW":"zh","CIS":"ru","SAC":"es","BR":"pt"}

WRAPPING_PAIRS = [('꧁','꧂'),('『','』'),('【','】'),('《','》'),('〈','〉'),('〔','〕'),('〖','〗'),('〘','〙'),('〚','〛'),('❬','❭'),('❮','❯'),('⦅','⦆'),('⟦','⟧'),('⟨','⟩'),('⫷','⫸')]
SINGLE_SYMBOLS = ['☆','★','✧','✦','✩','✪','✫','✬','✭','✮','✯','✰','♡','♥','❤','❥','❦','❧','ゝ','々','〆','⁂','※','⁑']

# ---------- IP Spoofer ----------
class FastIPSpoofer:
    _IP_POOL = [f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(5000)]
    _IP_INDEX = 0
    @classmethod
    def get_ip(cls):
        ip = cls._IP_POOL[cls._IP_INDEX % len(cls._IP_POOL)]
        cls._IP_INDEX += 1
        return ip

# ---------- User-Agent ----------
def get_ua():
    versions = ["4.0.19P8","4.0.39","4.0.40"]
    android = ["11","12","13","14"]
    devices = ["SM-A325M","SM-A525F","SM-A536B","SM-A736B","SM-A715F","SM-A725F","SM-A515F","SM-A127F","SM-A226B","SM-A326B","SM-M325F","SM-M515F","SM-G991B","SM-G996B","SM-G998B","SM-S901B","SM-S906B","SM-S908B","SM-G781B","SM-G770F","SM-G973F","SM-G960F","SM-N986B","SM-N976B","SM-F711B","SM-F926B","SM-F731B","SM-F936B","M2012K11AG","M2101K7AG","MZB08A","Redmi Note 9","Redmi Note 10","Redmi Note 11","Redmi Note 12","Redmi 8","Redmi 9","Redmi 10","Poco X3","Poco X3 Pro","POCO F3","POCO F4","POCO M3","POCO M4 Pro","11T Pro","Mi 11","Mi 11 Lite","Mi 12","Mi 13","CPH2249","CPH2333","CPH2025","OPPO A74","OPPO A96","OPPO A77","OPPO Reno5","OPPO Reno6","OPPO Reno7","OPPO Reno8","OPPO F19","OPPO F21 Pro","V2046","V2050","V2024","vivo 1906","vivo V21","vivo V23","vivo V25","vivo Y72","vivo Y20","vivo Y75","vivo Y55","vivo X60","vivo T1","RMX3370","RMX3392","RMX2020","RMX3081","realme 7","realme 8","realme 9","realme GT","realme GT Neo","realme 9 Pro","realme 9i","realme C25","realme C31","realme C35","Pixel 4a","Pixel 5","Pixel 6","Pixel 6a","Pixel 7","Pixel 7 Pro","OnePlus 8","OnePlus 8T","OnePlus 9","OnePlus 10 Pro","OnePlus Nord","OnePlus Nord 2","Nokia 8.1","Nokia 7.2","Nokia 6.2","Nokia X20","Nokia X10","Nokia G50","ASUS_Z01QD","Asus ZenFone 8","Asus ZenFone 9","Asus ROG Phone 5","Asus ROG Phone 6","Infinix X6815","Infinix X6831","Infinix Zero 5G","TECNO KI5q","TECNO CK8n","Tecno Camon 19","Nothing Phone (1)"]
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(devices)};Android {random.choice(android)};en;ID;)"

# ---------- Enkripsi & Protobuf ----------
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

def aes_encrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(hex_data):
    data = bytes.fromhex(hex_data)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size)).hex()

# ---------- Nama random ----------
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

# ---------- Fungsi inti pembuatan akun ----------
def create_account(region, account_name, password_prefix, is_ghost=False):
    try:
        rand_part = "".join(random.choices("0123456789ABCDEF", k=16))
        password = f"{password_prefix}_{rand_part}"
        
        # 1. Register guest
        url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
        payload = {"app_id":100067, "client_type":2, "password":password, "source":2}
        body_json = json.dumps(payload, separators=(",",":"))
        signature = hmac.new(HEX_KEY, body_json.encode("utf-8"), hashlib.sha256).hexdigest()
        headers = {
            "User-Agent": get_ua(),
            "Authorization": f"Signature {signature}",
            "Content-Type": "application/json; charset=utf-8",
            "X-Forwarded-For": FastIPSpoofer.get_ip(),
            "X-Real-IP": FastIPSpoofer.get_ip(),
        }
        resp = requests.post(url, headers=headers, data=body_json, timeout=OPT['timeout'])
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get('code') != 0:
            return None
        uid = str(data['data']['uid'])

        # 2. Dapatkan token
        url2 = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers2 = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": get_ua(),
            "X-Forwarded-For": FastIPSpoofer.get_ip(),
            "X-Real-IP": FastIPSpoofer.get_ip(),
        }
        body2 = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": HEX_KEY.hex(),
            "client_id": "100067"
        }
        resp2 = requests.post(url2, headers=headers2, data=body2, timeout=OPT['timeout'])
        if resp2.status_code != 200:
            return None
        token_data = resp2.json()
        if 'open_id' not in token_data:
            return None
        open_id = token_data['open_id']
        access_token = token_data['access_token']

        # 3. Enkripsi open_id
        keystream = [0x30]*32
        encoded = "".join(chr(ord(open_id[i]) ^ keystream[i % len(keystream)]) for i in range(len(open_id)))
        field = codecs.decode(''.join(c if 32<=ord(c)<=126 else f'\\u{ord(c):04x}' for c in encoded), 'unicode_escape').encode('latin1')

        # 4. MajorRegister
        url3 = "https://loginbp.ggpolarbear.com/MajorRegister"
        name = generate_random_name(account_name)
        lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload3 = {
            1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1,
            13: 1, 14: field, 15: lang, 16: 1, 17: 1
        }
        proto_bytes = build_proto(payload3)
        encrypted = aes_encrypt(proto_bytes)
        headers3 = {
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB54",
            "User-Agent": get_ua(),
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.",
            "X-Forwarded-For": FastIPSpoofer.get_ip(),
            "X-Real-IP": FastIPSpoofer.get_ip(),
        }
        requests.post(url3, headers=headers3, data=encrypted, timeout=OPT['timeout'])

        # 5. MajorLogin (ambil account_id & jwt)
        login_result = major_login(uid, password, access_token, open_id, region, is_ghost)
        if login_result.get('account_id') == 'N/A':
            return None
        account_id = login_result['account_id']
        jwt = login_result.get('jwt_token', '')

        # 6. Force region bind (opsional)
        if not is_ghost and jwt and region.upper() != "BR":
            try:
                force_region_bind(region, jwt, is_ghost)
            except:
                pass

        return {
            "uid": uid,
            "password": password,
            "name": name,
            "region": "GHOST" if is_ghost else region.upper(),
            "account_id": account_id,
            "jwt_token": jwt
        }
    except Exception:
        return None

def major_login(uid, password, access_token, open_id, region, is_ghost):
    try:
        lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload = b''  # Gunakan payload baku dari moss.py (dipotong untuk singkat)
        # Karena payload ini sangat panjang, kita akan gunakan pendekatan alternatif:
        # kita generate ulang menggunakan protobuf untuk MajorLogin
        # Tapi agar sederhana, kita panggil API dengan cara yang sama seperti di moss.py
        # Di sini kita akan buat protobuf untuk MajorLogin secara dinamis
        fields = {
            3: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            4: "free fire",
            5: 1,
            7: "1.126.5",
            8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)",
            9: "Handheld",
            10: "ATM Mobils",
            11: "WIFI",
            17: "Adreno (TM) 640",
            18: "OpenGL ES 3.2",
            19: "Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f",
            20: "105.235.139.91",
            21: lang,
            22: open_id,
            23: 4,
            24: "Handheld",
            25: "Asus ASUS_I005DA",
            26: region.upper(),
            29: access_token,
            33: "ATM Mobils",
            34: "WIFI",
            37: "7428b253defc164018c604a1ebbfebdf",
            73: "/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm",
            75: "2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk",
            83: "OpenGLES2",
            85: "Dhaka",
            87: "android",
            88: "KqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2",
            90: '{"cur_rate":null,"support_etc2":false}'
        }
        proto = build_proto(fields)
        encrypted = encrypt_api(proto.hex())
        url = "https://loginbp.ggpolarbear.com/MajorLogin"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB54",
            "User-Agent": get_ua(),
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1",
            "X-Forwarded-For": FastIPSpoofer.get_ip(),
            "X-Real-IP": FastIPSpoofer.get_ip(),
        }
        resp = requests.post(url, headers=headers, data=bytes.fromhex(encrypted), timeout=OPT['timeout'])
        if resp.status_code == 200 and 'eyJ' in resp.text:
            text = resp.text
            jwt_start = text.find("eyJ")
            if jwt_start != -1:
                jwt_token = text[jwt_start:]
                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                    try:
                        parts = jwt_token.split('.')
                        if len(parts) >= 2:
                            payload_part = parts[1]
                            padding = 4 - len(payload_part) % 4
                            if padding != 4:
                                payload_part += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload_part)
                            data = json.loads(decoded)
                            account_id = data.get('account_id') or data.get('external_id')
                            if account_id:
                                return {"account_id": str(account_id), "jwt_token": jwt_token}
                    except:
                        pass
        return {"account_id": "N/A", "jwt_token": ""}
    except:
        return {"account_id": "N/A", "jwt_token": ""}

def force_region_bind(region, jwt_token, is_ghost):
    try:
        url = "https://loginbp.ggpolarbear.com/ChooseRegion"
        region_code = "RU" if region.upper() == "CIS" else region.upper()
        proto = build_proto({1: region_code})
        encrypted = encrypt_api(proto.hex())
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB54",
            "X-Forwarded-For": FastIPSpoofer.get_ip(),
            "X-Real-IP": FastIPSpoofer.get_ip(),
        }
        requests.post(url, headers=headers, data=bytes.fromhex(encrypted), timeout=OPT['timeout'])
    except:
        pass