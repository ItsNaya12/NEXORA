import os

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
from pathlib import Path

# ============================================================
# NEXORA 🌱 QUANTUM-ENHANCED CROP YIELD PREDICTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

API_URL = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
PREDICTION_FILE = BASE_DIR / "quantum_predictions.csv"
COMPARISON_FILE = BASE_DIR / "model_comparison.csv"

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEXORA | Smart Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F5F8F5;
    }

    [data-testid="stSidebar"] {
        background-color: #123D2C;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    .hero {
        background: linear-gradient(120deg, #123D2C, #237A52);
        padding: 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero p {
        color: #E1F3E7;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-title {
        color: #174B34;
        font-size: 23px;
        font-weight: 750;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .info-card {
        background: white;
        border: 1px solid #E3ECE5;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
    }

    .info-card h4 {
        color: #174B34;
        margin-bottom: 8px;
    }

    .info-card p {
        color: #536A5E;
        margin-bottom: 0;
    }

    .prediction-result {
        background: linear-gradient(120deg, #E2F5E8, #F5FCF6);
        border: 1px solid #B9DFC5;
        padding: 24px;
        border-radius: 18px;
        margin-top: 16px;
        margin-bottom: 20px;
    }

    .prediction-result h3 {
        color: #174B34;
        margin-bottom: 8px;
    }

    .small-note {
        color: #607468;
        font-size: 13px;
    }

    div.stButton > button {
        background-color: #237A52;
        color: white;
        border: none;
        border-radius: 10px;
        min-height: 44px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background-color: #185E3D;
        color: white;
        border: none;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border: 1px solid #E3ECE5;
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def check_backend():
    """Check whether the FastAPI backend is responding."""
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=3,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_field_insights(record):
    """
    Generate simple rule-based observations from entered values.

    These observations are illustrative and are not a substitute
    for location-specific agronomic advice.
    """
    insights = []

    rainfall = record["Rainfall (mm)"]
    temperature = record["Temperature (Â°C)"]
    moisture = record["Soil Moisture (%)"]
    ndvi = record["NDVI"]

    if rainfall < 50:
        insights.append(
            "🌱 Rainfall input is relatively low. "
            "Consider checking local rainfall history."
        )
    elif rainfall > 200:
        insights.append(
            "ðŸŒ§ï¸ Rainfall input is relatively high. "
            "Review drainage and local weather conditions."
        )
    else:
        insights.append(
            "🌱 Rainfall input is within the demonstration "
            "range of 50â€“200 mm."
        )

    if temperature < 15:
        insights.append(
            "🌱 Temperature is on the cooler side for this "
            "demonstration. Suitability depends on the crop."
        )
    elif temperature > 35:
        insights.append(
            "🌱 Temperature is high in this demonstration. "
            "Check crop-specific heat stress guidance."
        )
    else:
        insights.append(
            "🌱 Temperature is within the demonstration "
            "range of 15â€“35 Â°C."
        )

    if moisture < 30:
        insights.append(
            "🌱Soil moisture is relatively low. "
            "Verify the sensor reading and crop water needs."
        )
    elif moisture > 70:
        insights.append(
            "🌱 Soil moisture is relatively high. "
            "Check whether the soil is waterlogged."
        )
    else:
        insights.append(
            "🌱 Soil moisture is within the demonstration "
            "range of 30â€“70%."
        )

    if ndvi < 0.3:
        insights.append(
            "🌱 NDVI is relatively low and may indicate "
            "limited vegetation. Check crop stage and image quality."
        )
    elif ndvi > 0.7:
        insights.append(
            "🌱 NDVI is relatively high, which can indicate "
            "strong vegetation in suitable conditions."
        )
    else:
        insights.append(
            "🌱 NDVI is in the middle range of this demonstration."
        )

    return insights


def find_column(df, aliases):
    """Find a dataframe column using possible column names."""
    normalized = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in df.columns
    }

    for alias in aliases:
        key = alias.strip().lower().replace(" ", "_")
        if key in normalized:
            return normalized[key]

    return None


def style_chart(fig, height=330):
    """Apply consistent styling to Plotly charts."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, sans-serif",
            color="#536A5E",
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="#EEF2EF"),
        yaxis=dict(gridcolor="#EEF2EF"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )
    return fig


def load_csv(path):
    """Safely load a CSV file."""
    if not path.exists():
        return None

    try:
        return pd.read_csv(path)
    except (pd.errors.ParserError, OSError, UnicodeDecodeError):
        return None


# ============================================================
# SESSION STATE
# ============================================================

if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# ðŸŒ± NEXORA")
    st.caption("Smart Agriculture Intelligence")
    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Yield Prediction",
            "Model Performance",
            "Prediction History",
            "About NEXORA",
        ],
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown("### 🌱 System Status")

    backend_online = check_backend()

    if backend_online:
        st.success("Prediction API: Online")
    else:
        st.error("Prediction API: Offline")
        st.caption(
            "Start the FastAPI backend in another terminal."
        )

    st.markdown("---")
    st.caption("Quantum-enhanced crop yield research prototype")
    st.caption("NEXORA | Agriculture + AI + Quantum Computing")


# ============================================================
# PAGE 1 🌱 YIELD PREDICTION
# ============================================================

if page == "Yield Prediction":

    st.markdown(
        """
        <div class="hero">
            <h1>ðŸŒ± Smart Crop Yield Prediction</h1>
            <p>
                Explore data-driven crop yield estimates using
                agricultural inputs and a machine-learning backend.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_intro1, col_intro2, col_intro3 = st.columns(3)

    with col_intro1:
        st.markdown(
            """
            <div class="info-card">
                <h4>🌱¸ Weather Inputs</h4>
                <p>Enter rainfall and temperature measurements.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_intro2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🌱 Soil Conditions</h4>
                <p>Provide soil moisture and vegetation index.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_intro3:
        st.markdown(
            """
            <div class="info-card">
                <h4>🌱  Prediction Engine</h4>
                <p>Send input features to the FastAPI service.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">Enter Field Conditions</div>',
        unsafe_allow_html=True,
    )

    with st.form("yield_prediction_form"):

        col1, col2 = st.columns(2)

        with col1:
            rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                max_value=1000.0,
                value=120.0,
                step=5.0,
                help="Rainfall measurement in millimetres.",
            )

            temperature = st.number_input(
                "Temperature (Â°C)",
                min_value=-10.0,
                max_value=60.0,
                value=25.0,
                step=1.0,
                help="Temperature in degrees Celsius.",
            )

        with col2:
            soil_moisture = st.number_input(
                "Soil Moisture (%)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=1.0,
                help="Soil moisture percentage.",
            )

            ndvi = st.number_input(
                "NDVI",
                min_value=-1.0,
                max_value=1.0,
                value=0.65,
                step=0.05,
                format="%.2f",
                help="Normalized Difference Vegetation Index.",
            )

        submitted = st.form_submit_button(
            "🌱 Predict Crop Yield",
            use_container_width=True,
        )

    if submitted:

        if not check_backend():
            st.error(
                "The prediction API is not available. "
                "Start your FastAPI server before predicting."
            )

        else:
            payload = {
                "rainfall_mm": rainfall,
                "temperature_c": temperature,
                "soil_moisture_pct": soil_moisture,
                "ndvi": ndvi,
            }

            with st.spinner(
                "Analyzing field conditions and generating prediction..."
            ):
                try:
                    response = requests.post(
                        f"{API_URL}/api/predict",
                        json=payload,
                        timeout=120,
                    )

                    response.raise_for_status()
                    result = response.json()

                    if (
                        "predicted_yield_tons_per_hectare"
                        not in result
                    ):
                        st.error(
                            "The API response does not contain "
                            "'predicted_yield_tons_per_hectare'. "
                            "Check the response from /docs."
                        )
                    else:
                        predicted_yield = float(
                            result[
                                "predicted_yield_tons_per_hectare"
                            ]
                        )

                        record = {
                            "Timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "Rainfall (mm)": rainfall,
                            "Temperature (Â°C)": temperature,
                            "Soil Moisture (%)": soil_moisture,
                            "NDVI": ndvi,
                            "Predicted Yield (tons/ha)": predicted_yield,
                        }

                        st.session_state.prediction_history.append(
                            record
                        )

                        st.markdown(
                            f"""
                            <div class="prediction-result">
                                <h3>ðŸŒ¾ Estimated Crop Yield</h3>
                                <h1 style="color:#17633D;
                                    font-size:42px;">
                                    {predicted_yield:.2f}
                                    tons/hectare
                                </h1>
                                <p style="color:#536A5E;">
                                    Prediction generated successfully
                                    from the current model.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        metric1, metric2, metric3 = st.columns(3)

                        with metric1:
                            st.metric(
                                "Rainfall",
                                f"{rainfall:.1f} mm",
                            )

                        with metric2:
                            st.metric(
                                "Temperature",
                                f"{temperature:.1f} Â°C",
                            )

                        with metric3:
                            st.metric(
                                "NDVI",
                                f"{ndvi:.2f}",
                            )

                        st.markdown(
                            '<div class="section-title">'
                            'Field Condition Insights</div>',
                            unsafe_allow_html=True,
                        )

                        for insight in get_field_insights(record):
                            st.info(insight)

                        st.caption(
                            "Important: This is a research prototype. "
                            "Predictions depend on training data and "
                            "model quality. They are not guaranteed "
                            "agricultural outcomes or farming advice."
                        )

                except requests.exceptions.Timeout:
                    st.error(
                        "The prediction request timed out. "
                        "Check whether the backend is still training "
                        "or processing the request."
                    )

                except requests.exceptions.HTTPError as exc:
                    st.error(
                        f"The prediction API returned an HTTP error: "
                        f"{exc}"
                    )
                    try:
                        st.code(response.text)
                    except Exception:
                        pass

                except requests.exceptions.RequestException as exc:
                    st.error(
                        f"Could not connect to the prediction API: {exc}"
                    )

                except (ValueError, TypeError, KeyError) as exc:
                    st.error(
                        f"Could not process the prediction response: {exc}"
                    )

    st.markdown("---")

    st.markdown(
        '<div class="section-title">How It Works</div>',
        unsafe_allow_html=True,
    )

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("### 01 Â· Input")
        st.write(
            "Enter rainfall, temperature, soil moisture, "
            "and NDVI values."
        )

    with step2:
        st.markdown("### 02 Â· Process")
        st.write(
            "The Streamlit interface sends your inputs to "
            "the FastAPI prediction service."
        )

    with step3:
        st.markdown("### 03 Â· Result")
        st.write(
            "The backend returns an estimated yield "
            "based on the model it uses."
        )


# ============================================================
# PAGE 2 🌱 MODEL PERFORMANCE
# ============================================================

elif page == "Model Performance":

    st.markdown(
        """
        <div class="hero">
            <h1>ðŸ“Š Model Performance</h1>
            <p>
                Compare model evaluation metrics and inspect
                quantum-model predictions on the available test data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Lower MAE and RMSE are better. Higher RÂ² is generally better. "
        "Always evaluate models on comparable test data."
    )

    # --------------------------------------------------------
    # MODEL COMPARISON TABLE AND METRICS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Model Comparison</div>',
        unsafe_allow_html=True,
    )

    comparison_df = load_csv(COMPARISON_FILE)

    if comparison_df is None:
        st.warning(
            "model_comparison.csv was not found or could not be read. "
            "Run compare_models.py to generate the comparison file."
        )

    else:
        model_col = find_column(
            comparison_df,
            ["Model", "Model_Name", "Algorithm"],
        )
        mae_col = find_column(
            comparison_df,
            ["MAE", "Mean_Absolute_Error"],
        )
        rmse_col = find_column(
            comparison_df,
            ["RMSE", "Root_Mean_Squared_Error"],
        )
        r2_col = find_column(
            comparison_df,
            ["R2", "RÂ²", "R_Squared", "R2_Score"],
        )

        if not all([model_col, mae_col, rmse_col, r2_col]):
            st.error(
                "The comparison CSV must contain model names and "
                "MAE, RMSE, and R2 columns."
            )
            st.dataframe(
                comparison_df,
                use_container_width=True,
            )

        else:
            display_df = comparison_df[
                [model_col, mae_col, rmse_col, r2_col]
            ].copy()

            display_df.columns = [
                "Model",
                "MAE",
                "RMSE",
                "RÂ²",
            ]

            for metric in ["MAE", "RMSE", "RÂ²"]:
                display_df[metric] = pd.to_numeric(
                    display_df[metric],
                    errors="coerce",
                )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

            best_mae_row = display_df.loc[
                display_df["MAE"].idxmin()
            ]
            best_rmse_row = display_df.loc[
                display_df["RMSE"].idxmin()
            ]
            best_r2_row = display_df.loc[
                display_df["RÂ²"].idxmax()
            ]

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Lowest MAE",
                    f"{best_mae_row['MAE']:.3f}",
                    help=f"Model: {best_mae_row['Model']}",
                )

            with m2:
                st.metric(
                    "Lowest RMSE",
                    f"{best_rmse_row['RMSE']:.3f}",
                    help=f"Model: {best_rmse_row['Model']}",
                )

            with m3:
                st.metric(
                    "Highest RÂ²",
                    f"{best_r2_row['RÂ²']:.3f}",
                    help=f"Model: {best_r2_row['Model']}",
                )

            # ------------------------------------------------
            # METRIC COMPARISON CHARTS
            # ------------------------------------------------

            st.markdown(
                '<div class="section-title">'
                'Evaluation Metric Comparison</div>',
                unsafe_allow_html=True,
            )

            chart1, chart2 = st.columns(2)

            with chart1:
                mae_fig = go.Figure()

                mae_fig.add_trace(
                    go.Bar(
                        x=display_df["Model"],
                        y=display_df["MAE"],
                        marker_color="#21845D",
                        text=display_df["MAE"].round(3),
                        textposition="outside",
                        name="MAE",
                    )
                )

                mae_fig.update_layout(
                    title="Mean Absolute Error (MAE)",
                    xaxis_title="Model",
                    yaxis_title="MAE",
                )

                st.plotly_chart(
                    style_chart(mae_fig),
                    use_container_width=True,
                )

            with chart2:
                rmse_fig = go.Figure()

                rmse_fig.add_trace(
                    go.Bar(
                        x=display_df["Model"],
                        y=display_df["RMSE"],
                        marker_color="#4C8C70",
                        text=display_df["RMSE"].round(3),
                        textposition="outside",
                        name="RMSE",
                    )
                )

                rmse_fig.update_layout(
                    title="Root Mean Squared Error (RMSE)",
                    xaxis_title="Model",
                    yaxis_title="RMSE",
                )

                st.plotly_chart(
                    style_chart(rmse_fig),
                    use_container_width=True,
                )

            r2_fig = go.Figure()

            r2_fig.add_trace(
                go.Bar(
                    x=display_df["Model"],
                    y=display_df["RÂ²"],
                    marker_color="#D99B36",
                    text=display_df["RÂ²"].round(3),
                    textposition="outside",
                    name="RÂ²",
                )
            )

            r2_fig.update_layout(
                title="RÂ² Score",
                xaxis_title="Model",
                yaxis_title="RÂ²",
            )

            st.plotly_chart(
                style_chart(r2_fig),
                use_container_width=True,
            )

            st.download_button(
                label="â¬‡ï¸ Download Model Comparison CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name="nexora_model_comparison.csv",
                mime="text/csv",
            )

    # --------------------------------------------------------
    # ACTUAL VS PREDICTED YIELD â€” QUANTUM QNN
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        '🌱 Actual vs Predicted Yield</div>',
        unsafe_allow_html=True,
    )

    prediction_df = load_csv(PREDICTION_FILE)

    if prediction_df is None:
        st.warning(
            "quantum_predictions.csv was not found or could not be read. "
            "Run quantum_model.py to generate it."
        )

    else:
        actual_col = find_column(
            prediction_df,
            ["Actual_Yield", "Actual Yield", "Actual"],
        )

        predicted_col = find_column(
            prediction_df,
            ["Predicted_Yield", "Predicted Yield", "Predicted"],
        )

        if actual_col is None or predicted_col is None:
            st.warning(
                "Expected columns Actual_Yield and Predicted_Yield "
                "were not found in quantum_predictions.csv."
            )

            st.caption(
                "Available columns: "
                + ", ".join(map(str, prediction_df.columns))
            )

        else:
            chart_df = prediction_df[
                [actual_col, predicted_col]
            ].copy()

            chart_df[actual_col] = pd.to_numeric(
                chart_df[actual_col],
                errors="coerce",
            )

            chart_df[predicted_col] = pd.to_numeric(
                chart_df[predicted_col],
                errors="coerce",
            )

            chart_df = chart_df.dropna().reset_index(drop=True)

            if chart_df.empty:
                st.warning(
                    "The prediction file contains no valid numeric rows."
                )

            else:
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=chart_df[actual_col],
                        y=chart_df[predicted_col],
                        mode="markers",
                        name="Test predictions",
                        marker=dict(
                            size=10,
                            color="#21845D",
                            opacity=0.8,
                        ),
                        hovertemplate=(
                            "Actual: %{x:.2f} tons/ha<br>"
                            "Predicted: %{y:.2f} tons/ha"
                            "<extra></extra>"
                        ),
                    )
                )

                minimum = min(
                    chart_df[actual_col].min(),
                    chart_df[predicted_col].min(),
                )

                maximum = max(
                    chart_df[actual_col].max(),
                    chart_df[predicted_col].max(),
                )

                if minimum == maximum:
                    minimum -= 0.5
                    maximum += 0.5

                fig.add_trace(
                    go.Scatter(
                        x=[minimum, maximum],
                        y=[minimum, maximum],
                        mode="lines",
                        name="Ideal prediction",
                        line=dict(
                            color="#D97706",
                            dash="dash",
                            width=2,
                        ),
                    )
                )

                fig.update_layout(
                    title="Quantum QNN: Actual vs Predicted",
                    xaxis_title="Actual yield (tons/ha)",
                    yaxis_title="Predicted yield (tons/ha)",
                    height=430,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#FFFFFF",
                    font=dict(color="#536A5E"),
                    margin=dict(
                        l=20,
                        r=20,
                        t=55,
                        b=25,
                    ),
                    xaxis=dict(gridcolor="#EEF2EF"),
                    yaxis=dict(gridcolor="#EEF2EF"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0,
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.caption(
                    "Points closer to the dashed line indicate "
                    "predictions closer to actual test-set values. "
                    "The chart reflects the available test data."
                )

                prediction_export = chart_df.rename(
                    columns={
                        actual_col: "Actual_Yield",
                        predicted_col: "Predicted_Yield",
                    }
                )

                st.download_button(
                    label="â¬‡ï¸ Download Actual vs Predicted Data",
                    data=prediction_export.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="nexora_actual_vs_predicted.csv",
                    mime="text/csv",
                )

    # --------------------------------------------------------
    # TRANSPARENT MODEL LIMITATIONS
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        'âš ï¸ Understanding the Results</div>',
        unsafe_allow_html=True,
    )

    st.warning(
        """
        Model performance must be judged using independent test data.
        A quantum model is not automatically more accurate than a
        classical model. If the current Random Forest has lower error
        and a higher RÂ² score, report that result honestly.

        Results generated from synthetic data are demonstrations only
        and do not establish real-world agricultural performance.
        """
    )


# ============================================================
# PAGE 3 🌱 PREDICTION HISTORY
# ============================================================

elif page == "Prediction History":

    st.markdown(
        """
        <div class="hero">
            <h1>🌱 Prediction History</h1>
            <p>
                Review and export predictions generated during
                this Streamlit session.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state.prediction_history

    if not history:
        st.info(
            "No predictions have been generated in this session yet. "
            "Open Yield Prediction and submit your field measurements."
        )

    else:
        history_df = pd.DataFrame(history)

        h1, h2 = st.columns(2)

        with h1:
            st.metric(
                "Total Predictions",
                len(history_df),
            )

        with h2:
            st.metric(
                "Average Predicted Yield",
                (
                    f"{history_df['Predicted Yield (tons/ha)'].mean():.2f} "
                    "tons/ha"
                ),
            )

        st.markdown(
            '<div class="section-title">Prediction Records</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

        trend_fig = go.Figure()

        trend_fig.add_trace(
            go.Scatter(
                x=list(range(1, len(history_df) + 1)),
                y=history_df["Predicted Yield (tons/ha)"],
                mode="lines+markers",
                name="Predicted yield",
                line=dict(
                    color="#21845D",
                    width=3,
                ),
                marker=dict(size=8),
            )
        )

        trend_fig.update_layout(
            title="Yield Predictions During This Session",
            xaxis_title="Prediction number",
            yaxis_title="Predicted yield (tons/ha)",
        )

        st.plotly_chart(
            style_chart(trend_fig),
            use_container_width=True,
        )

        st.download_button(
            label="â¬‡ï¸ Export Prediction History",
            data=history_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="nexora_prediction_history.csv",
            mime="text/csv",
        )

        if st.button(
            "🌱 Clear Session History",
            use_container_width=False,
        ):
            st.session_state.prediction_history = []
            st.rerun()

    st.caption(
        "History is stored in Streamlit session state. "
        "It is not a permanent database and may disappear after "
        "a session reset or application restart."
    )


# ============================================================
# PAGE 4 â€” ABOUT NEXORA
# ============================================================

elif page == "About NEXORA":

    st.markdown(
        """
        <div class="hero">
            <h1>🌱About NEXORA</h1>
            <p>
                Exploring AI and quantum machine learning
                for agricultural prediction.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Project Overview</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        NEXORA is a research prototype designed to explore crop yield
        prediction using agricultural input features and machine
        learning. Its interface brings together field measurements,
        a prediction API, model evaluation, and prediction visualizations.
        """
    )

    about1, about2 = st.columns(2)

    with about1:
        st.markdown(
            """
            <div class="info-card">
                <h4>🌱 Agricultural Inputs</h4>
                <p>
                    Rainfall, temperature, soil moisture,
                    and Normalized Difference Vegetation Index (NDVI).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h4>🌱  Machine Learning</h4>
                <p>
                    Model predictions and performance comparisons
                    help assess the behaviour of different approaches.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with about2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🌱 Quantum Machine Learning</h4>
                <p>
                    A quantum neural network (QNN) is explored
                    as an experimental approach to prediction.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <h4>🌱Model Evaluation</h4>
                <p>
                    MAE, RMSE, RÂ², and actual-versus-predicted
                    visualizations help examine model performance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Technology Stack</div>',
        unsafe_allow_html=True,
    )

    technology_data = pd.DataFrame(
        {
            "Technology": [
                "Python",
                "Streamlit",
                "FastAPI",
                "Qiskit",
                "Pandas",
                "Plotly",
                "Scikit-learn",
            ],
            "Purpose": [
                "Core programming language",
                "Interactive user interface",
                "Prediction API",
                "Quantum computing and QNN experiments",
                "Data handling",
                "Interactive charts",
                "Classical machine-learning models",
            ],
        }
    )

    st.dataframe(
        technology_data,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Project Limitations</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        - Predictions are only as reliable as the model and training data.
        - Synthetic data is useful for prototyping, but not proof of
          performance on real farms.
        - Quantum machine learning does not guarantee an advantage over
          classical machine-learning methods.
        - Real-world validation requires reliable agricultural datasets,
          appropriate train/test separation, and domain expertise.
        """
    )

    st.success(
        "NEXORA's goal is to explore, evaluate, and communicate "
        "data-driven agricultural prediction responsibly."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:10px; color:#718276;">
        <strong>NEXORA</strong> Â· Smart Agriculture Research Prototype<br>
        <span style="font-size:12px;">
            AI + Quantum Machine Learning + Agriculture
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
