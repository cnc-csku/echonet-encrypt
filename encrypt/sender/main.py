import socket
import time

def echonet_encrypt(data, key):
    return bytes([(b + key) % 256 for b in data])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 'receiver' คือชื่อ service ที่เราจะตั้งใน docker-compose
s.connect(('receiver', 5000))
msg = b'\x80\x01\x02'
s.sendall(echonet_encrypt(msg, 5))
s.close()