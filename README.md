# 🏏 IPL Analytics & AI Query System

A full-stack interactive Indian Premier League (IPL) data analytics web application powered by **Python (Flask)**, **Pandas**, **Google Gemini AI (genai SDK)**, and a responsive **HTML5/JS Dashboard**.

---

## ✨ Key Features

- **🤖 AI-Powered Natural Language Query Router**: Ask questions in plain English (e.g., *"What is Virat Kohli's strike rate in successful chases?"*, *"Top 3 teams by win percentage"*, *"Jasprit Bumrah economy rate in death overs (16-20)"*).
- **📊 40+ Analytics Functions**: Comprehensive team, player, stadium/venue, leaderboards, head-to-head, boundary statistics, and match record metrics.
- **⚡ Dual Routing Engine**: Dynamic Gemini AI JSON tool calling with robust rule-based fallback routing for zero downtime and instant answers.
- **🎯 Team & Player Name Resolution**: Built-in support for team aliases (`CSK`, `MI`, `RCB`, `Delhi Daredevils` ↔ `Delhi Capitals`, `Punjab Kings` ↔ `Kings XI Punjab`) and player misspellings.
- **📈 Rich Visual Dashboards**: Interactive Plotly.js charts, stat cards, metric grids, and data tables.
- WEB PAGE LINK -[Live Demo](https://ipl-analytics-abhi.vercel.app)  

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask, Pandas, NumPy, `google-genai` SDK, `python-dotenv`
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3, Plotly.js
- **Data Source**: Ball-by-ball IPL dataset (`matches.csv` & `deliveries.csv`)

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/abhishekadbhute-create/IPL-Analytics.git
cd IPL-Analytics/IPL_ANALYTICS
```

### 2. Set Up Python Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend/` directory based on `.env.example`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run Backend & Frontend Servers
**Terminal 1 (Backend - Port 5000):**
```bash
python app.py
```

**Terminal 2 (Frontend - Port 8000):**
```bash
cd ../frontend
python -m http.server 8000
```

Open `http://localhost:8000` in your browser!

---

## 🧪 QA Validation Suite

Run the automated QA test suite verifying all 40 core analytics questions against raw dataset ground truth:

```bash
cd backend
python run_full_qa_21_40_suite.py
```

---

## 📝 License

This project is open-source under the MIT License.
