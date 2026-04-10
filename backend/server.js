require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const mongoose = require('mongoose');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/kanpur_trafficdb";

app.use(cors());
app.use(express.json());

// Serve static files from the React app build folder
app.use(express.static(path.join(__dirname, '../frontend/build')));

mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('[PROD] Connected to MongoDB.'))
    .catch(err => console.error('[ERROR] MongoDB connection error:', err));

const TrafficPatternSchema = new mongoose.Schema({ locality_name: String }, { collection: 'traffic_patterns' });
const TrafficPattern = mongoose.model('TrafficPattern', TrafficPatternSchema, 'traffic_patterns');

const COORDS_CACHE = {};

async function getCoordinates(locality) {
    if (COORDS_CACHE[locality]) return COORDS_CACHE[locality];
    try {
        const geoUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(locality + ', Kanpur, Uttar Pradesh')}&format=json&limit=1`;
        const response = await axios.get(geoUrl, { headers: { 'User-Agent': 'KanpurTrafficDeploy/1.0' } });
        if (response.data && response.data.length > 0) {
            const coords = { lat: parseFloat(response.data[0].lat), lng: parseFloat(response.data[0].lon) };
            COORDS_CACHE[locality] = coords;
            return coords;
        }
    } catch (err) { console.error(`Geocoding error: ${locality}`); }
    return null;
}

app.post('/api/predict', async (req, res) => {
    const { origin, destination, day_type, time_slot, weather } = req.body;
    
    const startCoords = await getCoordinates(origin);
    const endCoords = await getCoordinates(destination);

    let distanceKm = "5.0"; 
    let baseDurationMin = 10;

    if (startCoords && endCoords) {
        try {
            const osrmUrl = `http://router.project-osrm.org/route/v1/driving/${startCoords.lng},${startCoords.lat};${endCoords.lng},${endCoords.lat}?overview=false`;
            const osrmRes = await axios.get(osrmUrl);
            if (osrmRes.data.routes && osrmRes.data.routes[0]) {
                distanceKm = (osrmRes.data.routes[0].distance / 1000).toFixed(2);
                baseDurationMin = Math.round(osrmRes.data.routes[0].duration / 60);
            }
        } catch (err) { console.error("OSRM Error"); }
    }

    const pythonPath = process.env.PYTHON_PATH || 'python';
    const pythonProcess = spawn(pythonPath, [
        path.join(__dirname, './predict.py'),
        origin, day_type, time_slot, weather
    ]);

    let pythonData = "";
    pythonProcess.stdout.on('data', (data) => pythonData += data.toString());

    pythonProcess.on('close', (code) => {
        try {
            const mlResult = JSON.parse(pythonData.trim());
            const speed = mlResult.predicted_speed_kmh;
            const multiplier = Math.max(1, (25 / Math.max(speed, 5))); 
            const finalTime = Math.round(baseDurationMin * multiplier);

            res.json({
                ml_prediction: mlResult,
                actual_distance: `${distanceKm} km`,
                actual_time: `${finalTime} mins`,
                route_status: speed < 15 ? "Heavy Traffic" : (speed < 25 ? "Moderate" : "Smooth")
            });
        } catch (e) {
            if (!res.headersSent) res.status(500).json({ error: "Prediction error" });
        }
    });
});

app.get('/api/localities', async (req, res) => {
    try {
        const locs = await TrafficPattern.distinct('locality_name');
        res.json(locs.filter(l => l).sort());
    } catch { res.status(500).json([]); }
});

// The catch-all handler: for any request that doesn't match one above, send back React's index.html file.
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build', 'index.html'));
});

app.listen(PORT, () => console.log(`Backend optimized for deployment on port ${PORT}`));