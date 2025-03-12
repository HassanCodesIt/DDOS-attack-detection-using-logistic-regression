# -*- coding: utf-8 -*-
"""DDOS attack detection using logistic regression.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gygTiLNHlBu1e9sOj2LC8EYtCp8tF6Zb
"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("aikenkazin/ddos-sdn-dataset")

print("Path to dataset files:", path)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load dataset
file_path = "/root/.cache/kagglehub/datasets/aikenkazin/ddos-sdn-dataset/versions/1/dataset_sdn.csv"
df = pd.read_csv(file_path)

# Display first 5 rows
df.head()

# Check dataset info
df.info()

# Check missing values
print("\nMissing values in dataset:\n", df.isnull().sum())

# Check class distribution
print("\nClass distribution:\n", df['label'].value_counts())

# Define the target column
target_column = 'label'

# Drop non-relevant features
X = df.drop(columns=[target_column, 'dt'])  # 'dt' is a timestamp, removing it
y = df[target_column]

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Training size:", X_train.shape, "Testing size:", X_test.shape)

# Drop non-numeric columns (IP addresses)
drop_columns = ['dt']  # Remove timestamp

# Identify categorical columns
categorical_columns = ['label']  # The target variable is categorical but doesn't need encoding

# Select numerical columns only
X = df.drop(columns=drop_columns + categorical_columns)

# Convert categorical IP addresses and protocol indicators into numerical form (One-Hot Encoding)
X = pd.get_dummies(X, drop_first=True)  # Converts categorical columns into binary values

# Extract target variable again
y = df['label']

# Train-test split again
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Data successfully processed! 🚀")

import numpy as np

# Check for NaN values
print("NaNs in X_train_scaled:", np.isnan(X_train_scaled).sum())
print("NaNs in X_test_scaled:", np.isnan(X_test_scaled).sum())

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy="mean")

# Apply imputation
X_train_scaled = imputer.fit_transform(X_train_scaled)
X_test_scaled = imputer.transform(X_test_scaled)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")

# Classification Report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix
plt.figure(figsize=(6,4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.title("Confusion Matrix")
plt.show()

import joblib

# Save the trained model
joblib.dump(model, "ddos_logistic_regression.pkl")
print("Model saved successfully!")

# Load the model
loaded_model = joblib.load("ddos_logistic_regression.pkl")

# Make a prediction on new data (Example: First row from test set)
sample_input = X_test_scaled[0].reshape(1, -1)  # Reshape for single prediction
predicted_label = loaded_model.predict(sample_input)

print("Predicted Label:", predicted_label[0])

label_map = {0: "Normal Traffic", 1: "DDoS Attack"}
print("Predicted Label:", label_map[predicted_label[0]])

joblib.dump(list(X_train.columns), "feature_names.pkl")

import joblib
import numpy as np
import pandas as pd

# Load trained model
model = joblib.load("ddos_logistic_regression.pkl")

# Load saved feature names (ensures input matches training format)
feature_names = joblib.load("feature_names.pkl")  # Must be saved during training

# Function to format input correctly
def format_input(sample_dict):
    """
    Converts a dictionary of sample features into a NumPy array matching model input.
    Ensures all expected features are present.
    """
    df_sample = pd.DataFrame([sample_dict])  # Convert to DataFrame

    # Add missing columns with default value 0
    for col in feature_names:
        if col not in df_sample:
            df_sample[col] = 0

    # Ensure correct column order
    df_sample = df_sample[feature_names]

    return df_sample.to_numpy()

# Function to detect DDoS attack
def check_ddos(sample_dict):
    """
    Predicts if the network traffic sample is a DDoS attack.

    :param sample_dict: Dictionary of feature values
    :return: Predicted class (0 = Normal, 1 = DDoS Attack)
    """
    sample_input = format_input(sample_dict)
    predicted_label = model.predict(sample_input)[0]  # Make prediction
    label_map = {0: "✅ Normal Traffic", 1: "🚨 DDoS Attack Detected!"}
    return label_map[predicted_label]

# Example input (fill in actual values)
sample_data = {
    "pktcount": 34,
    "bytecount": 1200,
    "dur": 30,
    "tot_kbps": 200,
    "port_no": 80,
    "pktrate": 10,
    "flows": 50,
    "packetins": 5,
    "Protocol_TCP": 1,
    "Protocol_UDP": 0,
    "Protocol_ICMP": 0,
    # All missing features will be added automatically
}

# Run detection
result = check_ddos(sample_data)
print("🚦 Prediction:", result)

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# Load trained model
model = joblib.load("ddos_logistic_regression.pkl")

# Load saved feature names (ensures input matches training format)
feature_names = joblib.load("feature_names.pkl")  # This was saved during training

# Load dataset
df = pd.read_csv("/root/.cache/kagglehub/datasets/aikenkazin/ddos-sdn-dataset/versions/1/dataset_sdn.csv")

# Define features and target
target_column = "label"
X = df.drop(columns=[target_column, "dt"], errors="ignore")  # Drop timestamp if present
y = df[target_column]

# Ensure all feature names exist
for col in feature_names:
    if col not in X.columns:
        X[col] = 0  # Fill missing features with default value

# Reorder columns to match training format
X = X[feature_names]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv("/root/.cache/kagglehub/datasets/aikenkazin/ddos-sdn-dataset/versions/1/dataset_sdn.csv")

# Count number of normal vs. attack instances
attack_counts = df["label"].value_counts().sort_index()

# Labels
categories = ["Normal Traffic", "DDoS Attack"]
values = attack_counts.tolist()

# Print counts
print(f"Normal Traffic: {values[0]}")
print(f"DDoS Attacks: {values[1]}")

# Set Seaborn style
sns.set_style("darkgrid")

# Create a line plot
plt.figure(figsize=(8, 5))
plt.plot(categories, values, marker="o", linestyle="-", color="red", linewidth=2, markersize=8)

# Add labels and title
plt.xlabel("Traffic Type")
plt.ylabel("Number of Instances")
plt.title("DDoS Attacks vs. Normal Traffic in Dataset")
plt.ylim(0, max(values) * 1.2)  # Adjust y-axis for better visibility

# Show the plot
plt.show()