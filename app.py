
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ============================================================
# 🌱 NEXORA — SMART CROP YIELD PREDICTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
API_URL = os.getenv(
    "NEXORA_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

HISTORY_FILE = BASE_DIR / "quantum_predictions.csv"
COMPARISON_FILE = BASE_DIR / "model_comparison.csv"

st.set_page_config(
    page_title="NEXORA | Smart Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 🎨 STYLING
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f4fbf4, #edf5ef);
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(120deg, #123d2a, #21865a);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    font-size: 35px;
}
.hero p {
    color: #e4f7e9;
    font-size: 16px;
}
.info-card {
    background: white;
    border: 1px solid #d9e9dc;
    padding: 20px;
    border-radius: 15px;
    min-height: 135px;
    box-shadow: 0 3px 12px rgba(20, 70, 40, 0.05);
}
.info-card h3 {
    color: #17633d;
}
.section-title {
    color: #17633d;
    font-size: 23px;
    font-weight: 700;
    margin: 20px 0 12px 0;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce9df;
    padding: 15px;
    border-radius: 12px;
}
.stButton > button,
.stFormSubmitButton > button {
    background: #17633d;
    color: white;
    border-radius: 10px;
    border: none;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #21865a;
    color: white;
}
.footer {
    text-align: center;
    color: #64816d;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔧 HELPER FUNCTIONS
# ============================================================

def check_backend():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=4
        )
        return response.ok
    except requests.RequestException:
        return False


def load_history():
    if HISTORY_FILE.exists():
        try:
            return pd.read_csv(HISTORY_FILE)
        except (OSError, pd.errors.ParserError):
            return pd.DataFrame()
    return pd.DataFrame()


def save_history(record):
    history = load_history()
    updated = pd.concat(
        [history, pd.DataFrame([record])],
        ignore_index=True
    )
    updated.to_csv(HISTORY_FILE, index=False)


def load_comparison():
    if COMPARISON_FILE.exists():
        try:
            return pd.read_csv(COMPARISON_FILE)
        except (OSError, pd.errors.ParserError):
            return pd.DataFrame()
    return pd.DataFrame()


def extract_yield(response_data):
    """Read a yield value from common API response field names."""
    keys = [
        "predicted_yield",
        "prediction",
        "yield_prediction",
        "yield",
        "predicted_yield_tonnes_per_hectare",
    ]

    for key in keys:
        value = response_data.get(key)
        if isinstance(value, (int, float)):
            return float(value)

    nested = response_data.get("result")
    if isinstance(nested, dict):
        return extract_yield(nested)

    return None


def show_footer():
    st.markdown("""
    <div class="footer">
        <strong>🌱 NEXORA</strong> · Smart Agriculture Research Prototype<br>
        AI + ⚛️ Quantum Machine Learning + 🌾 Agriculture
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 🧭 SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 🌱 NEXORA")
    st.caption("Smart Agriculture Intelligence")
    st.markdown("---")

    page = st.radio(
        "🧭 Navigation",
        [
            "🌾 Yield Prediction",
            "📊 Model Performance",
            "🗂️ Prediction History",
            "ℹ️ About NEXORA",
        ],
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown("### ⚙️ System Status")

    backend_online = check_backend()

    if backend_online:
        st.success("🟢 Backend Online")
    else:
        st.warning("🟠 Backend Unavailable")
        st.caption(
            "Check your API URL and ensure the backend is running."
        )

    st.markdown("---")
    st.caption("🌍 Agriculture · AI · Quantum Computing")


# ============================================================
# 🌾 PAGE 1 — YIELD PREDICTION
# ============================================================

if page == "🌾 Yield Prediction":

    st.markdown("""
    <div class="hero">
        <h1>🌱 Smart Crop Yield Prediction</h1>
        <p>
            Explore data-driven crop yield estimates using weather,
            soil, and vegetation measurements.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌿 Agricultural Intelligence")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>🌦️ Weather Inputs</h3>
            <p>Enter rainfall and temperature measurements.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>🌱 Soil Conditions</h3>
            <p>Provide soil moisture and vegetation index.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <h3>⚛️ Prediction Engine</h3>
            <p>Request a yield estimate from the prediction API.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📝 Enter Field Measurements</div>',
                unsafe_allow_html=True)

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            rainfall = st.number_input(
                "🌧️ Rainfall (mm)",
                min_value=0.0,
                max_value=1000.0,
                value=100.0,
                step=5.0,
            )

            temperature = st.number_input(
                "🌡️ Temperature (°C)",
                min_value=-10.0,
                max_value=60.0,
                value=28.0,
                step=0.5,
            )

        with col2:
            soil_moisture = st.number_input(
                "💧 Soil Moisture (%)",
                min_value=0.0,
                max_value=100.0,
                value=45.0,
                step=1.0,
            )

            ndvi = st.number_input(
                "🛰️ Vegetation Index (NDVI)",
                min_value=-1.0,
                max_value=1.0,
                value=0.55,
                step=0.05,
                format="%.2f",
            )

        submitted = st.form_submit_button(
            "🚀 Predict Crop Yield",
            use_container_width=True,
        )

    if submitted:
        if not backend_online:
            st.error(
                "The prediction backend is unavailable. "
                "Check the NEXORA_API_URL setting and backend service."
            )
        else:
            payload = {
                "rainfall": rainfall,
                "temperature": temperature,
                "soil_moisture": soil_moisture,
                "ndvi": ndvi,
            }

            try:
                with st.spinner("🧠 Analysing field measurements..."):
                    response = requests.post(
                        f"{API_URL}/api/predict",
                        json=payload,
                        timeout=60,
                    )

                if not response.ok:
                    st.error(
                        f"Prediction API returned HTTP {response.status_code}."
                    )
                    st.code(response.text[:1500])

                else:
                    data = response.json()
                    predicted_yield = extract_yield(data)

                    if predicted_yield is None:
                        st.warning(
                            "The API responded, but its yield field "
                            "was not recognised. Check the response below."
                        )
                        st.json(data)
                    else:
                        record = {
                            "Rainfall (mm)": rainfall,
                            "Temperature (°C)": temperature,
                            "Soil Moisture (%)": soil_moisture,
                            "NDVI": ndvi,
                            "Predicted Yield": predicted_yield,
                        }

                        try:
                            save_history(record)
                        except OSError as error:
                            st.warning(
                                f"Could not save local history: {error}"
                            )

                        st.success("✅ Prediction completed!")

                        st.markdown(
                            '<div class="section-title">'
                            '🌾 Estimated Crop Yield</div>',
                            unsafe_allow_html=True,
                        )

                        st.metric(
                            "Predicted Yield",
                            f"{predicted_yield:,.3f}",
                            help="Value returned by the configured backend.",
                        )

                        m1, m2, m3 = st.columns(3)

                        m1.metric("🌧️ Rainfall", f"{rainfall:.1f} mm")
                        m2.metric("🌡️ Temperature", f"{temperature:.1f} °C")
                        m3.metric("💧 Soil Moisture", f"{soil_moisture:.1f}%")

                        st.markdown("### 🔎 Field Input Summary")
                        st.dataframe(
                            pd.DataFrame([record]),
                            use_container_width=True,
                            hide_index=True,
                        )

                        with st.expander("🔧 View complete API response"):
                            st.json(data)

            except requests.RequestException as error:
                st.error(f"Prediction request failed: {error}")

    st.markdown("---")
    st.markdown("### 🔄 How NEXORA Works")

    step1, step2, step3 = st.columns(3)

    step1.info("**01 · Input**\n\nEnter weather and soil measurements.")
    step2.info("**02 · Process**\n\nThe backend processes the submitted features.")
    step3.info("**03 · Result**\n\nView the yield estimate returned by the API.")

    show_footer()


# ============================================================
# 📊 PAGE 2 — MODEL PERFORMANCE
# ============================================================

elif page == "📊 Model Performance":

    st.markdown("""
    <div class="hero">
        <h1>📊 Model Performance</h1>
        <p>
            Review available model-comparison metrics and prediction data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    comparison_df = load_comparison()

    if comparison_df.empty:
        st.info(
            "No model_comparison.csv data was found. "
            "Add your evaluated model metrics to this file to display charts."
        )
    else:
        st.markdown("### 📋 Comparison Data")
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )

        numeric_columns = comparison_df.select_dtypes(
            include="number"
        ).columns.tolist()

        model_column = next(
            (
                column for column in comparison_df.columns
                if column.lower() in ["model", "model_name", "algorithm"]
            ),
            None,
        )

        if numeric_columns:
            metric = st.selectbox(
                "📈 Select metric to visualise",
                numeric_columns,
            )

            if model_column:
                fig = px.bar(
                    comparison_df,
                    x=model_column,
                    y=metric,
                    color=model_column,
                    title=f"📊 Model Comparison — {metric}",
                    text_auto=".3f",
                )
            else:
                chart_df = comparison_df.copy()
                chart_df["Row"] = range(1, len(chart_df) + 1)
                fig = px.bar(
                    chart_df,
                    x="Row",
                    y=metric,
                    title=f"📊 Metric — {metric}",
                    text_auto=".3f",
                )

            fig.update_layout(
                template="plotly_white",
                showlegend=bool(model_column),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "⬇️ Download Model Comparison CSV",
            data=comparison_df.to_csv(index=False).encode("utf-8"),
            file_name="nexora_model_comparison.csv",
            mime="text/csv",
        )

    history_df = load_history()

    if not history_df.empty and "Predicted Yield" in history_df.columns:
        st.markdown("### 🌾 Recent Yield Estimates")

        chart = px.line(
            history_df.reset_index(),
            x="index",
            y="Predicted Yield",
            markers=True,
            title="Prediction History",
            labels={
                "index": "Prediction Number",
                "Predicted Yield": "Predicted Yield",
            },
        )
        chart.update_layout(template="plotly_white")
        st.plotly_chart(chart, use_container_width=True)

    st.info(
        "Model metrics should be calculated on comparable held-out test data. "
        "A quantum model is not automatically more accurate than a classical model."
    )

    show_footer()


# ============================================================
# 🗂️ PAGE 3 — PREDICTION HISTORY
# ============================================================

elif page == "🗂️ Prediction History":

    st.markdown("""
    <div class="hero">
        <h1>🗂️ Prediction History</h1>
        <p>Review and export predictions saved by this dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    history_df = load_history()

    if history_df.empty:
        st.info(
            "No prediction history is available yet. "
            "Run a successful prediction to add an entry."
        )
    else:
        st.metric("📌 Saved Predictions", len(history_df))

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Export Prediction History",
            data=history_df.to_csv(index=False).encode("utf-8"),
            file_name="nexora_prediction_history.csv",
            mime="text/csv",
        )

        if st.button("🗑️ Clear Session History"):
            try:
                HISTORY_FILE.unlink(missing_ok=True)
                st.success("Prediction history file cleared.")
                st.rerun()
            except OSError as error:
                st.error(f"Could not clear history: {error}")

    show_footer()


# ============================================================
# ℹ️ PAGE 4 — ABOUT NEXORA
# ============================================================

elif page == "ℹ️ About NEXORA":

    st.markdown("""
    <div class="hero">
        <h1>🌱 About NEXORA</h1>
        <p>
            Exploring crop yield prediction through data,
            machine learning, and quantum computing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    NEXORA is a research prototype exploring crop yield prediction
    using agricultural input features and machine learning.

    Its dashboard brings together field measurements, prediction
    results, and model-evaluation information in one interface.
    """)

    st.markdown("### 🌍 Core Components")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>🌦️ Agricultural Inputs</h3>
            <p>
                Rainfall, temperature, soil moisture, and vegetation
                index can help describe field conditions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h3>📊 Model Evaluation</h3>
            <p>
                Comparison tables and charts help inspect model
                performance when evaluation data is available.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>🧠 Machine Learning</h3>
            <p>
                A prediction API connects the dashboard to the
                configured backend model.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h3>⚛️ Quantum Machine Learning</h3>
            <p>
                Quantum neural networks can be investigated and
                evaluated alongside classical baselines.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎯 Project Goal")

    st.success(
        "NEXORA aims to explore, evaluate, and communicate "
        "data-driven agricultural predictions responsibly."
    )

    st.warning(
        "Predictions are estimates, not guaranteed crop outcomes. "
        "Their reliability depends on the model, training data, "
        "and the units and format expected by the backend."
    )

    show_footer()
