FROM python:3.9-slim
WORKDIR /app
COPY . .

# เพิ่มบรรทัดนี้เพื่อบังคับให้ Python พ่น print() ออกมาทันที
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]