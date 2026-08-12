# Aerospace Payload Pressure Safety & Control System
# Hardware-in-the-loop (HIL) telemetry simulation

import csv
import random
import time

TOTAL_HARDWARE_MASS_LB = 10.43
GAS_NAME = "High-Pressure Nitrogen (N2)"
CYLINDER_VOLUME_L = 5.0
GAS_CONSTANT_R = 0.0821  # L·atm/(mol·K)
MAX_SAFE_PRESSURE = 145.0  # atm
TEMPERATURE_K = 293.15  # 20 °C
GAS_MOLES = 30.0
MOLECULAR_WEIGHT_N2_G = 28.01

CSV_FILE = "aerospace_payload_telemetry.csv"

servo_angle = 0
previous_pressure = None
previous_time = None
gas_moles = GAS_MOLES
temperature_k = TEMPERATURE_K

# Telemetry fields:
# Timestamp, temperature, pressure, dP/dt, servo status, total mass
with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Timestamp (s)",
        "Port 3: Temp (K)",
        "Port 2: Pressure (atm)",
        "Pressure Rate (atm/s)",
        "Port 1: Servo Status",
        "Total System Mass (lbs)"
    ])

start_time = time.time()

while True:
    current_time = time.time() - start_time

    # Simulated environmental heating.
    temperature_k += random.uniform(0.6, 2.2)

    # Ideal-gas pressure model: P = nRT/V
    pressure_atm = (gas_moles * GAS_CONSTANT_R * temperature_k) / CYLINDER_VOLUME_L

    if previous_pressure is None or previous_time is None:
        dp_dt = 0.0
    else:
        dt = current_time - previous_time
        dp_dt = (pressure_atm - previous_pressure) / dt if dt > 0 else 0.0

    # N2 mass: mol × g/mol, converted to pounds.
    gas_mass_lb = (gas_moles * MOLECULAR_WEIGHT_N2_G) / 453.59237
    total_mass_lb = TOTAL_HARDWARE_MASS_LB + gas_mass_lb

    if pressure_atm > MAX_SAFE_PRESSURE:
        servo_angle = 90
        print("⚠ CRITICAL OVERPRESSURE DETECTED!")
        print(f" -> Pressure: {pressure_atm:.1f} atm")
        print(f" -> dP/dt: {dp_dt:.2f} atm/s")
        print(" -> Port 1 Servo: 90° (OPEN - VENTING)")

        # Simulated 6% vent event.
        gas_moles *= 0.94
        temperature_k -= 6.0
    else:
        servo_angle = 0
        print(
            f"Pressure: {pressure_atm:.1f} atm | "
            f"dP/dt: {dp_dt:.2f} atm/s | "
            f"Temp: {temperature_k:.1f} K | "
            f"Mass: {total_mass_lb:.3f} lbs | Status: NOMINAL"
        )

    servo_status = (
        "90° (OPEN - VENTING)" if servo_angle == 90
        else "0° (CLOSED)"
    )

    # Recalculate total mass after a safety vent so the logged state
    # reflects the reduced gas inventory.
    gas_mass_lb = (gas_moles * MOLECULAR_WEIGHT_N2_G) / 453.59237
    total_mass_lb = TOTAL_HARDWARE_MASS_LB + gas_mass_lb

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            round(current_time, 1),
            round(temperature_k, 2),
            round(pressure_atm, 2),
            round(dp_dt, 2),
            servo_status,
            round(total_mass_lb, 3)
        ])

    previous_pressure = pressure_atm
    previous_time = current_time
    time.sleep(1)
