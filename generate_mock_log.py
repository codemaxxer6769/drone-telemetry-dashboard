import pandas as pd
import numpy as np

# Generate 300 seconds (5 minutes) of flight data
time_steps = np.arange(0, 300, 1)

# Base GPS origin (e.g., Regina/Moose Jaw open flight field)
base_lat = 50.4501
base_lon = -104.6178

# Simulated helical/circular flight trajectory
latitudes = base_lat + (np.sin(time_steps * 0.02) * 0.002) + (time_steps * 0.000005)
longitudes = base_lon + (np.cos(time_steps * 0.02) * 0.002) + (time_steps * 0.000005)

# --- ALTITUDE CURVE UPDATE ---
# Uses a smooth sine arc across the 300s duration so the drone takes off from ~10m,
# reaches a peak altitude around ~85m during cruise, and descends back down for landing.
altitudes = 10 + 75 * np.sin(np.pi * (time_steps / 300))

# Speed & Physics calculations
# Ground speed (m/s) with dynamic variations
speed_ms = np.abs(np.gradient(altitudes)) * 2 + 8.0 + np.random.normal(0, 0.5, len(time_steps))

# Aerodynamic Drag: F_drag = 0.5 * rho * v^2 * Cd * A
air_density = 1.225  # kg/m^3
cd_a = 0.05          # Drag coefficient * frontal area
drag_force_n = 0.5 * air_density * (speed_ms ** 2) * cd_a

# Thrust Force (N) required to maintain flight and overcome drag
thrust_force_n = drag_force_n + 12.0 + np.random.normal(0, 0.3, len(time_steps))

# Power & Thermal metrics
battery_pct = np.maximum(0, 100 - (time_steps * 0.28))
motor_temp_c = 25.0 + (time_steps * 0.18) + np.random.normal(0, 0.4, len(time_steps))

# Assemble DataFrame
mock_df = pd.DataFrame({
    'timestamp_sec': time_steps,
    'latitude': latitudes,
    'longitude': longitudes,
    'altitude': np.round(altitudes, 2),
    'speed_ms': np.round(speed_ms, 2),
    'drag_force_n': np.round(drag_force_n, 2),
    'thrust_force_n': np.round(thrust_force_n, 2),
    'battery_pct': np.round(battery_pct, 1),
    'motor_temp_c': np.round(motor_temp_c, 1)
})

# Save to CSV
mock_df.to_csv('mock_flight_log.csv', index=False)
print("Updated 'mock_flight_log.csv' successfully with complete landing profile and physics metrics!")