# =============================================================================
# data_generator.py
# Ye file EV ka dummy WLTP-based data banati hai (jab tak real data na aaye)
# Physics formulas use kiye hain taake realistic lage
# Author: Kashif Jawad Mazhar
# =============================================================================

import numpy as np
import pandas as pd


def generate_dummy_data(duration=1800, dt=1):
    """
    EV driving data banata hai.
    duration = total seconds (1800 = 30 min)
    dt = sampling interval (1 = har 1 second)
    Returns: DataFrame with all signals
    """

    # Time array banayo: 0, 1, 2, ... 1799
    t = np.arange(0, duration, dt)
    n = len(t)

    # -------------------------------------------------------------------------
    # Speed profile - multiple sine waves ka combination
    # (real driving behaviour ke kareeb, koi jump nahi)
    # -------------------------------------------------------------------------
    speed = (
        50
        + 25 * np.sin(2 * np.pi * t / 250)
        + 15 * np.sin(2 * np.pi * t / 400)
        + 10 * np.sin(2 * np.pi * t / 180)
    )
    speed = np.clip(speed, 0, 130)  # 0-130 km/h ke beech

    # -------------------------------------------------------------------------
    # Vehicle parameters (Polestar 2 ki values)
    # -------------------------------------------------------------------------
    mass = 1600              # kg
    Cd = 0.29                # drag coefficient
    A = 2.3                  # frontal area (m2)
    rho = 1.225              # air density (kg/m3)
    Crr = 0.010              # rolling resistance
    g = 9.81                 # gravity (m/s2)
    wheel_radius = 0.35      # wheel radius (m)
    eta_motor = 0.96         # motor efficiency
    eta_inverter = 0.96      # inverter efficiency
    eta_drivetrain = 0.90    # drivetrain efficiency
    battery_capacity_kwh = 94
    battery_voltage_nom = 407

    # -------------------------------------------------------------------------
    # Speed ko m/s mein convert karo (physics ke liye zaroori)
    # -------------------------------------------------------------------------
    v = speed / 3.6
    accel = np.gradient(v, dt)

    # -------------------------------------------------------------------------
    # Forces calculate karo (Newton's laws)
    # -------------------------------------------------------------------------
    F_roll = Crr * mass * g                      # rolling resistance
    F_aero = 0.5 * rho * Cd * A * v ** 2         # aerodynamic drag
    F_accel = mass * accel                       # acceleration force
    F_total = F_roll + F_aero + F_accel

    # -------------------------------------------------------------------------
    # Mechanical power at wheels: P = F * v
    # Regenerative braking mein 60% energy recover hoti hai
    # -------------------------------------------------------------------------
    P_wheel = F_total * v
    P_wheel = np.where(P_wheel < 0, P_wheel * 0.6, P_wheel)

    # -------------------------------------------------------------------------
    # Battery power calculate karo
    # Driving: P_battery = P_wheel / total_efficiency (losses ke baad)
    # Regen:   P_battery = P_wheel * total_efficiency (losses ke baad)
    # -------------------------------------------------------------------------
    total_eff = eta_drivetrain * eta_motor * eta_inverter

    P_battery = np.where(
        P_wheel >= 0,
        P_wheel / total_eff,      # driving
        P_wheel * total_eff       # regen
    )

    # -------------------------------------------------------------------------
    # Battery voltage aur current
    # Ohm's law: I = P / V
    # -------------------------------------------------------------------------
    battery_voltage = battery_voltage_nom + 5 * np.sin(2 * np.pi * t / 500)
    battery_current = P_battery / battery_voltage

    # -------------------------------------------------------------------------
    # Motor speed (rpm) - gear ratio = 1
    # -------------------------------------------------------------------------
    motor_rpm = (v / wheel_radius) * 60 / (2 * np.pi)

    # Motor torque (Nm): T = P / omega
    omega = motor_rpm * 2 * np.pi / 60
    motor_torque = np.where(omega > 1, P_wheel / np.maximum(omega, 1), 0)
    motor_torque = np.clip(motor_torque, -343, 343)

    # Motor power (kW), limit ke andar
    motor_power = np.clip(P_wheel / 1000, -200, 200)

    # -------------------------------------------------------------------------
    # Battery SOC (State of Charge)
    # Energy = P * t (integrate karo)
    # SOC = 100% - (used energy / capacity) * 100
    # -------------------------------------------------------------------------
    energy_wh = np.cumsum(P_battery) * dt / 3600
    soc = 100 - (energy_wh / (battery_capacity_kwh * 1000)) * 100
    soc = np.clip(soc, 0, 100)

    # -------------------------------------------------------------------------
    # Efficiency calculation
    # -------------------------------------------------------------------------
    # Driving: eta = P_wheel / P_battery (output / input)
    # Regen:   eta = P_battery / P_wheel (output / input - roles ulte)
    #
    # Note: Regen mein motor generator ban jata hai, isliye formula flip hoti hai

    eff_driving = np.where(
        P_battery > 100,
        (P_wheel / P_battery) * 100,
        0
    )

    eff_regen = np.where(
        P_battery < -100,
        (P_battery / P_wheel) * 100,
        0
    )

    efficiency = eff_driving + eff_regen
    efficiency = np.clip(efficiency, 0, 100)

    # -------------------------------------------------------------------------
    # Sab kuch DataFrame mein daalo (Excel jaisi table)
    # -------------------------------------------------------------------------
    df = pd.DataFrame({
        'time': t,
        'speed_kmh': speed,
        'battery_voltage_V': battery_voltage,
        'battery_current_A': battery_current,
        'battery_power_kW': P_battery / 1000,
        'soc_percent': soc,
        'motor_rpm': motor_rpm,
        'motor_torque_Nm': motor_torque,
        'motor_power_kW': motor_power,
        'efficiency_percent': efficiency,
        'energy_consumed_kWh': np.maximum(energy_wh, 0) / 1000,
    })

    return df


# Ye part sirf tab chalta hai jab file directly run karo
if __name__ == "__main__":
    df = generate_dummy_data()
    df.to_csv("dummy_data.csv", index=False)
    print(f"Data generated: {len(df)} rows")
    print(df.head())