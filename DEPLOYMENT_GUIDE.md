# 🚀 Kanpur Traffic AI - Deployment Guide

This document provides instructions for deploying your AI-powered traffic prediction app to high-availability cloud platforms like **Render**, **Railway**, or **DigitalOcean**.

---

## 1. Prepare Your Database (MongoDB Atlas)
Don't use your local MongoDB in production. 
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Deploy a free cluster and create a database named `kanpur_trafficdb`.
3. Go to **Network Access** and add `0.0.0.0/0` (Allow access from anywhere).
4. Get your **Connection String** from the "Connect" button.

## 2. Seed Data to Cloud DB
To move your current data to the cloud, update your `process_and_seed.py` temporarily with your Atlas URI and run it once:
```python
# In process_and_seed.py
client = MongoClient("YOUR_ATLAS_CONNECTION_STRING")
```

## 3. Deployment Configuration (Render.com)
Render is the easiest platform for this stack.

### A. Repository Setup
1. Push your entire project folder to **GitHub**.

### B. Create Web Service
1. Link your GitHub repo to Render.
2. Select **Node** as the environment.
3. **Build Command**:
   ```bash
   cd frontend && npm install && npm run build && cd ../backend && npm install
   ```
4. **Start Command**:
   ```bash
   cd backend && node server.js
   ```

### C. Environment Variables (Secret Files)
Add these in the Render Dashboard under **Environment**:
- `MONGODB_URI`: Your Atlas connection string.
- `PYTHON_PATH`: Set to `python3`.
- `PORT`: 5000 (Render will override this automatically, which is fine).

### D. Python Dependencies
Render will detect the `requirements.txt` in the root and automatically install `pandas`, `scikit-learn`, etc.

---

## 4. Manual Testing After Deployment
1. Visit your provided Render URL (e.g., `https://kanpur-traffic.onrender.com`).
2. Verify that the **Localities** list loads (this confirms MongoDB connection).
3. Try a **Prediction** (this confirms the Node -> Python bridge is working).

## 🛠️ Maintenance
If you update your AI model (`traffic_model.pkl`), simply push the new `.pkl` file to GitHub, and Render will automatically redeploy the latest version.
