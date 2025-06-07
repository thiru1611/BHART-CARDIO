import streamlit as st
import numpy as np
import time
import math
import pandas as pd

# Utility function to generate a single ECG point (Y-value) at a given time for a specific type
# This function simulates the different phases of an ECG waveform (P, QRS, T) and adds noise.
# For MI, it introduces simulated ST elevation, deeper Q waves, and inverted T waves.
def generate_ecg_point(time_ms, ecg_type):
    # Simulate a heart rate of 60 bpm (1 beat per second)
    beat_duration = 1000  # milliseconds for one complete ECG cycle
    time_in_beat = time_ms % beat_duration  # Current time within the 1-second beat cycle

    y = 0  # Baseline for the ECG signal

    # Simulate P wave (at the beginning of the beat cycle)
    if 0 <= time_in_beat < 100:
        y += math.sin(time_in_beat / 100 * math.pi) * 10  # A small positive hump
    # Simulate PR segment (flat line after P wave)
    elif 100 <= time_in_beat < 150:
        y += 0
    # Simulate QRS complex (the main sharp spike)
    elif 150 <= time_in_beat < 250:
        if time_in_beat < 170:  # Q wave (downward deflection)
            y += (time_in_beat - 170) / 20 * 30
        elif time_in_beat < 200:  # R wave (large upward deflection)
            y += ((time_in_beat - 170) / 30) * -80
        else:  # S wave (downward deflection after R)
            y += (time_in_beat - 200) / 50 * 50
    # Simulate ST segment (flat line after S wave, before T wave)
    elif 250 <= time_in_beat < 320:
        y += 0
    # Simulate T wave (a broader hump after ST segment)
    elif 320 <= time_in_beat < 450:
        y += math.sin((time_in_beat - 320) / 130 * math.pi) * 20

    # Add random noise to make the signal less perfect
    y += (np.random.rand() - 0.5) * 5

    # Apply Myocardial Infarction (MI) specific changes if `ecg_type` is 'mi'
    if ecg_type == 'mi':
        # Simulate ST elevation: A significant upward shift of the ST segment, characteristic of STEMI
        if 250 <= time_in_beat < 320:
            y -= 30  # Elevate ST segment by a fixed amount
        # Simulate pathological Q wave: A deeper and wider Q wave, often indicating past MI
        if 150 <= time_in_beat < 170:
            y += (time_in_beat - 170) / 20 * 60  # Make Q wave significantly deeper
        # Simulate T wave inversion: The T wave goes below the baseline, common in MI
        if 320 <= time_in_beat < 450:
            y *= -1.5  # Invert and amplify the T wave

    return y

# Function to simulate AI analysis based on the selected ECG type
def perform_ai_analysis(ecg_type):
    new_diagnosis = ''
    new_confidence_score = 0
    new_characteristics = []

    if ecg_type == 'normal':
        new_diagnosis = 'Normal Sinus Rhythm'
        new_confidence_score = np.random.randint(90, 100) # 90-99%
        new_characteristics = [
            'Regular rhythm',
            'Heart rate 60-100 bpm',
            'Normal P waves preceding each QRS complex',
            'Normal PR interval (0.12-0.20s)',
            'Normal QRS duration (<0.12s)',
            'Isoelectric ST segment',
            'Upright T waves',
        ]
    elif ecg_type == 'mi':
        new_diagnosis = 'Myocardial Infarction (Simulated)'
        new_confidence_score = np.random.randint(85, 96) # 85-95%
        new_characteristics = [
            'ST segment elevation or depression (depending on MI type)',
            'Pathological Q waves (wider and deeper than normal)',
            'T-wave inversion or hyperacute T waves',
            'Possible abnormal R-wave progression',
            'May be associated with arrhythmias',
        ]
    return new_diagnosis, new_confidence_score, new_characteristics

# Streamlit App UI
st.set_page_config(layout="centered", page_title="Real-Time AI-Based ECG Analyzer", page_icon="❤️")

