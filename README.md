# interactiondesign
queue management system with database functionality
# Queue Update System

A Python Flask application for managing queue updates with photo uploads and database storage.

## Features

- Submit queue updates (location, queue length, waiting time, photo)
- Store all data in SQLite database
- Upload photos (file upload or base64)
- Retrieve updates with filters
- Archive/delete updates
- View statistics
- Simple web interface for testing

## Database Schema

**QueueUpdate Table:**
- id (Integer, Primary Key)
- location (String) - e.g., "Yangon Petrol Station"
- queue_length (String) - "Short", "Medium", or "Long"
- waiting_time (String) - e.g., "10:30 AM" or "15 minutes"
- photo_path (String) - path to uploaded photo
- timestamp (DateTime) - auto-generated
- status (String) - "active" or "archived"

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Upload Update (File Upload)
```
POST /api/upload
Content-Type: multipart/form-data

Form Data:
- location: string
- queue_length: string (Short/Medium/Long)
- waiting_time: string (optional)
- photo: file (optional)
```

### 2. Upload Update (Base64)
```
POST /api/upload-base64
Content-Type: application/json

Body:
{
  "location": "Yangon Petrol Station",
  "queue_length": "Medium",
  "waiting_time": "10:30 AM",
  "photo": "base64_encoded_string",
  "photo_name": "image.jpg"
}
```

### 3. Get All Updates
```
GET /api/updates?location=xxx&status=active&limit=50
```

### 4. Get Single Update
```
GET /api/updates/<id>
```

### 5. Archive Update
```
PUT /api/updates/<id>/archive
```

### 6. Delete Update
```
DELETE /api/updates/<id>
```

### 7. Get All Locations
```
GET /api/locations
```

### 8. Get Statistics
```
GET /api/stats
```

### 9. Get Photo
```
GET /api/photo/<filename>
```

## Usage Examples

### Python (using requests)

```python
import requests

# Upload update
data = {
    'location': 'Yangon Petrol Station',
    'queue_length': 'Medium',
    'waiting_time': '10:30 AM'
}
files = {'photo': open('image.jpg', 'rb')}
response = requests.post('http://localhost:5000/api/upload', data=data, files=files)
print(response.json())

# Get all updates
response = requests.get('http://localhost:5000/api/updates')
print(response.json())

# Get specific location
response = requests.get('http://localhost:5000/api/updates?location=Yangon Petrol Station')
print(response.json())
```

### JavaScript (fetch API)

```javascript
// Upload update
const formData = new FormData();
formData.append('location', 'Yangon Petrol Station');
formData.append('queue_length', 'Medium');
formData.append('waiting_time', '10:30 AM');
formData.append('photo', photoFile);

fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));

// Get updates
fetch('http://localhost:5000/api/updates')
  .then(r => r.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Upload update
curl -X POST http://localhost:5000/api/upload \
  -F "location=Yangon Petrol Station" \
  -F "queue_length=Medium" \
  -F "waiting_time=10:30 AM" \
  -F "photo=@image.jpg"

# Get all updates
curl http://localhost:5000/api/updates

# Get by location
curl "http://localhost:5000/api/updates?location=Yangon%20Petrol%20Station"

# Get statistics
curl http://localhost:5000/api/stats
```

## Testing

Run the test script to verify all endpoints:

```bash
# Start the server first
python app.py

# In another terminal, run tests
python test_api.py
```

## Web Interface

Access the basic web interface at `http://localhost:5000/` to:
- Submit updates via form
- View recent updates
- Test the system without writing code

## File Structure

```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── test_api.py            # API test suite
├── README.md              # This file
├── queue_updates.db       # SQLite database (created on first run)
└── uploads/               # Uploaded photos directory (created on first run)
```

## Database Operations

The SQLite database is created automatically on first run. You can inspect it using:

```bash
sqlite3 queue_updates.db

# SQL commands:
SELECT * FROM queue_updates;
SELECT * FROM queue_updates WHERE location = 'Yangon Petrol Station';
SELECT COUNT(*) FROM queue_updates;
```

## Notes

- Photos are stored in the `uploads/` directory
- Database file: `queue_updates.db`
- Max file upload size: 16MB
- All timestamps are in UTC
- CORS is enabled for cross-origin requests
