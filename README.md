# ⚡ PhishGuard — AI Phishing Detection System

> Final-year project: ML-powered URL threat assessment.
> **90.76% accuracy** on 2,488-URL dataset · GradientBoosting · FastAPI · React

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND  React + Vite  :5173                       │
│  InputForm → axios POST /predict                    │
└──────────────────────┬──────────────────────────────┘
                       │  { "url": "https://..." }
                       ▼
┌─────────────────────────────────────────────────────┐
│  BACKEND  FastAPI  :8000                             │
│  1. url_validator.py     → structural checks         │
│  2. feature_extractor.py → 13 numeric features       │
│  3. model.pkl            → predict_proba()           │
│  4. _build_explanations  → human-readable reasons    │
└──────────────────────┬──────────────────────────────┘
                       │  [[f1, f2, ..., f13]]
                       ▼
┌─────────────────────────────────────────────────────┐
│  ML MODEL  GradientBoostingClassifier + Scaler       │
│  Accuracy: 90.76% · ROC-AUC: 0.96+                  │
│  Returns: [P(legit), P(phishing)]                    │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
# From project root
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Start server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

### 3. Retrain Model (optional)

```bash
python -m backend.model.train --data phishing_url_dataset.csv
```

### 4. Run Tests

```bash
# From project root
pip install pytest httpx
pytest backend/tests/ -v
```

---

## 📡 API Reference

### `POST /predict`

**Request:**
```json
{ "url": "https://example.com" }
```

**Response:**
```json
{
  "url": "https://example.com",
  "status": "SAFE",
  "risk_score": 8.4,
  "confidence": 93.2,
  "features": [
    { "name": "isHttps", "value": 1.0, "risk": false },
    ...
  ],
  "explanations": ["✅ No suspicious indicators found."],
  "processing_time_ms": 3.8
}
```

**Status values:** `SAFE` (score < 30) · `SUSPICIOUS` (30–65) · `PHISHING` (≥ 65)

---

### `GET /health`

```json
{ "status": "ok", "model_loaded": true, "features": ["url_length", ...] }
```

---

## 🧩 Features Extracted

| Feature | Description |
|---|---|
| `url_length` | Total character count of URL |
| `valid_url` | Structural validity (has scheme + host) |
| `at_symbol` | Presence of `@` (domain-spoofing trick) |
| `sensitive_words_count` | Count of keywords like login, verify, secure |
| `path_length` | Length of URL path component |
| `isHttps` | 1 if HTTPS, 0 if HTTP |
| `nb_dots` | Number of `.` in URL |
| `nb_hyphens` | Number of `-` in URL |
| `nb_and` | Number of `&` (query parameters) |
| `nb_or` | Number of `\|` |
| `nb_www` | Count of "www" |
| `nb_com` | Count of ".com" |
| `nb_underscore` | Number of `_` |

---

## 🔌 Chrome Extension

1. Open `chrome://extensions/` in Chrome
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `chrome_extension/` folder
5. Make sure backend is running on port 8000

---

## ⚠️ Common Errors & Fixes

| Error | Fix |
|---|---|
| `CORS error` in browser console | Check `ALLOWED_ORIGINS` in `backend/config.py` includes your frontend URL |
| `Model file not found` | Run `uvicorn` from project root, not from `backend/` folder |
| `422 Unprocessable Entity` | URL is missing `http://` or `https://` scheme |
| `Connection refused` on frontend | Backend not running — start it with `uvicorn backend.main:app --reload` |
| `ModuleNotFoundError: backend` | Run commands from project root, not inside `backend/` |

---

## 📊 Model Performance

- **Dataset:** 2,488 URLs (1,313 legitimate, 1,175 phishing)
- **Algorithm:** GradientBoostingClassifier (200 estimators, depth=5, lr=0.1)
- **Accuracy:** 90.76%
- **Precision (Phishing):** 93%
- **Recall (Phishing):** 87%
- **5-fold CV:** 0.912 ± 0.015

---

## 📁 Project Structure

```
phishing_detector/
├── backend/
│   ├── main.py               # FastAPI app + all routes
│   ├── config.py             # Settings, check_keys()
│   ├── model/
│   │   ├── model.pkl         # Trained model (auto-generated)
│   │   ├── feature_names.pkl # Feature order (auto-generated)
│   │   └── train.py          # Training pipeline
│   ├── utils/
│   │   ├── feature_extractor.py
│   │   ├── url_validator.py
│   │   └── logger.py
│   └── tests/
│       ├── test_api.py
│       └── test_model.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   ├── components/
│   │   │   ├── InputForm.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── Loader.jsx
│   │   └── services/api.js
│   ├── package.json
│   └── vite.config.js
├── chrome_extension/
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── requirements.txt
├── .env.example
└── README.md
```
