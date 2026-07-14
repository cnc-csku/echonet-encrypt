import socket
from cryptography.hazmat.primitives.asymmetric import dh
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

parameters = dh.generate_parameters(generator=2, key_size=2048)
params_bytes = parameters.parameter_bytes(serialization.Encoding.PEM, serialization.ParameterFormat.PKCS3)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 5000))
s.listen(5)

print("Receiver พร้อม...", flush=True)
while True:
    conn, addr = s.accept()
    try:
        conn.sendall(len(params_bytes).to_bytes(4, 'big') + params_bytes)
        
        size = int.from_bytes(recv_all(conn, 4), 'big')
        sender_pub = serialization.load_pem_public_key(recv_all(conn, size))
        
        priv = parameters.generate_private_key()
        pub_bytes = priv.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        conn.sendall(len(pub_bytes).to_bytes(4, 'big') + pub_bytes)
        
        derived_key = HKDF(hashes.SHA256(), 32, None, b'handshake').derive(priv.exchange(sender_pub))
        aesgcm = AESGCM(derived_key)
        
        msg_size = int.from_bytes(recv_all(conn, 4), 'big')
        encrypted_data = recv_all(conn, msg_size)
        
        decrypted = aesgcm.decrypt(encrypted_data[:12], encrypted_data[12:], None)
        print(f"ได้รับข้อความ: {decrypted.decode()}", flush=True)
        
    except Exception as e: print(f"Error: {e}", flush=True)
    finally: conn.close()