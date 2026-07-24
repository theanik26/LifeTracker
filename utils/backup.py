import os
import json
import shutil
from datetime import datetime
from database.connection import db
from models.log import DailyLog

def export_json_backup():
    """
    Returns all logs in a formatted JSON string for backup.
    """
    logs = DailyLog.query.order_by(DailyLog.date.asc()).all()
    backup_data = {
        'version': '1.0',
        'export_time': datetime.now().isoformat(),
        'logs': [log.to_dict() for log in logs]
    }
    return json.dumps(backup_data, indent=2)

def import_json_backup(json_string):
    """
    Parses a JSON backup and updates/inserts daily logs into SQLite.
    Returns a tuple (success_boolean, message_string, count_imported).
    """
    try:
        data = json.loads(json_string)
        if 'logs' not in data:
            return False, "Invalid backup format: missing logs array.", 0
            
        logs_list = data['logs']
        imported_count = 0
        
        for item in logs_list:
            # Parse date
            try:
                log_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
            except ValueError:
                continue # Skip invalid date format
                
            # Check if record already exists
            log = DailyLog.query.filter_by(date=log_date).first()
            
            score = 0
            # Calculate score safely from keys
            q1 = bool(item.get('q1_val', False))
            q2 = bool(item.get('q2_val', False))
            q3 = bool(item.get('q3_val', False))
            q4 = bool(item.get('q4_val', False))
            q5 = bool(item.get('q5_val', False))
            
            score = sum([q1, q2, q3, q4, q5])
            completed = (score == 5)
            
            if log:
                # Update existing record
                log.q1_val = q1
                log.q1_note = item.get('q1_note', '')
                log.q2_val = q2
                log.q2_note = item.get('q2_note', '')
                log.q3_val = q3
                log.q3_note = item.get('q3_note', '')
                log.q4_val = q4
                log.q4_note = item.get('q4_note', '')
                log.q5_val = q5
                log.q5_note = item.get('q5_note', '')
                log.score = score
                log.completed = completed
            else:
                # Insert new record
                new_log = DailyLog(
                    date=log_date,
                    q1_val=q1,
                    q1_note=item.get('q1_note', ''),
                    q2_val=q2,
                    q2_note=item.get('q2_note', ''),
                    q3_val=q3,
                    q3_note=item.get('q3_note', ''),
                    q4_val=q4,
                    q4_note=item.get('q4_note', ''),
                    q5_val=q5,
                    q5_note=item.get('q5_note', ''),
                    score=score,
                    completed=completed
                )
                db.session.add(new_log)
                
            imported_count += 1
            
        db.session.commit()
        return True, "Backup imported successfully.", imported_count
    except json.JSONDecodeError:
        return False, "File is not a valid JSON document.", 0
    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}", 0

def create_db_backup(db_filepath, backup_dir):
    """
    Copies the active SQLite database file to the backups folder with a timestamped name.
    """
    if not os.path.exists(db_filepath):
        return False, "Database file not found."
        
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"lifetrack_backup_{timestamp}.db"
    dest_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(db_filepath, dest_path)
        return True, f"Backup created successfully: {backup_filename}"
    except Exception as e:
        return False, f"Failed to copy database: {str(e)}"
