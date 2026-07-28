## 🚀 Portfolio Project Case Study

### **Project Title: UAV Telemetry Analytics Dashboard with AI Diagnostics**

#### **Project Overview**

Developed a responsive, web-based ground control analytics platform designed to ingest, process, and evaluate unmanned aerial vehicle (UAV) flight log data. The application converts raw CSV data streams into interactive time-series visualizations and leverages a localized Large Language Model (LLM) engine to perform automated hardware safety audits.

#### **Core Accomplishments**

* **Dynamic Ingestion Pipeline:** Built a robust file-uploader workflow using **Streamlit** and **Pandas** that seamlessly parses multi-variable telemetry data on-the-fly.
* **Interactive Visualization:** Engineered real-time data visualizations mapping critical flight dynamics including altitude, battery discharge curves, and independent multi-motor thermal profiles.
* **Resilient AI Diagnostic Engine:** Integrated **Ollama (Mistral 7B)** via a streaming HTTP REST API to automatically analyze flight extremes. Designed an **intelligent fallback logic loop** that parses real-time metrics dynamically into structured markdown reports if local infrastructure timeouts occur, ensuring a $100\%$ UI uptime and zero layout breakage.
* **Automated Safety Auditing:** Implemented rule-based thresholds that instantly highlight critical drone operational risks, such as high thermal loads ($>80^\circ\text{C}$ on Motor 2) and critical battery thresholds ($<11.0\text{V}$), matching actual pilot flight scenarios.

#### **Technical Stack**

* **Frontend/Framework:** Streamlit (Python)
* **Data Processing:** Pandas, NumPy
* **AI/LLM Integration:** Ollama, Mistral 7B, Requests (HTTP Streaming API)
* **Data Format:** CSV Telemetry Data
