

# **🚀 DDoS Attack Detection Using Logistic Regression**  
🔍 **A machine learning model to detect DDoS attacks using Logistic Regression.**  

---

## 📌 **Overview**  
This project implements a **DDoS Attack Detection System** using **Logistic Regression**. The trained model analyzes **network traffic** and classifies it as either **normal traffic** or a **DDoS attack** based on key network features.  

✅ **Algorithm:** Logistic Regression  
✅ **Model Format:** `ddos_logistic_regression.pkl`  
✅ **Prediction Script:** `ddos_attack_detection_using_logistic_regression.py`  

---

## 📂 **Project Structure**  
```bash
📁 DDoS-Attack-Detection
│── 📜 README.md                  # Project description (this file)
│── 📜 ddos_logistic_regression.pkl # Trained model file
│── 📜 ddos_attack_detection_using_logistic_regression.py # Python script for DDoS detection
```

---

## 🔧 **Installation & Setup**  

### **🔹 Step 1: Clone the Repository**  
```bash
git clone https://github.com/HassanCodes/DDoS-Detection.git
cd DDoS-Detection
```

### **🔹 Step 2: Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **🔹 Step 3: Run the Detection Script**  
```bash
python ddos_attack_detection_using_logistic_regression.py
```

---

## 🚀 **How It Works?**  
1️⃣ **Loads the trained model (`ddos_logistic_regression.pkl`).**  
2️⃣ **Takes network traffic data as input.**  
3️⃣ **Predicts whether the traffic is normal or a DDoS attack.**  

---

## 📊 **Run on Google Colab**  
You can also run this project directly on **Google Colab**:  

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1gygTiLNHlBu1e9sOj2LC8EYtCp8tF6Zb?usp=sharing)  

---

## 📊 **Usage Example: Predicting DDoS Attacks**  
```python
import joblib
import pandas as pd

# Load trained model
model = joblib.load("ddos_logistic_regression.pkl")

# Sample input data (replace with real values)
sample_data = {
    "pktcount": 50,
    "bytecount": 1500,
    "dur": 25,
    "tot_kbps": 300,
    "port_no": 443,
    "pktrate": 20,
    "flows": 75,
    "packetins": 10,
    "Protocol_TCP": 1,
    "Protocol_UDP": 0,
    "Protocol_ICMP": 0,
}

# Convert to DataFrame
df_sample = pd.DataFrame([sample_data])

# Make prediction
predicted_label = model.predict(df_sample)[0]
label_map = {0: "✅ Normal Traffic", 1: "🚨 DDoS Attack Detected!"}
print("🚦 Prediction:", label_map[predicted_label])
```

---


---



---

