
import requests

API_KEY = "172959eb31d12ccf3e80642a5931d8ed"   # 👈 put your real key here

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            print("API Error:", data)
            return None

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0)
        }

    except Exception as e:
        print("Weather function error:", e)
        return None