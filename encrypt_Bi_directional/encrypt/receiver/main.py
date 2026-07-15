import socket

def echonet_decrypt(data, key):
    return bytes([(b - key) % 256 for b in data])

def echonet_encrypt(data, key):
    return bytes([(b + key) % 256 for b in data])

def start_receiver():
    # เปิด TCP พอร์ต 5000 รอรับข้อมูลจาก sender
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.bind(('0.0.0.0', 5000))
    server_s.listen(5)
    print("Receiver is ready...")

    while True:
        try:
            conn, addr = server_s.accept()
            encrypted_msg = conn.recv(1024)
            
            if encrypted_msg:
                # 1. ถอดรหัสคำสั่งโคมไฟ
                decrypted_msg = echonet_decrypt(encrypted_msg, 5)
                print(f"Decrypted command from Sender: {decrypted_msg.hex()}")
                
                # 2. สร้าง UDP คุยกับโคมไฟจริง
                device_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                #เพิ่มบรรทัดนี้เข้าไปครับ เพื่อจองพอร์ต 3610 ไว้รอรับคำตอบขากลับ
                device_s.bind(('0.0.0.0', 3610)) 
                
                device_s.settimeout(1.0)
                
                # ส่งคำสั่งเข้าโคมไฟจริงเหมือนเดิม
                device_s.sendto(decrypted_msg, ('echonet-nodes-floor_lamp_real-1', 3610))
                
                try:
                    #  3. ดักฟังคำตอบที่โคมไฟจริงตอบกลับมา!
                    reply_msg, reply_addr = device_s.recvfrom(1024)
                    print(f"Received reply from real lamp: {reply_msg.hex()}")
                    
                    # เข้ารหัสขากลับ แล้วส่งย้อนผ่าน TCP ให้ Sender
                    encrypted_reply = echonet_encrypt(reply_msg, 5)
                    conn.sendall(encrypted_reply)
                    print("Encrypted reply has been sent back to Sender")
                except socket.timeout:
                    print("Real lamp did not respond within 1 second")
                
                device_s.close()
                
            conn.close()
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    start_receiver()