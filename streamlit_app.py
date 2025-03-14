import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Example data (replace with your actual data)
stress_values = np.array([120, 240, 1000, 2000, 4000, 8000])
e_values = np.array([2.465, 2.45, 2.3, 2.13, 1.91, 1.56])

# Create a Plotly figure with your data
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stress_values,
    y=e_values,
    mode='markers',
    marker=dict(size=10, color='blue'),
    name='Data Points'
))
fig.update_xaxes(type="log", title_text="Stress (psf) [log scale]")
fig.update_yaxes(autorange='reversed', title_text="Void Ratio (e)")
fig.update_layout(title="e vs. log(Stress)", dragmode='select')

# Use Streamlit session state to track selected point indices
if 'selected_indices' not in st.session_state:
    st.session_state.selected_indices = set()

# Capture click events on the Plotly chart.
# The function returns a list of events, each with a "pointIndex" key.
events = plotly_events(fig, click_event=True, hover_event=False, override_height=500)

# Process the events: toggle the selection for each clicked point.
if events:
    for event in events:
        idx = event.get("pointIndex")
        if idx is not None:
            if idx in st.session_state.selected_indices:
                st.session_state.selected_indices.remove(idx)
            else:
                st.session_state.selected_indices.add(idx)

# Update the marker colors based on selection: selected points become red.
colors = []
for i in range(len(stress_values)):
    if i in st.session_state.selected_indices:
        colors.append("red")
    else:
        colors.append("blue")
fig.data[0].marker.color = colors

# Display the updated figure
st.plotly_chart(fig, use_container_width=True)

# Optionally, show the list of selected indices
st.write("Selected point indices:", list(st.session_state.selected_indices))
