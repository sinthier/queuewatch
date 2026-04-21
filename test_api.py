"""
Test script to demonstrate database operations
Run this after starting the Flask app to test the API
"""

import requests
import json
import base64

BASE_URL = "http://localhost:5000"

def test_upload_with_file():
    """Test uploading with actual file"""
    print("\n1. Testing upload with file...")
    
    # You can create a dummy image or use an existing one
    files = {'photo': open('test_image.jpg', 'rb')} if False else {}
    
    data = {
        'location': 'Yangon Petrol Station',
        'queue_length': 'Medium',
        'waiting_time': '10:30 AM'
    }
    
    response = requests.post(f"{BASE_URL}/api/upload", data=data, files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_upload_base64():
    """Test uploading with base64 encoded image"""
    print("\n2. Testing upload with base64...")
    
    # Create a small dummy image (1x1 red pixel PNG)
    dummy_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    
    data = {
        'location': 'Downtown Station',
        'queue_length': 'Short',
        'waiting_time': '5 minutes',
        'photo': dummy_image_base64,
        'photo_name': 'test.png'
    }
    
    response = requests.post(
        f"{BASE_URL}/api/upload-base64",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_get_all_updates():
    """Get all updates"""
    print("\n3. Getting all updates...")
    
    response = requests.get(f"{BASE_URL}/api/updates")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total updates: {data['count']}")
    for update in data['data']:
        print(f"  - ID: {update['id']}, Location: {update['location']}, Queue: {update['queue_length']}")
    return data

def test_get_by_location():
    """Get updates filtered by location"""
    print("\n4. Getting updates for 'Yangon Petrol Station'...")
    
    response = requests.get(f"{BASE_URL}/api/updates?location=Yangon Petrol Station")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Count: {data['count']}")
    return data

def test_get_single_update(update_id):
    """Get a single update by ID"""
    print(f"\n5. Getting update with ID {update_id}...")
    
    response = requests.get(f"{BASE_URL}/api/updates/{update_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_archive_update(update_id):
    """Archive an update"""
    print(f"\n6. Archiving update {update_id}...")
    
    response = requests.put(f"{BASE_URL}/api/updates/{update_id}/archive")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_get_locations():
    """Get all unique locations"""
    print("\n7. Getting all locations...")
    
    response = requests.get(f"{BASE_URL}/api/locations")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Locations: {data['data']}")
    return data

def test_get_stats():
    """Get statistics"""
    print("\n8. Getting statistics...")
    
    response = requests.get(f"{BASE_URL}/api/stats")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Stats: {json.dumps(data, indent=2)}")
    return data

def test_delete_update(update_id):
    """Delete an update"""
    print(f"\n9. Deleting update {update_id}...")
    
    response = requests.delete(f"{BASE_URL}/api/updates/{update_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

if __name__ == "__main__":
    print("=" * 50)
    print("Queue Update System - API Test Suite")
    print("=" * 50)
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Test uploads
        result1 = test_upload_with_file()
        result2 = test_upload_base64()
        
        # Get all updates
        all_updates = test_get_all_updates()
        
        # Test with first update if available
        if all_updates['data']:
            first_id = all_updates['data'][0]['id']
            
            # Get single update
            test_get_single_update(first_id)
            
            # Get by location
            test_get_by_location()
            
            # Archive update
            test_archive_update(first_id)
            
            # Get locations
            test_get_locations()
            
            # Get stats
            test_get_stats()
            
            # Optionally delete (commented out by default)
            # test_delete_update(first_id)
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to the server.")
        print("Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
