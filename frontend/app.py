import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Crop Recommendation System", layout="centered")

# Language selection
language = st.radio("🌍 Select Language", ["English", "Hindi", "Telugu"])

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

# ---------------- TRANSLATION FUNCTION ----------------
def translate(text, lang):
    translations = {
        "English": {
            "High temperature": "High temperature suitable for warm-weather crops",
            "Low rainfall": "Low rainfall conditions detected",
            "High rainfall": "High rainfall suitable for water-loving crops",
            "Optimal pH": "Optimal soil pH level for crop growth",
            "Soil type": "Soil type supports balanced growth conditions"
        },
        "Hindi": {
            "High temperature": "उच्च तापमान गर्म मौसम की फसलों के लिए उपयुक्त है",
            "Low rainfall": "कम वर्षा की स्थिति पाई गई है",
            "High rainfall": "अधिक वर्षा पानी पसंद करने वाली फसलों के लिए उपयुक्त है",
            "Optimal pH": "मिट्टी का pH स्तर फसल के लिए उपयुक्त है",
            "Soil type": "मिट्टी का प्रकार संतुलित वृद्धि में सहायक है"
        },
        "Telugu": {
            "High temperature": "అధిక ఉష్ణోగ్రత వేడి వాతావరణ పంటలకు అనుకూలం",
            "Low rainfall": "తక్కువ వర్షపాతం పరిస్థితులు గుర్తించబడ్డాయి",
            "High rainfall": "అధిక వర్షపాతం నీటిని ఇష్టపడే పంటలకు అనుకూలం",
            "Optimal pH": "మట్టిలో pH స్థాయి పంట పెరుగుదలకు అనుకూలం",
            "Soil type": "మట్టి రకం సమతుల్య పెరుగుదలకు సహాయపడుతుంది"
        }
    }

    for key in translations.get(lang, {}):
        if key in text:
            return translations[lang][key]

    return text

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
        response = requests.post(
            "https://crop-recommendation-system-1-acdt.onrender.com/predict",
            json=data
        )

        

        if response.status_code != 200:
            st.error("API Error")
        else:
            result = response.json()

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
            if "explanation" in result and result["explanation"]:
                st.subheader("🧠 Why this crop?")

                for point in result["explanation"]:
                    st.write(f"✔ {translate(point, language)}")
            else:
                st.info("No explanation available")

            # ---------------- TOP 3 ----------------
            st.subheader("📌 Top 3 Predictions")

            for crop in result["top_predictions"]:
                st.write(f"🌱 {crop['crop']} — {crop['confidence'] * 100:.1f}%")

    except Exception as e:
        st.error(f"Connection Error: {e}")

    
    