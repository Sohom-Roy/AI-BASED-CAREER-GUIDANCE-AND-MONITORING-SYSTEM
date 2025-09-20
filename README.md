# AI-Enhanced Career Guidance System

A comprehensive web application that provides AI-powered career recommendations using machine learning, real-time monitoring through ESP32 integration, and parent portal functionality.

## 🌟 Features

- **AI-Powered Career Recommendations**: Uses scikit-learn Decision Tree classifier for personalized career suggestions
- **NLP Interest Extraction**: Leverages spaCy for intelligent interest analysis
- **Real-time Monitoring**: ESP32 integration with MQTT for focus tracking
- **Parent Portal**: Monitor student progress and study habits
- **Modern UI**: Beautiful React frontend with responsive design
- **RESTful API**: Flask backend with comprehensive endpoints

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │   MQTT Broker   │
│   (Port 3000)   │◄──►│   (Port 5000)   │◄──►│  (Port 1883)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        │
                       ┌─────────────────┐             │
                       │  SQLite Database│             │
                       └─────────────────┘             │
                                                       │
                       ┌─────────────────┐             │
                       │     ESP32       │─────────────┘
                       │  (Focus Sensor) │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **MQTT Broker** (Mosquitto recommended)

### Installation

1. **Clone/Download the project**
   ```bash
   # The project structure is already set up
   cd "C:\Users\PALAS\OneDrive\Desktop\New folder (3)"
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **MQTT Broker Setup**
   
   **Windows:**
   ```bash
   # Download Mosquitto from https://mosquitto.org/download/
   # Or use chocolatey:
   choco install mosquitto
   
   # Start the broker
   mosquitto -v
   ```
   
   **macOS:**
   ```bash
   brew install mosquitto
   mosquitto -v
   ```
   
   **Linux:**
   ```bash
   sudo apt-get install mosquitto mosquitto-clients
   sudo systemctl start mosquitto
   ```

### Running the Application

1. **Start MQTT Broker** (in a separate terminal)
   ```bash
   mosquitto -v
   ```

2. **Start Backend** (in a separate terminal)
   ```bash
   cd backend
   python app.py
   ```
   Backend will be available at: http://localhost:5000

3. **Start Frontend** (in a separate terminal)
   ```bash
   cd frontend
   npm start
   ```
   Frontend will be available at: http://localhost:3000

## 📱 Usage

### For Students

1. **Register**: Visit http://localhost:3000 and fill out the registration form
2. **Get Recommendations**: Update your interests and scores to get AI-powered career suggestions
3. **View Roadmap**: See detailed career paths with skills, courses, and internships

### For Parents

1. **Access Parent Portal**: Use the link provided after student registration
2. **Monitor Progress**: View real-time focus data from ESP32 sensors
3. **Track Statistics**: See focus rates and study patterns

### ESP32 Integration

The system expects ESP32 to publish MQTT messages to:
- **Topic**: `monitor/{user_id}/focus`
- **Payload**: `"true"` (focused) or `"false"` (distracted)

Example ESP32 code snippet:
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// MQTT setup
const char* mqtt_server = "your_broker_ip";
const int mqtt_port = 1883;
const char* topic = "monitor/1/focus"; // Replace 1 with actual user_id

void publishFocusStatus(bool isFocused) {
  String payload = isFocused ? "true" : "false";
  client.publish(topic, payload.c_str());
}
```

## 🔧 API Endpoints

### Backend API (http://localhost:5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register a new user |
| POST | `/api/recommend` | Get career recommendations |
| GET | `/api/parent/<user_id>` | Get monitoring data for parent |
| GET | `/api/user/<user_id>` | Get user information |
| GET | `/api/health` | Health check |

### Example API Usage

**Register a user:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "interests": "coding, mathematics, problem solving",
    "skills": "Python, JavaScript, SQL",
    "scores": "Math:85,Science:90",
    "parent_email": "parent@example.com"
  }'
```

**Get recommendations:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "interests": "coding, artificial intelligence",
    "scores": "Math:90,Science:85"
  }'
```

## 🧪 Testing

### Manual Testing

1. **Test Registration**: Register a new user and verify database entry
2. **Test Recommendations**: Submit interests and scores, verify AI response
3. **Test MQTT**: Publish test messages to verify monitoring
4. **Test Parent Portal**: Access parent view and verify data display

### MQTT Testing

Use MQTT client tools to test the integration:

```bash
# Install MQTT client (if not already installed)
pip install paho-mqtt

# Test publishing focus data
mosquitto_pub -h localhost -t "monitor/1/focus" -m "true"
mosquitto_pub -h localhost -t "monitor/1/focus" -m "false"
```

## 🔍 Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **MQTT connection failed**
   - Ensure Mosquitto broker is running
   - Check firewall settings
   - Verify broker address and port

3. **CORS errors**
   - Ensure Flask-CORS is installed
   - Check that backend is running on port 5000

4. **Database errors**
   - Delete `users.db` file to reset database
   - Restart the backend application

### Logs and Debugging

- **Backend logs**: Check terminal where `python app.py` is running
- **Frontend logs**: Check browser console (F12)
- **MQTT logs**: Check Mosquitto broker output

## 🚀 Production Deployment

### Backend (Flask)
- Deploy to Heroku, AWS, or similar
- Use PostgreSQL instead of SQLite
- Set up proper environment variables
- Configure production MQTT broker

### Frontend (React)
- Deploy to Vercel, Netlify, or similar
- Update API endpoints to production URLs
- Configure build optimizations

### Database
- Migrate from SQLite to PostgreSQL/MySQL
- Set up database backups
- Configure connection pooling

## 📊 Machine Learning Model

The system uses a Decision Tree classifier trained on synthetic data. For production:

1. **Replace with real dataset** (e.g., from Kaggle)
2. **Implement more sophisticated models** (Random Forest, Neural Networks)
3. **Add feature engineering** for better predictions
4. **Implement model retraining** pipeline

## 🔒 Security Considerations

- Add user authentication (JWT tokens)
- Implement input validation and sanitization
- Use HTTPS in production
- Secure MQTT broker with authentication
- Add rate limiting to API endpoints

## 📈 Future Enhancements

- **Real-time notifications** for parents
- **Advanced analytics** and reporting
- **Mobile app** for students and parents
- **Integration with learning management systems**
- **Gamification** features for student engagement
- **Video analysis** for focus detection
- **Multi-language support**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue with detailed description
4. Include system information and error logs

---

**Built with ❤️ using Flask, React, scikit-learn, and MQTT**
