import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.title("Minimal Click Example")

# If you have valid data, ensure it's loaded correctly:
stress_values = np.array([10, 100, 1000, 10000])  # Example data
e_values = np.array([1.2, 1.15, 1.1, 1.05])

# Session state for selected points
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = set()

# Build marker colors
colors = []
for i in range(len(stress_values)):
    if i in st.session_state.selected_indices:
        colors.append("red")
    else:
        colors.append("blue")

# Create figure
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stress_values,
    y=e_values,
    mode="markers",
    marker=dict(size=10, color=colors),
    name="Data Points"
))
fig.update_xaxes(type="log", title_text="Stress [log scale]")
fig.update_layout(title="Click Points to Toggle Color")

# Display with plotly_events
events = plotly_events(fig, click_event=True, hover_event=False)

# Toggle selection if any clicks happened
if events:
    for evt in events:
        idx = evt.get("pointIndex")
        if idx is not None:
            if idx in st.session_state.selected_indices:
                st.session_state.selected_indices.remove(idx)
            else:
                st.session_state.selected_indices.add(idx)

# Show which points are selected
st.write("Currently selected indices:", list(st.session_state.selected_indices))
