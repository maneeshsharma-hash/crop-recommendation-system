import streamlit as st
import requests

st.set_page_config(page_title="Crop Recommendation System", layout="centered")

st.title("🌱 Crop Recommendation System")
st.write("Enter soil and location details to get crop prediction")

# ---------------- SIDEBAR INPUTS ----------------
st.sidebar.header("🌾 Soil Inputs")

N = st.sidebar.slider("Nitrogen (N)", 0, 140, 50)
P = st.sidebar.slider("Phosphorus (P)", 0, 140, 50)
K = st.sidebar.slider("Potassium (K)", 0, 140, 50)
ph = st.sidebar.slider("pH Value", 0.0, 14.0, 6.5)

soil_type = st.sidebar.selectbox(
    "Soil Type",
    ["None", "Sandy", "Clay", "Black", "Red"]
)

city = st.sidebar.text_input("City")

# ---------------- BUTTON ----------------
if st.sidebar.button("🌾 Predict Crop"):

    data = {
        "N": N,
        "P": P,
        "K": K,
        "ph": ph,
        "city": city,
        "soil_type": None if soil_type == "None" else soil_type
    }

    try:
        response = requests.post("http://127.0.0.1:8000/predict", json=data)
        result = response.json()

        if "error" in result:
            st.error(result["error"])

        else:
            # ---------------- PRIMARY RESULT ----------------
            st.success(f"🌾 Recommended Crop: {result['primary_crop']}")

            st.metric("📊 Confidence", f"{result['confidence'] * 100:.2f}%")

            # ---------------- CARDS ----------------
            col1, col2 = st.columns(2)

            with col1:
                st.info(f"🌱 Expected Yield\n\n{result['yield']}")

            with col2:
                st.info(f"💰 Market Price\n\n{result['price']}")

            # ---------------- ALTERNATIVE ----------------
            if "alternative_crop" in result:
                st.warning(f"🔁 Alternative Crop: {result['alternative_crop']}")

            # ---------------- EXPLANATION ----------------
            if "explanation" in result:
                st.subheader("🧠 Why this crop?")

                for point in result["explanation"]:
                    st.write(f"✔ {point}")

            # ---------------- TOP 3 ----------------
            st.subheader("📌 Top 3 Predictions")

            for crop in result["top_predictions"]:
                st.write(f"🌱 {crop['crop']} — {crop['confidence'] * 100:.1f}%")

    except Exception as e:
        st.error(f"Connection Error: {e}")