import pandas as pd
import numpy as np

def generate_mock_data(filename="data/mock_flight_log.csv", duration_seconds=60):
    """
    Generates mock flight log data and saves it to a CSV file.

    Parameters:
    filename (str): The name of the file to save the mock data.
    duration_seconds (int): The duration of the flight log in seconds.
    """
    timestamps = np.arange(0, duration_seconds, 0.5)  # Generate timestamps every 0.5 seconds
    n_points = len(timestamps)

    # Simulate a steady climb, a hover, and a descent
    altitude = np.sin(timestamps / 10) * 15 + 15

    # Simulate battery drain over time
    battery_voltage = 12.6 - (timestamps * 0.03) - np.random.normal(0, 0.05, n_points)

    # Motor temperatures (Motor 3 will slowly overheat to simulate an anomaly)
    motor_1_temp = 45 + (timestamps * 0.1) + np.random.normal(0, 0.5, n_points)
    motor_2_temp = 45 + (timestamps * 0.7) + np.random.normal(0, 0.5, n_points) # Overheats!

    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Altitude_m": altitude,
        "Battery_V": battery_voltage,
        "Motor_1_Temp_C": motor_1_temp,
        "Motor_2_Temp_C": motor_2_temp
    })

    df.to_csv(filename, index=False)
    print(f"Successfully generated mock flight log data and saved to: {filename}")

if __name__ == "__main__":
    generate_mock_data()