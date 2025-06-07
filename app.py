import streamlit as st
import numpy as np
import time
import math
import pandas as pd
from io import BytesIO

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
st.write("This application simulates a real-time ECG stream and an AI's ability to differentiate between a normal ECG and one indicative of Myocardial Infarction. Select a scenario to start the live stream or upload a PDF for simulated analysis.")

# State management for Streamlit
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'ecg_type' not in st.session_state:
    st.session_state.ecg_type = None
if 'uploaded_pdf' not in st.session_state:
    st.session_state.uploaded_pdf = None
if 'pdf_analysis_triggered' not in st.session_state:
    st.session_state.pdf_analysis_triggered = False

# --- Section for Real-time Stream Simulation ---
st.header("Simulate Real-time ECG Stream")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Start Normal ECG Stream", disabled=st.session_state.is_streaming):
        st.session_state.is_streaming = True
        st.session_state.ecg_type = 'normal'
        st.session_state.pdf_analysis_triggered = False # Reset PDF analysis state
        st.session_state.uploaded_pdf = None # Clear uploaded PDF
        # st.experimental_rerun() # REMOVED: No longer needed here
        
with col2:
    if st.button("Start MI ECG Stream", type="secondary", disabled=st.session_state.is_streaming):
        st.session_state.is_streaming = True
        st.session_state.ecg_type = 'mi'
        st.session_state.pdf_analysis_triggered = False # Reset PDF analysis state
        st.session_state.uploaded_pdf = None # Clear uploaded PDF
        # st.experimental_rerun() # REMOVED: No longer needed here

with col3:
    if st.session_state.is_streaming:
        if st.button("Stop Stream", type="tertiary"):
            st.session_state.is_streaming = False
            st.session_state.ecg_type = None
            st.session_state.pdf_analysis_triggered = False # Reset PDF analysis state
            # st.experimental_rerun() # REMOVED: No longer needed here

# Placeholder for the ECG chart
chart_placeholder = st.empty()
analysis_placeholder = st.empty() # Placeholder for analysis results


# --- Section for PDF Upload and Simulated Analysis ---
st.header("Upload ECG PDF for Simulated Analysis")
uploaded_file = st.file_uploader("Upload a patient ECG PDF", type="pdf", disabled=st.session_state.is_streaming)

if uploaded_file is not None:
    st.session_state.uploaded_pdf = uploaded_file # Store uploaded file in session state
    st.success(f"PDF uploaded successfully: {uploaded_file.name}")
    st.info("Note: This app will simulate an AI diagnosis for the uploaded PDF. Actual ECG signal extraction and real AI analysis from a PDF is a complex task beyond the scope of this demo.")

    # Display the uploaded PDF (a basic embed, may not work on all environments without external libraries)
    # For a full-fledged PDF viewer, you might need `streamlit_pdf_viewer`
    # st.write(f"Displaying {uploaded_file.name}:")
    # st.download_button(
    #     label="Download Uploaded PDF",
    #     data=uploaded_file.getvalue(),
    #     file_name=uploaded_file.name,
    #     mime="application/pdf"
    # )
    # You could also use an iframe here, but security policies often restrict this
    # st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}" width="700" height="400" type="application/pdf"></iframe>', unsafe_allow_html=True)


    st.subheader("Simulate AI Analysis for Uploaded PDF")
    col_pdf_normal, col_pdf_mi = st.columns(2)

    with col_pdf_normal:
        if st.button("Simulate Normal Result for PDF", disabled=st.session_state.is_streaming):
            st.session_state.is_streaming = False # Ensure streaming stops if PDF analysis starts
            st.session_state.pdf_analysis_triggered = True
            st.session_state.ecg_type = 'normal' # Set type for simulated analysis
            # st.experimental_rerun()

    with col_pdf_mi:
        if st.button("Simulate MI Result for PDF", type="secondary", disabled=st.session_state.is_streaming):
            st.session_state.is_streaming = False # Ensure streaming stops if PDF analysis starts
            st.session_state.pdf_analysis_triggered = True
            st.session_state.ecg_type = 'mi' # Set type for simulated analysis
            # st.experimental_rerun()

    # Clear analysis results if a new PDF is uploaded or stream started
    if not st.session_state.is_streaming and not st.session_state.pdf_analysis_triggered:
        analysis_placeholder.empty()

# --- Display Real-time ECG Stream (if active) ---
if st.session_state.is_streaming and st.session_state.ecg_type:
    # Perform AI analysis immediately when stream starts (only if not already triggered by PDF)
    if not st.session_state.pdf_analysis_triggered: # Only re-run analysis if it's a new stream
        diagnosis, confidence_score, characteristics = perform_ai_analysis(st.session_state.ecg_type)
    
        # Display initial analysis results in the placeholder
        with analysis_placeholder.container():
            st.markdown(f"<h2 style='text-align: center; color: #4a5568;'>AI Analysis Result:</h2>", unsafe_allow_html=True)
            diagnosis_style_color = '#065f46' if st.session_state.ecg_type == 'normal' else '#b91c1c'
            bg_color = '#ecfdf5' if st.session_state.ecg_type == 'normal' else '#fef2f2'
            st.markdown(f"""
                <div style='background-color: {bg_color}; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);'>
                    <p style='text-align: left; font-size: 1.125rem; margin-bottom: 0.5rem;'>
                        <span style='font-weight: 500;'>Diagnosis:</span>
                        <span style='font-weight: 700; color: {diagnosis_style_color};'> {diagnosis}</span>
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

# --- Display PDF Analysis Results (if triggered) ---
if st.session_state.pdf_analysis_triggered and st.session_state.ecg_type:
    # Perform AI analysis
    diagnosis, confidence_score, characteristics = perform_ai_analysis(st.session_state.ecg_type)
    
    with analysis_placeholder.container():
        st.markdown(f"<h2 style='text-align: center; color: #4a5568;'>AI Analysis Result for Uploaded PDF:</h2>", unsafe_allow_html=True)
        diagnosis_style_color = '#065f46' if st.session_state.ecg_type == 'normal' else '#b91c1c'
        bg_color = '#ecfdf5' if st.session_state.ecg_type == 'normal' else '#fef2f2'
        st.markdown(f"""
            <div style='background-color: {bg_color}; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);'>
                <p style='text-align: left; font-size: 1.125rem; margin-bottom: 0.5rem;'>
                    <span style='font-weight: 500;'>Diagnosis:</span>
                    <span style='font-weight: 700; color: {diagnosis_style_color};'> {diagnosis}</span>
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
                    Note: This application provides a simulated AI analysis for uploaded PDFs for educational purposes only. It is not a medical device and should not be used for actual diagnosis.
                </p>
            </div>
        """, unsafe_allow_html=True)
    # Clear PDF analysis flag after displaying results
    st.session_state.pdf_analysis_triggered = False


      
       
