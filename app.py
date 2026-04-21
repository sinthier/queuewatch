from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///queue_updates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Model
class QueueUpdate(db.Model):
    __tablename__ = 'queue_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    queue_length = db.Column(db.String(20), nullable=False)  # 'Short', 'Medium', 'Long'
    waiting_time = db.Column(db.String(50), nullable=True)
    photo_path = db.Column(db.String(300), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'queue_length': self.queue_length,
            'waiting_time': self.waiting_time,
            'photo_path': self.photo_path,
            'photo_url': f'/api/photo/{os.path.basename(self.photo_path)}' if self.photo_path else None,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }

# Create database tables
with app.app_context():
    db.create_all()

# API Endpoints

@app.route('/api/upload', methods=['POST'])
def upload_update():
    """Upload a new queue update with photo"""
    try:
        location = request.form.get('location', 'Unknown Location')
        queue_length = request.form.get('queue_length')
        waiting_time = request.form.get('waiting_time')
        
        if not queue_length:
            return jsonify({'error': 'Queue length is required'}), 400
        
        # Handle photo upload
        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.filename}")
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
        
        # Create new queue update
        new_update = QueueUpdate(
            location=location,
            queue_length=queue_length,
            waiting_time=waiting_time,
            photo_path=photo_path
        )
        
        db.session.add(new_update)
        db.session.commit()
        
        return jsonify({
            'message': 'Update submitted successfully',
            'data': new_update.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-base64', methods=['POST'])
def upload_update_base64():
    """Upload update with base64 encoded photo"""
    try:
        data = request.get_json()
        
        location = data.get('location', 'Unknown Location')
        queue_length = data.get('queue_length')
        waiting_time = data.get('waiting_time')
        
        if not queue_length:
            return jsonify({'error': 'Queue length is required'}), 400
        
        # Handle base64 photo
        photo_path = None
        if 'photo' in data and data['photo']:
            photo_base64 = data['photo']
            photo_name = data.get('photo_name', 'image.jpg')
            
            if ',' in photo_base64:
                photo_base64 = photo_base64.split(',')[1]
            
            photo_data = base64.b64decode(photo_base64)
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo_name}")
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(photo_path, 'wb') as f:
                f.write(photo_data)
        
        new_update = QueueUpdate(
            location=location,
            queue_length=queue_length,
            waiting_time=waiting_time,
            photo_path=photo_path
        )
        
        db.session.add(new_update)
        db.session.commit()
        
        return jsonify({
            'message': 'Update submitted successfully',
            'data': new_update.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates', methods=['GET'])
def get_updates():
    """Get all queue updates with optional filters"""
    try:
        location = request.args.get('location')
        status = request.args.get('status', 'active')
        limit = request.args.get('limit', 50, type=int)
        
        query = QueueUpdate.query
        
        if location:
            query = query.filter_by(location=location)
        
        if status:
            query = query.filter_by(status=status)
        
        updates = query.order_by(QueueUpdate.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'count': len(updates),
            'data': [update.to_dict() for update in updates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates/<int:update_id>', methods=['GET'])
def get_update(update_id):
    """Get a specific update by ID"""
    try:
        update = QueueUpdate.query.get(update_id)
        if not update:
            return jsonify({'error': 'Update not found'}), 404
        
        return jsonify({'data': update.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates/<int:update_id>', methods=['DELETE'])
def delete_update(update_id):
    """Delete an update"""
    try:
        update = QueueUpdate.query.get(update_id)
        if not update:
            return jsonify({'error': 'Update not found'}), 404
        
        # Delete photo file if exists
        if update.photo_path and os.path.exists(update.photo_path):
            os.remove(update.photo_path)
        
        db.session.delete(update)
        db.session.commit()
        
        return jsonify({'message': 'Update deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates/<int:update_id>/archive', methods=['PUT'])
def archive_update(update_id):
    """Archive an update"""
    try:
        update = QueueUpdate.query.get(update_id)
        if not update:
            return jsonify({'error': 'Update not found'}), 404
        
        update.status = 'archived'
        db.session.commit()
        
        return jsonify({
            'message': 'Update archived successfully',
            'data': update.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/photo/<filename>')
def get_photo(filename):
    """Serve uploaded photos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all unique locations"""
    try:
        locations = db.session.query(QueueUpdate.location).distinct().all()
        return jsonify({
            'data': [loc[0] for loc in locations]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about queue updates"""
    try:
        total = QueueUpdate.query.count()
        active = QueueUpdate.query.filter_by(status='active').count()
        archived = QueueUpdate.query.filter_by(status='archived').count()
        
        queue_stats = db.session.query(
            QueueUpdate.queue_length,
            db.func.count(QueueUpdate.id)
        ).group_by(QueueUpdate.queue_length).all()
        
        return jsonify({
            'total_updates': total,
            'active_updates': active,
            'archived_updates': archived,
            'by_queue_length': {stat[0]: stat[1] for stat in queue_stats}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Basic HTML interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Queue System</title>
    </head>
    <body>
        <h1>Queue Update System</h1>
        
        <h2>Submit Update</h2>
        <form id="form">
            Location: <input type="text" id="location" value="Yangon Petrol Station"><br><br>
            Queue Length: 
            <select id="queue">
                <option value="Short">Short (1-10)</option>
                <option value="Medium">Medium (10-20)</option>
                <option value="Long">Long (20-30)</option>
            </select><br><br>
            Waiting Time: 
            <select id="hours">
                <option value="00">0 hours</option>
                <option value="01">1 hour</option>
                <option value="02">2 hours</option>
                <option value="03">3 hours</option>
                <option value="04">4 hours</option>
                <option value="05">5 hours</option>
                <option value="06">6 hours</option>
                <option value="07">7 hours</option>
                <option value="08">8 hours</option>
                <option value="09">9 hours</option>
                <option value="10">10 hours</option>
                <option value="11">11 hours</option>
                <option value="12">12 hours</option>
            </select>
            <select id="minutes">
                <option value="00">0 min</option>
                <option value="05">5 min</option>
                <option value="10">10 min</option>
                <option value="15">15 min</option>
                <option value="20">20 min</option>
                <option value="25">25 min</option>
                <option value="30">30 min</option>
                <option value="35">35 min</option>
                <option value="40">40 min</option>
                <option value="45">45 min</option>
                <option value="50">50 min</option>
                <option value="55">55 min</option>
            </select><br><br>
            Photo: <input type="file" id="photo"><br><br>
            <button type="submit">Submit</button>
        </form>
        
        <h2>Recent Updates</h2>
        <button onclick="load()">Refresh</button>
        <div id="list"></div>
        
        <script>
            document.getElementById('form').onsubmit = async (e) => {
                e.preventDefault();
                const fd = new FormData();
                fd.append('location', document.getElementById('location').value);
                fd.append('queue_length', document.getElementById('queue').value);
                fd.append('waiting_time', document.getElementById('hours').value + ':' + document.getElementById('minutes').value);
                const f = document.getElementById('photo').files[0];
                if (f) fd.append('photo', f);
                
                const r = await fetch('/api/upload', {method: 'POST', body: fd});
                const d = await r.json();
                alert(d.message);
                load();
            };
            
            async function load() {
                const r = await fetch('/api/updates?limit=10');
                const d = await r.json();
                document.getElementById('list').innerHTML = d.data.map(u => 
                    `<div style="border:1px solid #ccc; padding:10px; margin:10px 0">
                        <b>${u.location}</b> - ${u.queue_length}<br>
                        ${u.waiting_time ? 'Wait: ' + u.waiting_time + '<br>' : ''}
                        ${new Date(u.timestamp).toLocaleString()}<br>
                        ${u.photo_url ? '<img src="' + u.photo_url + '" width="200">' : ''}
                    </div>`
                ).join('');
            }
            
            load();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
