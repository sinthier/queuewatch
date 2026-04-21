import sqlite3
from datetime import datetime
import os

DB_PATH = 'queue_updates.db'

def create_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_update(location, queue_length, waiting_time=None, photo_path=None):
    """Insert a new queue update directly into database"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO queue_updates (location, queue_length, waiting_time, photo_path, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (location, queue_length, waiting_time, photo_path, datetime.utcnow(), 'active'))
    
    conn.commit()
    update_id = cursor.lastrowid
    conn.close()
    
    print(f"✓ Inserted update with ID: {update_id}")
    return update_id

def get_all_updates():
    """Retrieve all updates from database"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM queue_updates ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"\nTotal updates: {len(rows)}\n")
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"  Location: {row['location']}")
        print(f"  Queue: {row['queue_length']}")
        print(f"  Wait: {row['waiting_time']}")
        print(f"  Photo: {row['photo_path']}")
        print(f"  Time: {row['timestamp']}")
        print(f"  Status: {row['status']}")
        print("-" * 50)
    
    return [dict(row) for row in rows]

def get_updates_by_location(location):
    """Get updates for a specific location"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM queue_updates WHERE location = ? ORDER BY timestamp DESC', (location,))
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"\nUpdates for '{location}': {len(rows)}\n")
    for row in rows:
        print(f"ID: {row['id']} | Queue: {row['queue_length']} | Time: {row['timestamp']}")
    
    return [dict(row) for row in rows]

def get_update_by_id(update_id):
    """Get a specific update by ID"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM queue_updates WHERE id = ?', (update_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        print(f"\nUpdate ID: {row['id']}")
        print(f"Location: {row['location']}")
        print(f"Queue Length: {row['queue_length']}")
        print(f"Waiting Time: {row['waiting_time']}")
        print(f"Photo: {row['photo_path']}")
        print(f"Timestamp: {row['timestamp']}")
        print(f"Status: {row['status']}")
        return dict(row)
    else:
        print(f"Update with ID {update_id} not found")
        return None

def update_status(update_id, new_status):
    """Update the status of an update"""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE queue_updates SET status = ? WHERE id = ?', (new_status, update_id))
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"✓ Updated status for ID {update_id} to '{new_status}'")
    else:
        print(f"✗ No update found with ID {update_id}")
    
    conn.close()

def delete_update(update_id):
    """Delete an update from database"""
    conn = create_connection()
    cursor = conn.cursor()
    
    # First get photo path to delete file
    cursor.execute('SELECT photo_path FROM queue_updates WHERE id = ?', (update_id,))
    row = cursor.fetchone()
    
    if row and row['photo_path'] and os.path.exists(row['photo_path']):
        os.remove(row['photo_path'])
        print(f"✓ Deleted photo file: {row['photo_path']}")
    
    cursor.execute('DELETE FROM queue_updates WHERE id = ?', (update_id,))
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"✓ Deleted update with ID {update_id}")
    else:
        print(f"✗ No update found with ID {update_id}")
    
    conn.close()

def get_statistics():
    """Get database statistics"""
    conn = create_connection()
    cursor = conn.cursor()
    
    # Total updates
    cursor.execute('SELECT COUNT(*) as total FROM queue_updates')
    total = cursor.fetchone()['total']
    
    # Active updates
    cursor.execute('SELECT COUNT(*) as active FROM queue_updates WHERE status = "active"')
    active = cursor.fetchone()['active']
    
    # Archived updates
    cursor.execute('SELECT COUNT(*) as archived FROM queue_updates WHERE status = "archived"')
    archived = cursor.fetchone()['archived']
    
    # By queue length
    cursor.execute('SELECT queue_length, COUNT(*) as count FROM queue_updates GROUP BY queue_length')
    by_queue = cursor.fetchall()
    
    # By location
    cursor.execute('SELECT location, COUNT(*) as count FROM queue_updates GROUP BY location ORDER BY count DESC')
    by_location = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total Updates: {total}")
    print(f"Active: {active}")
    print(f"Archived: {archived}")
    print("\nBy Queue Length:")
    for row in by_queue:
        print(f"  {row['queue_length']}: {row['count']}")
    print("\nBy Location:")
    for row in by_location:
        print(f"  {row['location']}: {row['count']}")
    print("=" * 50)

def clear_all_data():
    """WARNING: Delete all data from database"""
    response = input("Are you sure you want to delete ALL data? (yes/no): ")
    if response.lower() == 'yes':
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM queue_updates')
        conn.commit()
        deleted = cursor.rowcount
        
        conn.close()
        
        # Delete all photos
        if os.path.exists('uploads'):
            for file in os.listdir('uploads'):
                os.remove(os.path.join('uploads', file))
        
        print(f"✓ Deleted {deleted} updates and all photos")
    else:
        print("Cancelled")

if __name__ == "__main__":
    print("=" * 50)
    print("Queue Update System - Database Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Insert new update")
        print("2. View all updates")
        print("3. View updates by location")
        print("4. View specific update")
        print("5. Archive update")
        print("6. Delete update")
        print("7. Show statistics")
        print("8. Clear all data")
        print("9. Exit")
        
        choice = input("\nEnter choice: ")
        
        if choice == '1':
            location = input("Location: ")
            print("Queue length: 1=Short, 2=Medium, 3=Long")
            ql = input("Enter (1/2/3): ")
            queue_map = {'1': 'Short', '2': 'Medium', '3': 'Long'}
            queue_length = queue_map.get(ql, 'Medium')
            waiting_time = input("Waiting time (optional): ")
            photo_path = input("Photo path (optional): ")
            
            insert_update(location, queue_length, waiting_time or None, photo_path or None)
        
        elif choice == '2':
            get_all_updates()
        
        elif choice == '3':
            location = input("Enter location: ")
            get_updates_by_location(location)
        
        elif choice == '4':
            update_id = int(input("Enter update ID: "))
            get_update_by_id(update_id)
        
        elif choice == '5':
            update_id = int(input("Enter update ID to archive: "))
            update_status(update_id, 'archived')
        
        elif choice == '6':
            update_id = int(input("Enter update ID to delete: "))
            delete_update(update_id)
        
        elif choice == '7':
            get_statistics()
        
        elif choice == '8':
            clear_all_data()
        
        elif choice == '9':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")
