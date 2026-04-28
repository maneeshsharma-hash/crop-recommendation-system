from fastapi import FastAPI
import pickle
import numpy as np
from utils.weather import get_weather
from typing import Optional

app = FastAPI()

# Load model
with open("model/crop_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.get("/")
def home():
    return {"message": "Crop Recommendation API is running"}
from pydantic import BaseModel

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    ph: float
    city: str
    soil_type: Optional[str] = None

def soil_to_npk(soil):
    if soil == "Sandy":
        return 40, 40, 40
    elif soil == "Clay":
        return 60, 60, 60
    elif soil == "Black":
        return 50, 50, 50
    elif soil == "Red":
        return 30, 30, 30
    else:
        return 45, 45, 45
yield_data = {
    "rice": "3-6 tons/hectare",
    "wheat": "2-5 tons/hectare",
    "maize": "4-7 tons/hectare",
    "cotton": "1-2 tons/hectare",
    "jute": "2-3 tons/hectare",
    "coffee": "0.8-1.5 tons/hectare",
    "coconut": "100-150 nuts/tree/year",
    "banana": "30-50 tons/hectare",
    "apple": "10-20 tons/hectare",
    "mango": "8-12 tons/hectare",
    "grapes": "15-25 tons/hectare",
    "watermelon": "20-30 tons/hectare",
    "muskmelon": "15-20 tons/hectare",
    "orange": "10-15 tons/hectare",
    "papaya": "40-60 tons/hectare",
    "pomegranate": "10-15 tons/hectare",
    "mungbean": "0.5-1 ton/hectare",
    "blackgram": "0.5-1 ton/hectare",
    "lentil": "0.8-1.5 tons/hectare",
    "pigeonpeas": "1-2 tons/hectare",
    "mothbeans": "0.4-0.8 tons/hectare",
    "chickpea": "1-2 tons/hectare",
    "kidneybeans": "1-2 tons/hectare",
    "millet": "1-2 tons/hectare",
    "sorghum": "2-4 tons/hectare",
    "soybean": "2-3 tons/hectare",
    "sunflower": "1-2 tons/hectare",
    "groundnut": "2-3 tons/hectare",
    "mustard": "1-2 tons/hectare",
    "sugarcane": "60-100 tons/hectare",
    "tea": "1.5-3 tons/hectare"
}
price_data = {
    "rice": "₹2000-2500/quintal",
    "wheat": "₹2100-2500/quintal",
    "maize": "₹1800-2200/quintal",
    "cotton": "₹6000-7000/quintal",
    "jute": "₹4000-5000/quintal",
    "coffee": "₹8000-12000/quintal",
    "coconut": "₹20-30/nut",
    "banana": "₹10-20/kg",
    "apple": "₹100-200/kg",
    "mango": "₹50-150/kg",
    "grapes": "₹40-80/kg",
    "watermelon": "₹10-20/kg",
    "muskmelon": "₹20-40/kg",
    "orange": "₹40-80/kg",
    "papaya": "₹20-40/kg",
    "pomegranate": "₹80-150/kg",
    "mungbean": "₹6000-7000/quintal",
    "blackgram": "₹6000-8000/quintal",
    "lentil": "₹5000-7000/quintal",
    "pigeonpeas": "₹7000-8000/quintal",
    "mothbeans": "₹5000-6000/quintal",
    "chickpea": "₹5000-6000/quintal",
    "kidneybeans": "₹6000-8000/quintal",
    "millet": "₹2000-3000/quintal",
    "sorghum": "₹2000-3000/quintal",
    "soybean": "₹4000-5000/quintal",
    "sunflower": "₹5000-6000/quintal",
    "groundnut": "₹5000-6000/quintal",
    "mustard": "₹5000-7000/quintal",
    "sugarcane": "₹300-350/quintal",
    "tea": "₹150-300/kg"
}
@app.post("/predict")
def predict(data: CropInput):
    try:
        # 🌦️ Get weather data
        weather = get_weather(data.city)

        if weather is None:
            return {"error": "Weather data not available. Check API key or city."}

        # 🌱 Soil handling (if provided)
        if data.soil_type:
            N, P, K = soil_to_npk(data.soil_type)
        else:
            N, P, K = data.N, data.P, data.K

        # 📊 Feature array for model
        features = np.array([
            N,
            P,
            K,
            weather["temperature"],
            weather["humidity"],
            data.ph,
            weather["rainfall"]
        ]).reshape(1, -1)

        # 🤖 Prediction probabilities
        probabilities = model.predict_proba(features)[0]
        classes = model.classes_

        # 🔝 Top 3 crops
        top_indices = np.argsort(probabilities)[-3:][::-1]

        results = []
        for i in top_indices:
            results.append({
                "crop": classes[i],
                "confidence": round(float(probabilities[i]), 2)
            })

        top_crop = results[0]
        alternate_crop = results[1]

        # 🧠 Explanation generator
        def generate_explanation(crop, weather, data):
            explanation = []

            if weather["temperature"] > 30:
                explanation.append("✔ High temperature suitable for warm-weather crops")

            if weather["temperature"] < 20:
                explanation.append("✔ Cool temperature suitable for cool-season crops")

            if weather["rainfall"] < 10:
                explanation.append("✔ Low rainfall conditions detected")

            if weather["rainfall"] > 100:
                explanation.append("✔ High rainfall suitable for water-loving crops")

            if 6 <= data.ph <= 7.5:
                explanation.append("✔ Optimal soil pH level for crop growth")

            if data.soil_type:
                explanation.append(f"✔ Soil type '{data.soil_type}' supports balanced growth conditions")

            return explanation

        # 📦 Final response
        response = {
            "top_predictions": results,
            "primary_crop": top_crop["crop"],
            "confidence": top_crop["confidence"],
            "yield": yield_data.get(top_crop["crop"], "Data not available"),
            "price": price_data.get(top_crop["crop"], "Data not available"),
            "alternative_crop": alternate_crop["crop"],
            "explanation": generate_explanation(top_crop["crop"], weather, data)
        }

        return response

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}
