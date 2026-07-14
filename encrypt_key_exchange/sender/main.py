import socket, time, os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def recv_all(conn, n):
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return bytes(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect(('receiver', 5000))
        break
    except: time.sleep(1)

raw_size = int.from_bytes(recv_all(s, 4), 'big')
params = serialization.load_pem_parameters(recv_all(s, raw_size))
priv = params.generate_private_key()
pub_bytes = priv.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
s.sendall(len(pub_bytes).to_bytes(4, 'big') + pub_bytes)

raw_size = int.from_bytes(recv_all(s, 4), 'big')
recv_pub = serialization.load_pem_public_key(recv_all(s, raw_size))

derived_key = HKDF(hashes.SHA256(), 32, None, b'handshake').derive(priv.exchange(recv_pub))
aesgcm = AESGCM(derived_key)

nonce = os.urandom(12)
encrypted = aesgcm.encrypt(nonce, b"Hello ECHONET", None)

full_payload = nonce + encrypted
s.sendall(len(full_payload).to_bytes(4, 'big') + full_payload)
s.close()