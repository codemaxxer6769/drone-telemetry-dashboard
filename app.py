import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import json

# Set up the Streamlit app configuration
st.set_page_config(layout="wide", page_title="Drone Telemetry Dashboard", page_icon="🚁")
st.title("🚁 Interactive Drone Telemetry & AI Flight Analyst")

# 1. Initialize session state memory for the report
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

# 2. Sidebar - File Upload / Data Source
st.sidebar.header("Data Control Panel")

def clear_report_state():
    st.session_state.ai_report = None

uploaded_file = st.sidebar.file_uploader(
    "Upload a Flight Log CSV", 
    type=["csv"], 
    on_change=clear_report_state
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")
else: 
    try: 
        # Tries new mock log, falls back to legacy path if not moved yet
        df = pd.read_csv("mock_flight_log.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("data/mock_flight_log.csv")
        except FileNotFoundError:
            st.sidebar.warning("No flight log uploaded and no mock data found.")
            st.stop()

# Helper function for Pydeck 3D Map
def render_3d_flight_map(data_df):
    st.subheader("🌐 3D Spatial Trajectory & Elevation")
    
    # Check for flexible column names
    lat_col = 'latitude' if 'latitude' in data_df.columns else ('Latitude' if 'Latitude' in data_df.columns else None)
    lon_col = 'longitude' if 'longitude' in data_df.columns else ('Longitude' if 'Longitude' in data_df.columns else None)
    alt_col = 'altitude' if 'altitude' in data_df.columns else ('altitude_m' if 'altitude_m' in data_df.columns else ('Altitude_m' if 'Altitude_m' in data_df.columns else None))

    if not (lat_col and lon_col and alt_col):
        st.error("Telemetry CSV is missing spatial coordinates (Latitude, Longitude, Altitude) required for 3D mapping.")
        return
    # Create a rounded altitude column specifically for clean tooltips!
    data_df['alt_display'] = data_df[alt_col].round(2)

    # Flight path layer (Blue Line)
    flight_path = data_df[[lon_col, lat_col, alt_col]].values.tolist()
    
    path_layer = pdk.Layer(
        "PathLayer",
        data=[{"path": flight_path, "color": [0, 200, 255]}],
        get_path="path",
        get_color="color",
        width_min_pixels=4,
        get_width=3,
    )

    # Takeoff & Landing markers (Green & Red Dots)
    start_pt = data_df.iloc[0]
    end_pt = data_df.iloc[-1]
    
    markers_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[
            {"position": [start_pt[lon_col], start_pt[lat_col], start_pt[alt_col]], "color": [0, 255, 0], "point_type": "Takeoff"},
            {"position": [end_pt[lon_col], end_pt[lat_col], end_pt[alt_col]], "color": [255, 0, 0], "point_type": "Landing"}
        ],
        get_position="position",
        get_color="color",
        get_radius=8,
        radius_min_pixels=6,
        pickable=True
    )

    # 3D Columns under path (Visual Altitude Extrusion)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=data_df,
        get_position=[lon_col, lat_col],
        get_elevation=alt_col,
        elevation_scale=1,
        radius=2,
        get_fill_color="[255, 100, 0, 160]",
        pickable=True,
        auto_highlight=True,
    )

    initial_view_state = pdk.ViewState(
        latitude=data_df[lat_col].mean(),
        longitude=data_df[lon_col].mean(),
        zoom=15,
        pitch=60,
        bearing=-30
    )

    # Render Pydeck map with open-source CartoDB dark basemap tiles
    st.pydeck_chart(pdk.Deck(
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        initial_view_state=initial_view_state,
        layers=[path_layer, column_layer, markers_layer],
        tooltip={"text": "Altitude: {alt_display} m\nSpeed: {speed_ms} m/s"}
    ))

# 3. Main Dashboard KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)

# Dynamic mapping for column differences between old/new CSVs
alt_val = df['altitude'].max() if 'altitude' in df.columns else df.get('Altitude_m', pd.Series([0])).max()
speed_val = df['speed_ms'].max() if 'speed_ms' in df.columns else 0.0
drag_val = df['drag_force_n'].max() if 'drag_force_n' in df.columns else 0.0
battery_val = df['battery_pct'].iloc[-1] if 'battery_pct' in df.columns else df.get('Battery_V', pd.Series([0])).min()
battery_unit = "%" if 'battery_pct' in df.columns else "V"

with col1:
    st.metric("Max Altitude", f"{alt_val:.2f} m")
with col2:
    st.metric("Max Speed", f"{speed_val:.2f} m/s" if speed_val else "N/A")
with col3:
    st.metric("Peak Drag Force", f"{drag_val:.2f} N" if drag_val else "N/A")
with col4:
    st.metric("Battery Status", f"{battery_val:.1f} {battery_unit}")

st.markdown("---")

# 4. Categorized Tabs Layout
tab1, tab2, tab3 = st.tabs([
    "🌐 3D Spatial Trajectory", 
    "🚀 Aerodynamics & Physics", 
    "⚡ Hardware & Power Trends"
])

with tab1:
    render_3d_flight_map(df)

