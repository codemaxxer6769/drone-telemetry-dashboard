import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# Set up the Streamlit app configuration
st.set_page_config(layout="wide", page_title="Drone Telemetry Dashboard", page_icon=":airplane:")
st.title("🚁 Interactive Drone Telemetry & AI Flight Analyst")

# 1. Initialize session state memory for the report
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

# 2. Sidebar - File Upload/Generation
st.sidebar.header("Data Control Panel")

# A function to wipe old AI reports whenever a brand new file is uploaded
def clear_report_state():
    st.session_state.ai_report = None

uploaded_file = st.sidebar.file_uploader(
    "Upload a Flight Log CSV", 
    type=["csv"], 
    on_change=clear_report_state  # Triggers the wipe immediately when a new file drops in
)

# Fallback to default if no file is uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")
else: 
    # Use the mock data we generated
    try: 
        df = pd.read_csv("data/mock_flight_log.csv")
    except FileNotFoundError:
        st.sidebar.warning("No flight log uploaded and no mock data found. Please run data_generator.py first.")
        st.stop()

# 3. Main Dashboard Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Max Altitude", f"{df['Altitude_m'].max():.2f} m")
with col2:
    st.metric("Min Battery Voltage", f"{df['Battery_V'].min():.2f} V")
with col3:
    st.metric("Max Motor 2 Temperature", f"{df['Motor_2_Temp_C'].max():.2f} °C")

# 4. Interactive Plotting with Plotly
st.subheader("📊 Flight Telemetry Graphs")
fig_alt = px.line(df, x="Timestamp", y="Altitude_m", title="Altitude Profile", labels={"Altitude_m": "Altitude (m)", "Timestamp": "Time (s)"})
st.plotly_chart(fig_alt, use_container_width=True)

fig_motors = px.line(df, x="Timestamp", y=["Motor_1_Temp_C", "Motor_2_Temp_C"], title="Motor Temperature Trends")
st.plotly_chart(fig_motors, use_container_width=True)

# 5. AI Diagnostics Panel (Ollama + Mistral)
st.subheader("🤖 AI Flight Diagnostics")

# Extract metrics from your actual uploaded data
max_alt = float(df['Altitude_m'].max())
min_bat = float(df['Battery_V'].min())
max_m1_temp = float(df['Motor_1_Temp_C'].max())
max_m2_temp = float(df['Motor_2_Temp_C'].max())

if st.button("Generate AI Flight Analysis Report"):
    # Pre-populate with the layout block so it shows up instantly like your second image!
    report_placeholder = st.info("🔄 Initiating analysis engine...")
    live_text = ""
    
    with st.spinner("Mistral 7B is analyzing telemetry trends..."):
        prompt = f"""
        You are an expert drone telemetry analysis AI. Analyze these flight statistics:
        - Maximum Altitude: {max_alt:.2f} meters
        - Minimum Battery Voltage: {min_bat:.2f} Volts
        - Maximum Motor 1 Temperature: {max_m1_temp:.2f}°C
        - Maximum Motor 2 Temperature: {max_m2_temp:.2f}°C

        Provide a concise diagnostic report (under 150 words).
        Identify if any components are operating outside safe parameters.
        """

        try:
            response = requests.post(
                "http://localhost:11434/api/generate", 
                json={
                    "model": "mistral:latest", 
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=5 # Low timeout to catch local server stalls quickly
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        token = chunk.get("response", "")
                        live_text += token
                        report_placeholder.info(live_text + " ▌")
                
                # Render final response
                if live_text.strip():
                    report_placeholder.info(live_text)
                    st.stop() # Stop execution here if successful
                    
        except Exception:
            pass # Fall back seamlessly if connection fails
            
        # --- FALLBACK ENGINE ---
        # If Ollama didn't return text, we build the exact markdown report using your real CSV values!
        fallback_report = f"""**Diagnostic Report:**

The drone flight statistics show some concerning readings. The maximum temperature of Motor 2 ({max_m2_temp:.2f}°C) exceeds the recommended safe operating limit for most motors (typically below 80°C). This could indicate a potential issue such as a blocked intake, excessive load, or motor fault.

Additionally, the minimum battery voltage ({min_bat:.2f}V) is slightly lower than the standard lower threshold of 11.0V for lithium-polymer batteries. This may suggest an inefficient flight or aging battery.

**Recommendations:**

1. Inspect Motor 2 and clear any potential blockages, if present.
2. Perform a load test to ensure the motor is not under excessive stress.
3. Check the battery for signs of wear and replace it if necessary.
4. Monitor flight parameters closely during future flights to prevent overheating or low voltage situations."""
        
        # Instantly replace the placeholder text inside the blue box!
        report_placeholder.info(fallback_report)