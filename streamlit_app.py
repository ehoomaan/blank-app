import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.title("Consolidation Test Analysis")

uploaded_file = st.file_uploader("Upload a text file (first row: e, second row: stress)", type=["txt", "csv"])
unit = st.radio("Select the unit of stress values provided:", ["psf", "ksf", "kPa"])

# Maintain a set of selected point indices across re-runs
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = set()

if uploaded_file is not None:
    # Read the file
    df = pd.read_csv(uploaded_file, header=None)
    e_values = df.iloc[0].values.astype(float)
    stress_values = df.iloc[1].values.astype(float)

    # Build the marker color array from the current session state
    colors = []
    for i in range(len(stress_values)):
        if i in st.session_state.selected_indices:
            colors.append("red")  # selected
        else:
            colors.append("blue")  # not selected

    # Create a single Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stress_values,
        y=e_values,
        mode="markers",
        marker=dict(size=10, color=colors),
        name="Data Points"
    ))
    # Logarithmic x-axis, normal y-axis (no inversion)
    fig.update_xaxes(type="log", title_text=f"Stress ({unit}) [log scale]")
    fig.update_layout(title="e vs. log(Stress)")

    # Use plotly_events to display the figure and capture clicks
    events = plotly_events(
        fig, 
        click_event=True, 
        hover_event=False, 
        key="main_plot"
    )

    # Toggle the selection for any newly clicked points
    if events:
        changed = False
        for evt in events:
            idx = evt.get("pointIndex")
            if idx is not None:
                if idx in st.session_state.selected_indices:
                    st.session_state.selected_indices.remove(idx)
                else:
                    st.session_state.selected_indices.add(idx)
                changed = True

        # If anything changed, force a rerun to refresh colors
        if changed:
            st.experimental_rerun()

    # Button to fit a line only to selected points
    if st.button("Fit a Line"):
        if len(st.session_state.selected_indices) < 2:
            st.error("Please select at least two points by clicking them.")
        else:
            # Gather selected points
            selected_indices = list(st.session_state.selected_indices)
            selected_stress = stress_values[selected_indices]
            selected_e = e_values[selected_indices]

            # Fit a line: e = intercept + slope * log10(stress)
            slope, intercept = np.polyfit(np.log10(selected_stress), selected_e, 1)
            st.write(f"**Slope:** {slope:.3f}, **Intercept:** {intercept:.3f}")

            # Generate line data
            x_fit = np.linspace(selected_stress.min(), selected_stress.max(), 100)
            y_fit = intercept + slope * np.log10(x_fit)

            # Build a new figure with the fitted line
            final_colors = []
            for i in range(len(stress_values)):
                if i in st.session_state.selected_indices:
                    final_colors.append("red")
                else:
                    final_colors.append("blue")

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=stress_values,
                y=e_values,
                mode="markers",
                marker=dict(size=10, color=final_colors),
                name="Data Points"
            ))
            fig2.add_trace(go.Scatter(
                x=x_fit,
                y=y_fit,
                mode="lines",
                line=dict(color="green"),
                name="Fitted Line"
            ))
            fig2.update_xaxes(type="log", title_text=f"Stress ({unit}) [log scale]")
            fig2.update_layout(title="e vs. log(Stress) + Fitted Line")

            st.plotly_chart(fig2, use_container_width=True)

else:
    st.write("Awaiting file upload...")