with tab2:
    st.subheader("Aerodynamic Forces & Velocity")
    time_col = 'timestamp_sec' if 'timestamp_sec' in df.columns else 'Timestamp'
    y_cols = [c for c in ['drag_force_n', 'thrust_force_n', 'speed_ms'] if c in df.columns]
    
    if y_cols:
        fig_physics = px.line(df, x=time_col, y=y_cols, title="Thrust vs. Aerodynamic Drag vs. Speed")
        st.plotly_chart(fig_physics, use_container_width=True)
    else:
        st.info("Additional aerodynamics columns (drag, thrust, speed) not found in current CSV.")

    st.subheader("📈 Altitude Profile Over Time")

    # Check for all variations of the altitude column name
    if 'altitude' in df.columns:
        st.line_chart(df['altitude'])
    elif 'altitude_m' in df.columns:
        st.line_chart(df['altitude_m'])
    elif 'Altitude_m' in df.columns:
        st.line_chart(df['Altitude_m'])
    else:
        st.info("Altitude data column not detected in current CSV.")

with tab3:
    st.subheader("Power & Thermal Diagnostics")
    time_col = 'timestamp_sec' if 'timestamp_sec' in df.columns else 'Timestamp'
    thermal_cols = [c for c in ['battery_pct', 'motor_temp_c', 'Motor_1_Temp_C', 'Motor_2_Temp_C', 'Battery_V'] if c in df.columns]
    
    fig_power = px.line(df, x=time_col, y=thermal_cols, title="Thermal & Battery Health Trends")
    st.plotly_chart(fig_power, use_container_width=True)

# ----------------------------------------------------
# 5. AI Diagnostics Panel (Groq Cloud API + Ollama Local + Fallback)
# ----------------------------------------------------
st.subheader("🤖 AI Flight Diagnostics")

max_alt_val = float(alt_val)
max_speed_val = float(speed_val)
max_drag_val = float(drag_val)
max_thrust_val = float(df['thrust_force_n'].max()) if 'thrust_force_n' in df.columns else 0.0
motor_temp_val = float(df['motor_temp_c'].max()) if 'motor_temp_c' in df.columns else float(df.get('Motor_2_Temp_C', pd.Series([0])).max())

if st.button("Generate AI Flight Analysis Report"):
    report_placeholder = st.info("🔄 Initiating AI analysis engine...")
    live_text = ""

    prompt = f"""
    You are an expert drone telemetry and aerodynamics analysis AI. Analyze these flight statistics:
    - Maximum Altitude: {max_alt_val:.2f} meters
    - Maximum Ground Speed: {max_speed_val:.2f} m/s
    - Peak Aerodynamic Drag Force: {max_drag_val:.2f} N
    - Peak Motor Thrust Force: {max_thrust_val:.2f} N
    - Maximum Motor Temperature: {motor_temp_val:.2f}°C
    - Final Battery Status: {battery_val:.1f}{battery_unit}

    Provide a concise flight diagnostic report (under 150 words).
    1. Evaluate aerodynamic efficiency (drag vs thrust ratio).
    2. Identify if thermal levels or battery discharge pose hardware safety risks.
    3. Give clear actionable maintenance recommendations.
    """

    # --- OPTION A: Try Groq Cloud API ---
    groq_api_key = None
    try:
        if "GROQ_API_KEY" in st.secrets:
            groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    if groq_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }

            # 1. Dynamically fetch currently available models from Groq
            models_res = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
            active_models = []
            if models_res.status_code == 200:
                active_models = [m["id"] for m in models_res.json().get("data", [])]

            # 2. Pick the first available active model from preferred candidates
            preferred_candidates = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "qwen/qwen3.6-27b",
                "openai/gpt-oss-120b"
            ]
            
            selected_model = None
            for candidate in preferred_candidates:
                if candidate in active_models:
                    selected_model = candidate
                    break
            
            # If none of preferred are found, grab the first available text model
            if not selected_model and active_models:
                selected_model = active_models[0]

            if selected_model:
                st.caption(f"⚡ Running live telemetry analysis via `{selected_model}`")
                payload = {
                    "model": selected_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=10
                )

                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith("data: ") and line_str != "data: [DONE]":
                                chunk = json.loads(line_str[6:])
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                live_text += delta
                                report_placeholder.info(live_text + " ▌")

                    if live_text.strip():
                        report_placeholder.info(live_text)
                        st.stop()

        except Exception:
            pass

    # --- OPTION C: Automated Fallback Engine (Safety net) ---
    fallback_report = f"""**Diagnostic Report (Automated Fallback Engine):**

The drone completed the flight with a peak altitude of **{max_alt_val:.2f} m** and max ground speed of **{max_speed_val:.2f} m/s**.

**Aerodynamic & Thermal Performance:**
- Aerodynamic drag hit a maximum of **{max_drag_val:.2f} N**, requiring motor thrust of up to **{max_thrust_val:.2f} N**.
- Motor temperature reached **{motor_temp_val:.2f}°C**. {"⚠️ Temperature is elevated, monitor cooling." if motor_temp_val > 75 else "Thermal levels remained nominal."}
- Ending battery state: **{battery_val:.1f}{battery_unit}**.

**Recommendations:**
1. Check motor mounts if thrust-to-drag ratio drops unexpectedly.
2. Ensure motor heat dissipation channels are clear prior to launch."""

    report_placeholder.info(fallback_report)