st.markdown("""
    <style>
    .reportview-container {
        background: #f0f2f6; /* Light gray background */
    }
    .main .block-container {
        background-color: #ffffff; /* White card background */
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    h1 {
        color: #1a56db; /* Blue for headings */
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    p {
        color: #4a5568; /* Darker gray for text */
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green button */
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    /* Specific styles for MI button */
    .stButton>button[kind="secondary"] {
        background-color: #ef4444; /* Red button */
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #dc2626;
    }
    /* Stop button */
    .stButton>button[kind="tertiary"] {
        background-color: #6b7280; /* Gray button */
    }
    .stButton>button[kind="tertiary"]:hover {
        background-color: #4b5563;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Real-Time AI-Based ECG Analyzer (Simulated)")
st.write("This application simulates a real-time ECG stream and an AI's ability to differentiate between a normal ECG and one indicative of Myocardial Infarction. Select a scenario to start the live stream and see a mock diagnosis.")

# State management for Streamlit
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'ecg_type' not in st.session_state:
    st.session_state.ecg_type = None

# Action Buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Start Normal ECG Stream", disabled=st.session_state.is_streaming):
        st.session_state.is_streaming = True
        st.session_state.ecg_type = 'normal'
        st.experimental_rerun() # Rerun to update the state and start streaming

with col2:
    if st.button("Start MI ECG Stream", type="secondary", disabled=st.session_state.is_streaming):
        st.session_state.is_streaming = True
        st.session_state.ecg_type = 'mi'
        st.experimental_rerun() # Rerun to update the state and start streaming

with col3:
    if st.session_state.is_streaming:
        if st.button("Stop Stream", type="tertiary"):
            st.session_state.is_streaming = False
            st.session_state.ecg_type = None
            st.experimental_rerun() # Rerun to clear state and stop streaming

# Placeholder for the ECG chart
chart_placeholder = st.empty()
analysis_placeholder = st.empty()

# Real-time ECG Stream and Analysis
if st.session_state.is_streaming and st.session_state.ecg_type:
    # Perform AI analysis immediately when stream starts
    diagnosis, confidence_score, characteristics = perform_ai_analysis(st.session_state.ecg_type)

    # Display initial analysis results
    with analysis_placeholder.container():
        st.markdown(f"<h2 style='text-align: center; color: #4a5568;'>AI Analysis Result:</h2>", unsafe_allow_html=True)
        if st.session_state.ecg_type == 'normal':
            st.markdown(f"""
                <div style='background-color: #ecfdf5; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);'>
                    <p style='text-align: left; font-size: 1.125rem; margin-bottom: 0.5rem;'>
                        <span style='font-weight: 500;'>Diagnosis:</span>
                        <span style='font-weight: 700; color: #065f46;'> {diagnosis}</span>
                    </p>
                    <p style='text-align: left; font-size: 1.125rem; margin-bottom: 1rem;'>
                        <span style='font-weight: 500;'>Confidence Score:</span>
                        <span style='font-weight: 700; color: #4a5568;'> {confidence_score}%</span>
                    </p>
                    <h3 style='font-size: 1.25rem; font-weight: 600; color: #4a5568; margin-bottom: 0.75rem;'>Typical ECG Characteristics:</h3>
                    <ul style='list-style-type: disc; margin-left: 1.25rem; color: #4a5568;'>
                        {"".join(f"<li>{char}</li>" for char in characteristics)}
                    </ul>
                    <p style='text-align: left; font-size: 0.875rem; color: #718096; margin-top: 1rem; font-style: italic;'>
                        Note: This application provides a simulated real-time ECG stream and AI analysis for educational purposes only. It is not a medical device and should not be used for actual diagnosis.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else: # MI type
            st.markdown(f"""
                <div style='background-color: #fef2f2; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);'>
                    <p style='text-align: left; font-size: 1.125rem; margin-bottom: 0.5rem;'>
                        <span style='font-weight: 500;'>Diagnosis:</span>
                        <span style='font-weight: 700; color: #b91c1c;'> {diagnosis}</span>
                    </p>
                    <p style='text-align: left; font-size: 1.125rem; margin-bottom: 1rem;'>
                        <span style='font-weight: 500;'>Confidence Score:</span>
                        <span style='font-weight: 700; color: #4a5568;'> {confidence_score}%</span>
                    </p>
                    <h3 style='font-size: 1.25rem; font-weight: 600; color: #4a5568; margin-bottom: 0.75rem;'>Typical ECG Characteristics:</h3>
                    <ul style='list-style-type: disc; margin-left: 1.25rem; color: #4a5568;'>
                        {"".join(f"<li>{char}</li>" for char in characteristics)}
                    </ul>
                    <p style='text-align: left; font-size: 0.875rem; color: #718096; margin-top: 1rem; font-style: italic;'>
                        Note: This application provides a simulated real-time ECG stream and AI analysis for educational purposes only. It is not a medical device and should not be used for actual diagnosis.
                    </p>
                </div>
            """, unsafe_allow_html=True)


    # Initialize ECG data for charting
    ecg_data_points = []
    time_index = 0
    max_ecg_points = 600 # Corresponds to canvas width for a 1:1 pixel mapping in React

    # Loop to continuously update the chart
    while st.session_state.is_streaming:
        new_point_value = generate_ecg_point(time_index, st.session_state.ecg_type)
        ecg_data_points.append(new_point_value)

        # Keep only the latest data points for scrolling effect
        if len(ecg_data_points) > max_ecg_points:
            ecg_data_points = ecg_data_points[-max_ecg_points:]

        # Create a pandas DataFrame for Streamlit chart
        chart_df = pd.DataFrame({
            'index': range(len(ecg_data_points)),
            'ECG Signal': ecg_data_points
        })

        with chart_placeholder.container():
            st.line_chart(chart_df.set_index('index'))

        time_index += 5 # Simulate 5ms per point
        time.sleep(0.005) # Control update speed (5ms sleep)

        # If the user stops the stream mid-loop, break out
        if not st.session_state.is_streaming:
            break
