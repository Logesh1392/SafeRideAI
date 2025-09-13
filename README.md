# 🛡️ SafeRideAI – Smart Helmet & Accident Detection


## 📌 Problem Statement
Build an AI-powered system capable of detecting **helmet violations** and **road accidents** from images and videos.  
The system should:  
- Store detection results (with metadata) in the cloud  
- Allow intelligent querying through an **Agent-based RAG chatbot**  
- Send **real-time alerts for accidents via Telegram bot**  
- Generate **periodic reports** that can be emailed to stakeholders  

## 📖 Project Overview

SafeRideAI is an AI-powered platform for real-time **helmet violation** and **accident detection**, fully integrated with:

* 🚦 **YOLOv8-based object detection**
* 🗄️ **AWS RDS (Postgres)** for detection history
* ☁️ **AWS S3** for storing captured images
* 🤖 **Chatbot with FAISS + Groq LLM (RAG)**
* 📧 **Email reports with PDF attachments**
* 📊 **Streamlit dashboard with 3 tabs** (Detection, Chatbot, Reports)

---

## 📂 Folder Structure

```
SafeRideAI/
├── app.py                 # Main dashboard (Detection, Chatbot, Reports tabs)
├── detection.py           # YOLO detection module + DB + S3
├── chatbot_ui.py          # Chatbot module with FAISS + LLM
├── mailreports_ui.py      # Reports UI module (email reports)
├── db_utils.py            # Database utility functions
├── models/                # Trained models
│   └── bestmodel.pt       # YOLO trained model (helmet/accident)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚡ Features

*✅ Real-time detection (Helmet / Accident) with YOLO
*✅ AWS S3 storage for captured images
*✅ Postgres (AWS RDS) for structured detection logs
*✅ RAG-based chatbot (FAISS + Groq LLM) to query detections
*✅ Automated email reports with attachments
*✅ Streamlit dashboard with 3 main sections

---

## 🚀 Setup & Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/<your-username>/SafeRideAI.git
cd SafeRideAI
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Linux/Mac
venv\Scripts\activate        # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```ini
# Database
DB_HOST=your-db-host
DB_PORT=5432
DB_USER=your-db-user
DB_PASS=your-db-password
DB_NAME=your-db-name

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-s3-bucket-name

# Email (Gmail SMTP)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

# Groq LLM API
GROQ_API_KEY=your_groq_api_key
```

### 5️⃣ Run Streamlit App

```bash
streamlit run app.py
```

👉 Open [http://localhost:8501](http://localhost:8501) in your browser 🎉

---

## 📊 Dashboard Overview

* **Detection Tab** → Run YOLO detection, view bounding boxes, save to DB + S3
* **Chatbot Tab** → Ask questions about detections or general safety queries
* **Reports Tab** → Generate & email detection history reports

---

## 🛠️ Tech Stack

* **Computer Vision** → YOLOv8 (ultralytics)
* **Database** → PostgreSQL (AWS RDS)
* **Cloud Storage** → AWS S3
* **LLM** → Groq API (Llama 3.1)
* **Vector Search** → FAISS + SentenceTransformers
* **Frontend** → Streamlit
* **Email Service** → Gmail SMTP

---

## ⚠️ Notes

* Store trained models inside the `models/` folder (e.g., `bestmodel.pt`).
* If your model file is larger than **100MB**, don’t push it to GitHub. Instead:

  * Add it to `.gitignore`
  * Upload it to **S3 / Google Drive**, and update README with download instructions.

---


---

## 👤 Author

**Logeshwaran M**
📧 Email: [lokesh.waran1392@gmail.com](mailto:lokesh.waran1392@gmail.com)
🚀 SafeRideAI Project
