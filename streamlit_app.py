import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.title("Minimal plotly_events Test")

# Known positive data
stress_values = np.array([10, 100, 1000, 10000])
e_values = np.array([1.2, 1.15, 1.1, 1.05])

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stress_values,
    y=e_values,
    mode="markers",
    marker=dict(size=10, color="blue"),
    name="Data"
))
fig.update_xaxes(type="log", title_text="Stress [log scale]")
fig.update_layout(title="Minimal Example")

events = plotly_events(fig, click_event=True, hover_event=False)

# Print out any events
st.write("Click events:", events)
