function showCropForm() {
    document.getElementById("crop_inputs").classList.remove("hidden");
    document.getElementById("npk_inputs").classList.add("hidden");
    document.getElementById("location_based_inputs").classList.add("hidden");
}

function showNpkForm() {
    document.getElementById("npk_inputs").classList.remove("hidden");
    document.getElementById("crop_inputs").classList.add("hidden");
    document.getElementById("location_based_inputs").classList.add("hidden");
}

function showLocationBasedForm() {
    document.getElementById("location_based_inputs").classList.remove("hidden");
    document.getElementById("crop_inputs").classList.add("hidden");
    document.getElementById("npk_inputs").classList.add("hidden");
}

function predict(model) {
    const url = model === "crop" ? "/predict_crop" : "/predict_npk";

    let data = model === "crop" ? {
        nitrogen: document.getElementById("nitrogen").value,
        phosphorus: document.getElementById("phosphorus").value,
        potassium: document.getElementById("potassium").value,
        ph: document.getElementById("ph").value,
        humidity: document.getElementById("humidity").value
    } : {
        ph: document.getElementById("ph_npk").value,
        moisture: document.getElementById("moisture").value,
        temperature: document.getElementById("temperature").value
    };

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (model === "npk") {
            document.getElementById("predicted_nitrogen").value = data.Nitrogen;
            document.getElementById("predicted_phosphorus").value = data.Phosphorus;
            document.getElementById("predicted_potassium").value = data.Potassium;
        } 
        
        // Crop name to image mapping
        const cropImages = {
            "mothbeans": "/static/images/mothbeans.png",
            "wheat": "/static/images/wheat.png",
            "rice": "/static/images/rice.png",
            "maize": "/static/images/maize.png",
            "blackgram": "/static/images/blackgram.png",
            "mungbeans": "/static/images/mungbeans.png",
            "Soyabeans": "/static/images/Soyabeans.png",
        };

        const cropKey = data.crop ? data.crop.toLowerCase() : '';
        const cropImage = cropImages[cropKey] || "/static/images/default.png";  

        if (data.crop) {
            document.getElementById("predictionResult").innerHTML = `<div class="loading">🔄 Predicting...</div>`;
            document.getElementById("predictionResult").innerHTML = `
                <div class="crop-result">
                    <h3>🌱 Recommended Crop: <span>${data.crop}</span></h3>
                    <div class="crop-image">
                        <img src="${cropImage}" alt="${data.crop}">
                    </div>
                    <p class="explanation">${data.explanation || generateExplanation(data.crop)}</p>
                </div>`;
        }
    })
    .catch(error => console.error("Error:", error));
}

function predictPlant() {
    let nitrogen = document.getElementById("predicted_nitrogen").value;
    let phosphorus = document.getElementById("predicted_phosphorus").value;
    let potassium = document.getElementById("predicted_potassium").value;
    let ph = document.getElementById("ph_npk").value;
    let humidity = document.getElementById("moisture").value;

    let cropData = { nitrogen, phosphorus, potassium, ph, humidity };
    
    fetch("/predict_crop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cropData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("predictionResult").innerHTML = `
                <div class="error-message">❌ Error: ${data.error}</div>`;
        } else {
            // Crop name to image mapping
            const cropImages = {
                "mothbeans": "/static/images/mothbeans.png",
                "wheat": "/static/images/wheat.png",
                "rice": "/static/images/rice.png",
                "maize": "/static/images/maize.png",
                "blackgram": "/static/images/blackgram.png",
                "mungbeans": "/static/images/mungbeans.png",
                "Soyabeans": "/static/images/Soyabeans.png",
            };

            const cropKey = data.crop.toLowerCase();
            const cropImage = cropImages[cropKey] || "/static/images/default.png";

            document.getElementById("predictionResult").innerHTML = `<div class="loading">🔄 Predicting...</div>`;
            document.getElementById("predictionResult").innerHTML = `
                <div class="crop-result">
                    <h3>🌱 Recommended Crop: <span>${data.crop}</span></h3>
                    <div class="crop-image">
                        <img src="${cropImage}" alt="${data.crop}">
                    </div>
                    <p class="explanation">${data.explanation || generateExplanation(data.crop)}</p>
                </div>`;
        }
    });
}

function generateExplanation(crop) {
    return "The recommended crop is " + crop + ". This crop is well-suited for the detected soil conditions, ensuring optimal growth and yield.";
}

// Location-Based Prediction Functions
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    document.getElementById("latitude").value = position.coords.latitude;
    document.getElementById("longitude").value = position.coords.longitude;
}

function showError(error) {
    alert("Error fetching location. Please enter manually.");
}

function enableManualInput() {
    document.getElementById("latitude").removeAttribute("readonly");
    document.getElementById("longitude").removeAttribute("readonly");
}

function predictCrop() {
    let lat = document.getElementById("latitude").value;
    let lon = document.getElementById("longitude").value;

    fetch('/predict_location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `latitude=${lat}&longitude=${lon}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("predictionResult").innerHTML = `
                <div class="location-result">
                    <h3>🌱 Recommended Crop: <span>${data.recommended_crop}</span></h3>
                    <div class="weather-info">
                        <div class="weather-item">
                            <span class="weather-icon">🌡️</span>
                            <p><b>Temperature:</b> ${data.temperature}°C</p>
                        </div>
                        <div class="weather-item">
                            <span class="weather-icon">💧</span>
                            <p><b>Humidity:</b> ${data.humidity}%</p>
                        </div>
                    </div>
                </div>`;
        }
    })
    .catch(error => console.error("Error:", error));
}

// Fetch sensor data
function fetchSensorData() {
    fetch('/get_sensor_data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ph_npk').value = data.ph;
            document.getElementById('moisture').value = data.moisture;
            document.getElementById('temperature').value = data.temperature;
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
        });
}
document.getElementById("predictionResult").innerHTML = `<div class="loading">🔄 Predicting...</div>`;

