# 🚁 UAV Telemetry Analytics Dashboard with Multi-Tier AI Diagnostics

A responsive, web-based ground control analytics platform designed to ingest, process, and evaluate Unmanned Aerial Vehicle (UAV) flight log data in real time. The application converts raw CSV telemetry streams into interactive spatial/time-series visualizations and leverages a **hybrid Large Language Model (LLM) engine** to perform automated hardware safety audits.

---

## ✨ Key Features & Architecture

* **Dynamic Telemetry Ingestion Pipeline:** Built a robust file-uploader workflow using **Streamlit** and **Pandas** to parse multi-variable UAV telemetry streams (altitude, ground speed, battery voltage, aerodynamic drag, and multi-motor thermal outputs) on-the-fly.
* **3D Spatial Path & Time-Series Visualizations:** Engineered interactive 3D trajectory tracking using **Pydeck** to render exact flight pathways alongside dynamic line charts for altitude profiles and thermal curves.
* **Resilient Multi-Tier AI Diagnostic Engine:** Integrated an intelligent LLM streaming pipeline with automatic failover to guarantee zero UI downtime:
1. **Primary (Cloud):** High-speed, low-latency streaming via **Groq Cloud API** (`Llama 3.1 8B` / `Mixtral 8x7b`).
2. **Secondary (Local Edge):** Local REST API connection to **Ollama** (`Mistral 7B`).
3. **Fallback Engine:** Custom rule-based extraction engine that parses real-time telemetry metrics dynamically into structured diagnostic markdown reports if all AI services are unreachable.


* **Automated Safety Auditing:** Contextualized diagnostic prompts evaluate critical operational risks, such as elevated thermal loads ($\ge 80^\circ\text{C}$ on motors), high drag-to-thrust ratios, and critical battery discharge levels.

---

## 🛠️ Technical Stack

* **Frontend & Framework:** Python, Streamlit
* **3D & Data Visualization:** Pydeck, Streamlit Charts
* **Data Processing:** Pandas, NumPy
* **AI & LLM Infrastructure:** Groq Cloud API, Ollama (Mistral 7B), Requests (HTTP Streaming REST API)
* **Deployment & DevOps:** Git, GitHub, Streamlit Community Cloud (Secrets Management)

---

## 🚀 Getting Started Locally

### Prerequisites

* Python 3.9+ installed
* *(Optional)* [Ollama](https://ollama.ai/) installed locally for offline AI execution.

### Installation & Run

1. **Clone the repository:**
```bash
git clone https://github.com/codemaxxer6769/drone-telemetry-dashboard.git
cd drone-telemetry-dashboard

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configure Environment Secrets (Optional for Groq API):**
Create a `.streamlit/secrets.toml` file in the root directory:
```toml
GROQ_API_KEY = "your_groq_api_key_here"

```


4. **Launch the Streamlit app:**
```bash
streamlit run app.py

```

---

## 📸 Usage & Workflow

1. Upload a drone telemetry `.csv` file (or generate mock telemetry using `generate_mock_log.py`).
2. Explore interactive telemetry metrics, altitude profile charts, and 3D flight trajectory visualizations.
3. Click **Generate AI Flight Analysis Report** to stream real-time, LLM-generated diagnostic reports detailing aerodynamic efficiency, thermal safety, and actionable maintenance steps.
