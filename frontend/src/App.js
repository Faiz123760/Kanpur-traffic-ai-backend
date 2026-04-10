import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Container, Row, Col, Form, Badge, Spinner } from 'react-bootstrap';
import './App.css';
import mapImage from './assets/map.jpg';
import backgroundVideo from './assets/Background Display.mp4';

const weekdaySlots = ['late_night_11pm_6am', 'morning_rush_8am_11am', 'mid_day_11am_4pm', 'evening_rush_5pm_9pm'];
const weekendSlots = ['morning_8am_12pm', 'afternoon_12pm_5pm', 'evening_5pm_10pm'];
const weatherOptions = ['clear', 'rainy', 'foggy', 'cloudy'];

function App() {
    const [localities, setLocalities] = useState([]);
    const [formData, setFormData] = useState({ origin: '', destination: '', day_type: 'weekday', time_slot: '', weather: 'clear' });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        async function init() {
            try {
                const res = await axios.get('/api/localities');
                if (Array.isArray(res.data)) {
                    setLocalities(res.data);
                    if (res.data.length > 0) setFormData(p => ({ ...p, origin: res.data[0], destination: res.data[1] || res.data[0] }));
                }
            } catch (err) { console.error("Backend offline"); }
        }
        init();
        
        // Auto-detect time
        const day = new Date().getDay();
        const hour = new Date().getHours();
        const dayType = (day === 0 || day === 6) ? 'weekend' : 'weekday';
        let timeSlot = '';
        if (dayType === 'weekday') {
            if (hour >= 23 || hour < 8) timeSlot = weekdaySlots[0];
            else if (hour >= 8 && hour < 11) timeSlot = weekdaySlots[1];
            else if (hour >= 11 && hour < 17) timeSlot = weekdaySlots[2];
            else timeSlot = weekdaySlots[3];
        } else {
            if (hour >= 8 && hour < 12) timeSlot = weekendSlots[0];
            else if (hour >= 12 && hour < 17) timeSlot = weekendSlots[1];
            else timeSlot = weekendSlots[2];
        }
        setFormData(prev => ({ ...prev, day_type: dayType, time_slot: timeSlot || (dayType === 'weekday' ? weekdaySlots[1] : weekendSlots[0]) }));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(p => ({ ...p, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await axios.post('/api/predict', formData);
            setResult(res.data);
        } catch { console.error("API error"); }
        finally { setLoading(false); }
    };

    return (
        <div className="main-wrapper">
            <video playsInline autoPlay muted loop id="bg-video">
                <source src={backgroundVideo} type="video/mp4" />
            </video>
            <div className="overlay"></div>

            <Container className="py-2">
                <header className="app-header">
                    <div className="header-title">
                        <span role="img" aria-label="clock">🕒</span>
                        Smart Traffic Advisor (Kanpur)
                        <span role="img" aria-label="car">🚕</span>
                    </div>
                </header>

                <Row className="g-4">
                    <Col lg={6}>
                        <div className="custom-card shadow-lg">
                            <Form onSubmit={handleSubmit}>
                                <Form.Group className="mb-3">
                                    <div className="card-label">Source point</div>
                                    <Form.Select name="origin" className="form-input-custom" value={formData.origin} onChange={handleChange}>
                                        {localities.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                                    </Form.Select>
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <div className="card-label">Destination point</div>
                                    <Form.Select name="destination" className="form-input-custom" value={formData.destination} onChange={handleChange}>
                                        {localities.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                                    </Form.Select>
                                </Form.Group>

                                <Row className="mb-3 g-2">
                                    <Col xs={6}>
                                        <div className="card-label">Day Schedule</div>
                                        <Form.Select name="day_type" className="form-input-custom" value={formData.day_type} onChange={handleChange}>
                                            <option value="weekday">Weekday</option>
                                            <option value="weekend">Weekend</option>
                                        </Form.Select>
                                    </Col>
                                    <Col xs={6}>
                                        <div className="card-label">Weather</div>
                                        <Form.Select name="weather" className="form-input-custom" value={formData.weather} onChange={handleChange}>
                                            {weatherOptions.map(w => <option key={w} value={w}>{w}</option>)}
                                        </Form.Select>
                                    </Col>
                                </Row>

                                <Form.Group className="mb-4">
                                    <div className="card-label">Time Window</div>
                                    <Form.Select name="time_slot" className="form-input-custom" value={formData.time_slot} onChange={handleChange}>
                                        {(formData.day_type === 'weekday' ? weekdaySlots : weekendSlots).map(t => (
                                            <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>

                                <button type="submit" className="btn-predict shadow-sm" disabled={loading}>
                                    {loading ? <Spinner animation="border" size="sm" /> : 'Get Exact Distance & Time'}
                                </button>
                            </Form>
                        </div>
                    </Col>

                    <Col lg={6}>
                        <div className="custom-card p-0 overflow-hidden mb-4">
                            <div className="map-container">
                                <img src={mapImage} alt="Map" className="map-image" />
                                <div className="position-absolute translate-middle-x" style={{bottom: '20px', left: '50%'}}>
                                   <Badge bg="info" className="text-dark">Actual Road Trace Ready</Badge>
                                </div>
                            </div>
                        </div>

                        <Row className="g-3">
                            <Col xs={4}>
                                <div className="stat-box">
                                    <div className="stat-label">Actual Time</div>
                                    <div className="stat-value text-info">
                                        {result ? result.actual_time : '--'}
                                    </div>
                                    <div className="text-muted small">Road Path</div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="stat-box">
                                    <div className="stat-label">Actual Distance</div>
                                    <div className="stat-value">
                                        {result ? result.actual_distance : '--'}
                                    </div>
                                    <div className="text-muted small">By Road km</div>
                                </div>
                            </Col>
                            <Col xs={4}>
                                <div className="stat-box">
                                    <div className="stat-label">Condition</div>
                                    <div className="stat-value" style={{fontSize: '1rem', color: '#22c55e'}}>
                                        {result ? result.route_status : '--'}
                                    </div>
                                    <div className="text-muted small">AI Forecast</div>
                                </div>
                            </Col>
                        </Row>

                        {result && (
                            <div className="mt-4 p-3 bg-primary bg-opacity-10 border border-primary border-opacity-25 rounded-3">
                                <strong>AI Intelligence:</strong> The system has geocoded your localities and found an actual road distance of <strong>{result.actual_distance}</strong>. Your predicted travel time is <strong>{result.actual_time}</strong> based on current traffic flow.
                            </div>
                        )}
                    </Col>
                </Row>
            </Container>
        </div>
    );
}

export default App;