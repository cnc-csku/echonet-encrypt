import socket

def echonet_decrypt(data, key):
    # ฟังก์ชันถอดรหัส (ลบกุญแจออก)
    return bytes([(b - key) % 256 for b in data])

def start_receiver():
    # สร้าง Socket แบบ TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 5000)) # เปิดพอร์ต 5000 รอรับ
    s.listen(5) # รอรับได้สูงสุด 5 การเชื่อมต่อพร้อมกัน
    print("Receiver พร้อมทำงานแล้ว... กำลังรอข้อมูล")

    while True:
        try:
            conn, addr = s.accept() # รอรับการเชื่อมต่อจาก Sender
            data = conn.recv(1024)
            if data:
                decrypted_data = echonet_decrypt(data, 5)
                print(f"ได้รับข้อมูลจาก {addr}: {decrypted_data.hex()}")
            conn.close() # ปิดการเชื่อมต่อชั่วคราวเพื่อรอ Sender ตัวถัดไป
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            break

if __name__ == "__main__":
    start_receiver()