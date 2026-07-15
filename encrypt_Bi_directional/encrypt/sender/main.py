import socket
import struct

def echonet_encrypt(data, key):
    return bytes([(b + key) % 256 for b in data])

def echonet_decrypt(data, key):
    return bytes([(b - key) % 256 for b in data])

def start_dynamic_sender():
    MCAST_GRP = '224.0.23.0'
    MCAST_PORT = 3610

    server_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_s.bind(('', MCAST_PORT))

    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    server_s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("Sender (Proxy) is ready...")

    while True:
        try:
            # รับข้อมูลดิบจาก Cloud (และจำ IP/Port ของ Cloud ไว้ในตัวแปร addr)
            raw_msg, addr = server_s.recvfrom(1024)
            
            if raw_msg:
                print(f"Received command from Cloud ({addr}): {raw_msg.hex()}")
                
                # เข้ารหัสข้อมูล
                encrypted_msg = echonet_encrypt(raw_msg, 5)
                
                # ส่งต่อหา Receiver ด้วย TCP พอร์ต 5000
                client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_s.connect(('receiver', 5000)) 
                client_s.sendall(encrypted_msg)
                
                # 🌟 4. รอรับคำตอบขากลับจาก Receiver ผ่านท่อ TCP เส้นเดิม
                client_s.settimeout(1.5)
                try:
                    encrypted_reply = client_s.recv(1024)
                    if encrypted_reply:
                        # ถอดรหัสคำตอบ
                        decrypted_reply = echonet_decrypt(encrypted_reply, 5)
                        print(f"Decrypted return reply: {decrypted_reply.hex()}")
                        
                        # 🌟 5. ยิง UDP ส่งคำตอบกลับไปหา Cloud ตัวแม่!
                        server_s.sendto(decrypted_reply, addr)
                        print(f"Successfully sent reply back to Cloud!")
                except socket.timeout:
                    print("No response data from Receiver")
                
                client_s.close()
                print("-" * 40)
                
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    start_dynamic_sender()