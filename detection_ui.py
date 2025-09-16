# detection_ui.py
import streamlit as st
from ultralytics import YOLO
from PIL import Image
from pathlib import Path
import os
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
import requests
from datetime import datetime
import tempfile
from db_utils import get_db_connection

# Load YOLO model
@st.cache_resource(show_spinner=False)
def load_model(model_path: str):
    return YOLO(model_path)

MODEL_PATH = r"C:\Users\Administrator\Desktop\SafeRideAI\model\best.pt"
model = load_model(MODEL_PATH)

# AWS S3 Config
S3_BUCKET = "saferideai-detections-2025"
s3_client = boto3.client("s3")

def upload_to_s3(file_path, s3_bucket, s3_key):
    try:
        s3_client.upload_file(file_path, s3_bucket, s3_key)
        return f"s3://{s3_bucket}/{s3_key}"
    except NoCredentialsError:
        st.error("⚠️ AWS credentials not found.")
        return None

# Ensure DB table exists
def ensure_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id SERIAL PRIMARY KEY,
                class TEXT,
                confidence FLOAT,
                box_coordinates TEXT,
                file_name TEXT,
                s3_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"⚠️ Could not create DB table: {e}")

ensure_table()

# Telegram Alert
def send_telegram_alert(file_path, detection_data, s3_path=None):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption_lines = []
    for det in detection_data:
        label = det['Class']
        conf = det['Confidence']
        coords = det['Box Coordinates']
        line = f"🕒 {timestamp}\n🏷️ Class: {label}\n✅ Confidence: {conf:.1f}%\n📍 Location: {coords}"
        if s3_path:
            line += f"\nS3 Path: {s3_path}"
        caption_lines.append(line)
    caption = "\n\n".join(caption_lines)

    if os.path.exists(file_path) and file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        with open(file_path, "rb") as img:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": img}
            )
    else:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": caption}
        )

# Detection Function
def process_detection(file_path, uploaded_file_name):
    results = model.predict(source=file_path, conf=0.25, save=True)
    detection_records = []
    s3_path = None

    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                coords = [round(x, 1) for x in box.xyxy[0].tolist()]
                label = r.names[cls_id]

                detection_records.append({
                    "Class": label,
                    "Confidence": round(conf * 100, 2),
                    "Box Coordinates": coords
                })

                # S3 upload
                s3_key = f"detections/{uploaded_file_name}"
                s3_path = upload_to_s3(file_path, S3_BUCKET, s3_key)

                # Insert into DB
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO detections (class, confidence, box_coordinates, file_name, s3_path)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (label, conf, str(coords), uploaded_file_name, s3_path))
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"⚠️ DB Insert Failed: {e}")

    # Telegram alert
    if any("Accident" in d['Class'] or "Without Helmet" in d['Class'] for d in detection_records):
        send_telegram_alert(file_path, detection_records, s3_path)

    return detection_records

# Streamlit UI for detection tab
def detection_ui():
    st.subheader("📤 Upload Image/Video for Detection")
    uploaded_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            file_path = temp_file.name

        if uploaded_file.type.startswith("image"):
            st.image(Image.open(file_path), caption="📸 Uploaded Image", use_container_width=True)
        else:
            st.video(file_path)

        detections = process_detection(file_path, uploaded_file.name)
        if detections:
            df = pd.DataFrame(detections)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ No detections found.")
