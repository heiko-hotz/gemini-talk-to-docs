# gemini-talk-to-docs

A web application that enables real-time interaction with Google's Gemini 2.0 model through multiple modalities:
- Voice input/output
- PDF document analysis
- Video feed integration

![App Demo](assets/screenshot.png)

## Features

- 🎤 Voice-based interaction with Gemini 2.0
- 📄 PDF document upload and analysis
- 🎥 Real-time video feed integration
- 🔒 Secure token-based authentication

## Prerequisites

- Python 3.7+
- Google Cloud Platform account
- Access to Gemini 2.0 API
- Valid GCP authentication token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gemini-talk-to-docs.git
cd gemini-talk-to-docs
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the WebSocket server:
```bash
python main.py
```

2. Start a local web server:
```bash
python -m http.server 8000
```

3. Open `http://localhost:8000` in your web browser

4. Enter your GCP access token and model ID

5. Connect to the model using the "Connect" button

6. You can now:
   - Upload PDF documents for analysis
   - Use voice commands (click the microphone button)
   - See yourself through the video feed
   - Receive audio responses from the model

## Configuration

The application uses the following default settings:
- WebSocket server runs on `localhost:8080`
- Web server runs on `localhost:8000`
- Uses Gemini 2.0 Flash model
- Audio sample rate: 16kHz for input, 24kHz for output
- Video feed maximum resolution: 640x480

## Architecture: WebSocket Proxy

This application implements a WebSocket proxy architecture between the client and Gemini's API for several key benefits:

1. **Security**: 
   - API keys and sensitive credentials remain secure on the server side
   - Prevents direct exposure of the Gemini API endpoint to clients
   - Enables proper token validation and rate limiting

2. **Performance**:
   - Maintains persistent connections for real-time streaming
   - Reduces latency for voice and video interactions
   - Enables efficient handling of large binary data (PDFs, video frames)

3. **Production Benefits**:
   - Easier deployment behind corporate firewalls
   - Centralized logging and monitoring
   - Ability to implement caching and request optimization
   - Simplified scaling and load balancing
   - Better control over API usage and costs

The proxy server (`main.py`) handles all communication between the web client and Gemini's API, making the application more secure and production-ready.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
