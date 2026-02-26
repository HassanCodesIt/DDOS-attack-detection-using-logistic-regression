

# **🚀 DDoS Attack Detection Using Logistic Regression**  
🔍 **A machine learning model to detect DDoS attacks using Logistic Regression — with a FastAPI backend and JavaScript frontend.**  

---

## 📌 **Overview**  
This project implements a **DDoS Attack Detection System** using **Logistic Regression**. The trained model analyzes **network traffic** and classifies it as either **normal traffic** or a **DDoS attack** based on key network features.  

✅ **Algorithm:** Logistic Regression  
✅ **Model Format:** `ddos_logistic_regression.pkl`  
✅ **API:** FastAPI (`main.py`)  
✅ **Frontend:** JavaScript single-page app (`static/index.html`)  
✅ **Training Script:** `ddos_attack_detection_using_logistic_regression.py`  

---

## 📂 **Project Structure**  
```bash
📁 DDoS-Attack-Detection
│── 📜 README.md                                          # Project description (this file)
│── 📜 requirements.txt                                   # Python dependencies
│── 📜 main.py                                            # FastAPI server
│── 📁 static/
│   └── 📜 index.html                                     # JavaScript frontend
│── 📜 ddos_logistic_regression.pkl                       # Trained model file
│── 📜 ddos_attack_detection_using_logistic_regression.py # Training script
```

---

## 🔧 **Installation & Setup**  

### **🔹 Step 1: Clone the Repository**  
```bash
git clone https://github.com/HassanCodesit/DDOS-attack-detection-using-logistic-regression
cd DDOS-attack-detection-using-logistic-regression
```

### **🔹 Step 2: Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **🔹 Step 3: Start the FastAPI Server**  
```bash
uvicorn main:app --reload
```

Open your browser at **http://127.0.0.1:8000** to use the frontend.

---

## 🌐 **API Endpoints**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the JavaScript frontend |
| `GET` | `/health` | Health check — returns model info |
| `POST` | `/predict` | Classify a traffic sample (JSON body) |
| `GET` | `/docs` | Interactive Swagger UI |

### Example `/predict` request

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"pktcount": 34, "bytecount": 1200, "dur": 30, "pktrate": 1.1,
       "flows": 5, "packetins": 3, "tot_kbps": 0.32, "Protocol_TCP": 1}'
```

### Example response

```json
{
  "prediction": 0,
  "label": "Normal Traffic",
  "confidence": 0.9983,
  "probabilities": {
    "Normal Traffic": 0.9983,
    "DDoS Attack": 0.0017
  }
}
```

---

## 🖥️ **Frontend**

The built-in web UI lets you enter traffic metrics, load pre-built DDoS / Normal samples, and see the model's prediction with a colour-coded result and probability bars.

![Frontend screenshot](https://github.com/user-attachments/assets/c90f68f9-0d2f-4588-bb43-2da9faaae820)

---

## 🚀 **How It Works?**  
1️⃣ **Loads the trained model (`ddos_logistic_regression.pkl`).**  
2️⃣ **Takes network traffic data as input (via API or the web form).**  
3️⃣ **Predicts whether the traffic is normal or a DDoS attack.**  
4️⃣ **Returns prediction, confidence score, and class probabilities.**  

---

## 📊 **Run on Google Colab**  
You can also run the training notebook directly on **Google Colab**:  

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1gygTiLNHlBu1e9sOj2LC8EYtCp8tF6Zb?usp=sharing)  

