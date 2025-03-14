import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events  # New import for click events
import base64, io

# --- App Title ---
st.title("Consolidation Test Analysis")

# --- File Upload ---
st.write("Upload a text file with two rows:")
st.write("- First row: void ratio (e) values (comma-separated)")
st.write("- Second row: stress values (in the unit you used)")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv"])

# --- Unit Selection ---
unit = st.radio("Select the unit of stress values provided:", ('psf', 'ksf', 'kPa'))

# --- Process Uploaded File ---
if uploaded_file is not None:
    try:
        # Read the file into a DataFrame (assuming comma-separated values)
        df = pd.read_csv(uploaded_file, header=None)
        # Assuming first row is void ratio (e) and second row is stress values
        e_values = df.iloc[0].values.astype(float)
        stress_values = df.iloc[1].values.astype(float)
    except Exception as e:
        st.error("Error processing file: " + str(e))
    
    # --- Create the Plot ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stress_values,
        y=e_values,
        mode='markers',
        marker=dict(size=10, color='blue'),  # initial color: blue
        name='Data Points'
    ))
    
    # Set x-axis to logarithmic scale and invert the y-axis
    fig.update_xaxes(type="log", title_text=f"Stress ({unit}) [log scale]")
    fig.update_layout(title="e vs. Stress)", dragmode='select')
    
    # Display the initial plot
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Interactive Click Events for Selection ---
    # Initialize session state to track selected point indices if not already present.
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = set()
    
    # Capture click events on the figure.
    events = plotly_events(fig, click_event=True, hover_event=False)
    if events:
        for event in events:
            idx = event.get("pointIndex")
            if idx is not None:
                if idx in st.session_state.selected_indices:
                    st.session_state.selected_indices.remove(idx)
                else:
                    st.session_state.selected_indices.add(idx)
    
    # Update the marker colors based on selected points.
    colors = []
    for i in range(len(stress_values)):
        if i in st.session_state.selected_indices:
            colors.append("red")  # selected points in red
        else:
            colors.append("blue")  # unselected remain blue
    fig.data[0].marker.color = colors
    
    # Display the updated plot with selection changes.
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Interactive Inputs for Line Fitting ---
    st.write("### Define Stress Range for Line Fitting")
    col1, col2 = st.columns(2)
    with col1:
        stress_min = st.number_input("Stress minimum", value=float(np.min(stress_values)))
    with col2:
        stress_max = st.number_input("Stress maximum", value=float(np.max(stress_values)))
    
    if st.button("Fit Line to Selected Range"):
        # Filter the data based on the specified stress range
        mask = (stress_values >= stress_min) & (stress_values <= stress_max)
        selected_stress = stress_values[mask]
        selected_e = e_values[mask]
        
        if len(selected_stress) < 2:
            st.error("Please select at least two data points within the range for fitting.")
        else:
            # Perform linear regression on log10(stress) vs. e
            log_stress = np.log10(selected_stress)
            coeffs = np.polyfit(log_stress, selected_e, 1)
            slope, intercept = coeffs
            
            st.write(f"Fitted line: **slope = {slope:.3f}**, **intercept = {intercept:.3f}**")
            
            # Generate fitted line data over the defined stress range
            x_fit = np.linspace(stress_min, stress_max, 100)
            y_fit = intercept + slope * np.log10(x_fit)
            
            # Add the fitted line to the figure
            fig.add_trace(go.Scatter(
                x=x_fit,
                y=y_fit,
                mode='lines',
                line=dict(color='red'),
                name=f'Fit: slope = {slope:.3f}'
            ))
            
            st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Awaiting file upload...")
