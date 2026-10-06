# =============================================================================
# dashboard.py
# Polestar EV Digital Twin Dashboard
# Author: Kashif Jawad Mazhar (Visualization Task)
# Run: python -m streamlit run dashboard.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_generator import generate_dummy_data

# Page setup
st.set_page_config(page_title="EV Dashboard", layout="wide")

# Title
st.title("Electric Vehicle Digital Twin Dashboard")
st.write("Powertrain Visualization - Kashif Jawad Mazhar")

# Data load karo
df = generate_dummy_data(duration=1800, dt=1)

# -------------------------------------------------------------------------
# Sidebar - Options
# -------------------------------------------------------------------------
st.sidebar.title("Options")
st.sidebar.write("Select graphs to display:")

show_speed = st.sidebar.checkbox("Speed", value=True)
show_power = st.sidebar.checkbox("Battery Power", value=True)
show_soc = st.sidebar.checkbox("Battery SOC", value=True)
show_eff = st.sidebar.checkbox("Efficiency", value=True)

st.sidebar.write("---")
st.sidebar.write("Vehicle: Polestar 2")
st.sidebar.write("Battery: 94 kWh, 407 V")
st.sidebar.write("Motor: 200 kW, 343 Nm")

# -------------------------------------------------------------------------
# Summary KPIs
# -------------------------------------------------------------------------
st.header("Summary")

col1, col2, col3, col4 = st.columns(4)

peak = df['battery_power_kW'].max()
avg = df['battery_power_kW'].mean()
energy = df['energy_consumed_kWh'].max()
eff = df[df['efficiency_percent'] > 0]['efficiency_percent'].mean()

col1.metric("Peak Power", round(peak, 1), "kW")
col2.metric("Average Power", round(avg, 1), "kW")
col3.metric("Total Energy", round(energy, 2), "kWh")
col4.metric("Avg Efficiency", round(eff, 1), "%")

st.write("")

# -------------------------------------------------------------------------
# Speed graph
# -------------------------------------------------------------------------
if show_speed:
    st.header("Vehicle Speed over Time")
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(df['time'], df['speed_kmh'], color='blue', linewidth=1)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Speed (km/h)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# -------------------------------------------------------------------------
# Battery Power graph
# -------------------------------------------------------------------------
if show_power:
    st.header("Battery Power over Time")
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(df['time'], df['battery_power_kW'], color='red', linewidth=1)
    ax.axhline(y=0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Power (kW)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# -------------------------------------------------------------------------
# SOC graph
# -------------------------------------------------------------------------
if show_soc:
    st.header("Battery State of Charge")
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(df['time'], df['soc_percent'], color='orange', linewidth=1.5)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("SOC (%)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# -------------------------------------------------------------------------
# Efficiency graph
# -------------------------------------------------------------------------
if show_eff:
    st.header("Powertrain Efficiency")
    fig, ax = plt.subplots(figsize=(12, 3))
    eff_data = df[df['efficiency_percent'] > 0]
    ax.plot(eff_data['time'], eff_data['efficiency_percent'],
            color='green', linewidth=1)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Efficiency (%)")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

st.write("")

# -------------------------------------------------------------------------
# Energy Flow - simple text
# -------------------------------------------------------------------------
st.header("Energy Flow")
st.write("Battery (94 kWh, 407 V) -> Inverter -> Motor (200 kW) -> Gear -> Wheels")
st.write("Regenerative braking recovers energy back to battery.")
st.write("Overall efficiency estimate: 0.96 x 0.96 x 0.90 = 82.9%")

st.write("")

# -------------------------------------------------------------------------
# Data Table
# -------------------------------------------------------------------------
st.header("Data Table")
if st.checkbox("Show first 20 rows"):
    st.write(df.head(20))

st.write("")
st.write("Note: This dashboard uses dummy WLTP-based data. Real simulation data will replace it later.")