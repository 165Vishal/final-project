from flask import Flask, request, render_template, jsonify, send_from_directory
import joblib
import requests
import google.generativeai as genai

app = Flask(__name__, static_folder="static")

# Load ML models
crop_model = joblib.load('crop_model.pkl')
npk_model = joblib.load('npk_model.pkl')

# OpenWeather API Key (Replace with your actual key)
API_KEY = "f896e893c9f729ad8de02945b6590d07"

# Google AI Configuration
genai.configure(api_key="AIzaSyASoIm9nGSEo8TwSdaz1Z-Y8PQM-m7Lhdc")  # Replace with your actual API key

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Crop Prediction Function
def predict_crop(nitrogen, phosphorus, potassium, ph, humidity):
    input_features = [[nitrogen, phosphorus, potassium, ph, humidity]]

    try:
        predicted_crop = crop_model.predict(input_features)[0]
        print(f"Predicted Crop: {predicted_crop}")  # Debugging

        if not predicted_crop:
            return "Unknown", "The model couldn't determine the best crop for these conditions."

        # ✅ Improved AI-generated explanation
        prompt = (
            f"The best crop to grow in this soil is '{predicted_crop}'. "
            f"This soil has the following characteristics:\n"
            f"- Nitrogen: {nitrogen}\n"
            f"- Phosphorus: {phosphorus}\n"
            f"- Potassium: {potassium}\n"
            f"- pH Level: {ph}\n"
            f"- Humidity: {humidity}\n"
            "Explain why this crop is suitable for these conditions in simple terms."
        )

        try:
            model_name = "models/gemini-1.5-pro"  # Try "models/gemini-1.5-pro" if available
            ai_model = genai.GenerativeModel(model_name=model_name)
            response = ai_model.generate_content(prompt)

            explanation = response.text if hasattr(response, "text") else "No explanation available."

        except Exception as ai_error:
            print(f"AI Model Error: {ai_error}")
            explanation = "Could not generate an explanation due to AI model error."

        print(f"AI Explanation: {explanation}")  # ✅ Print explanation in terminal

        return predicted_crop, explanation
    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Error", f"An error occurred while predicting: {str(e)}"





# NPK Prediction Function
def predict_npk(ph, moisture, temperature):
    input_features = [[ph, moisture, temperature]]

    try:
        predicted_npk = npk_model.predict(input_features)[0]
        return {"Nitrogen": predicted_npk[0], "Phosphorus": predicted_npk[1], "Potassium": predicted_npk[2]}
    except Exception as e:
        print(f"NPK Prediction Error: {e}")
        return {"error": "NPK prediction failed"}

# Location-Based Crop Prediction Function
def predict_crop_by_location(lat, lon):
    try:
        # Fetch weather data from OpenWeather API
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(weather_url)
        
        if response.status_code != 200:
            return {"error": "Failed to fetch weather data", "details": response.text}

        data = response.json()

        # Extract necessary data
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        # Improved crop recommendation based on temperature & humidity
        recommended_crop = predict_crop_from_weather(temperature, humidity)

        return {"temperature": temperature, "humidity": humidity, "recommended_crop": recommended_crop}

    except Exception as e:
        return {"error": str(e)}

def predict_crop_from_weather(temperature, humidity):
    if temperature > 30:
        return "Maize"
    elif 20 <= temperature <= 30:
        return "Rice"
    else:
        return "Wheat"

@app.route("/get_latest_sensor_data", methods=["GET"])
def get_latest_sensor_data():
    return jsonify(sensor_data_store)

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", crop=None, explanation=None, npk_values=None)

@app.route("/predict_crop", methods=["POST"])
def predict_crop_route():
    data = request.json
    try:
        crop, explanation = predict_crop(
            float(data["nitrogen"]),
            float(data["phosphorus"]),
            float(data["potassium"]),
            float(data["ph"]),
            float(data["humidity"]),
        )
        print(f"Predicted Crop: {crop}")  # ✅ Debugging
        print(f"AI Explanation: {explanation}")  # ✅ Debugging

        return jsonify({"crop": crop, "explanation": explanation})  # ✅ Ensure explanation is sent
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)})


@app.route("/predict_npk", methods=["POST"])
def predict_npk_route():
    data = request.json
    try:
        npk_values = predict_npk(float(data["ph"]), float(data["moisture"]), float(data["temperature"]))
        return jsonify(npk_values)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)})

@app.route("/predict_location", methods=["POST"])
def predict_location():
    lat = request.form.get("latitude")
    lon = request.form.get("longitude")

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    result = predict_crop_by_location(lat, lon)
    return jsonify(result)

sensor_data_store = {"ph": 0, "moisture": 0, "temperature": 0}

@app.route("/send_sensor_data", methods=["POST"])
def receive_sensor_data():
    global sensor_data_store
    data = request.form if request.form else request.json  # Handle both form & JSON data
    try:
        sensor_data_store["ph"] = float(data["ph"])
        sensor_data_store["moisture"] = float(data["moisture"])
        sensor_data_store["temperature"] = float(data["temperature"])
        print(f"Received Data: {sensor_data_store}")
        return jsonify({"message": "Data stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/upload_sensor_data', methods=['POST'])
def upload_sensor_data():
    ph = request.form.get('ph')
    moisture = request.form.get('moisture')
    temperature = request.form.get('temperature')

    print(f"Received Sensor Data - pH: {ph}, Moisture: {moisture}, Temperature: {temperature}")

    # Optionally: Save to database, or pass to ML model here

    return jsonify({"status": "success", "message": "Data received"}), 200

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
