import os
import random
from io import BytesIO
from datetime import datetime, date, timedelta
from flask import Blueprint, jsonify, request, Response, send_file, current_app

from database.connection import db
from models.log import DailyLog
from utils.analytics import (
    get_dashboard_metrics, 
    get_rolling_30_days, 
    get_analytics_data, 
    generate_monthly_report
)
from utils.export import export_csv, export_excel, export_pdf
from utils.backup import export_json_backup, import_json_backup, create_db_backup

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/log-details/<date_str>', methods=['GET'])
def get_log_details(date_str):
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
    log = DailyLog.query.filter_by(date=query_date).first()
    if not log:
        return jsonify({
            'success': True,
            'logged': False,
            'date': date_str,
            'data': None
        })
        
    return jsonify({
        'success': True,
        'logged': True,
        'date': date_str,
        'data': log.to_dict()
    })

@api_bp.route('/api/submit-log', methods=['POST'])
def submit_log():
    data = request.get_json() or {}
    
    date_str = data.get('date')
    if date_str:
        try:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'}), 400
    else:
        log_date = date.today()
        
    # Read Qs
    q1_val = bool(data.get('q1_val', False))
    q1_note = data.get('q1_note', '').strip()
    
    q2_val = bool(data.get('q2_val', False))
    q2_note = data.get('q2_note', '').strip()
    
    q3_val = bool(data.get('q3_val', False))
    q3_note = data.get('q3_note', '').strip()
    
    q4_val = bool(data.get('q4_val', False))
    q4_note = data.get('q4_note', '').strip()
    
    q5_val = bool(data.get('q5_val', False))
    q5_note = data.get('q5_note', '').strip()
    
    # Calc stats
    score = sum([q1_val, q2_val, q3_val, q4_val, q5_val])
    completed = (score == 5)
    
    # Check if exists
    log = DailyLog.query.filter_by(date=log_date).first()
    
    try:
        if log:
            log.q1_val = q1_val
            log.q1_note = q1_note
            log.q2_val = q2_val
            log.q2_note = q2_note
            log.q3_val = q3_val
            log.q3_note = q3_note
            log.q4_val = q4_val
            log.q4_note = q4_note
            log.q5_val = q5_val
            log.q5_note = q5_note
            log.score = score
            log.completed = completed
        else:
            log = DailyLog(
                date=log_date,
                q1_val=q1_val,
                q1_note=q1_note,
                q2_val=q2_val,
                q2_note=q2_note,
                q3_val=q3_val,
                q3_note=q3_note,
                q4_val=q4_val,
                q4_note=q4_note,
                q5_val=q5_val,
                q5_note=q5_note,
                score=score,
                completed=completed
            )
            db.session.add(log)
            
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Log saved successfully!',
            'completed': completed,
            'score': score,
            'date': log_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@api_bp.route('/api/calendar-days', methods=['GET'])
def get_calendar_days():
    days = get_rolling_30_days()
    return jsonify({'success': True, 'days': days})

@api_bp.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    chart_data = get_analytics_data()
    return jsonify({'success': True, 'data': chart_data})

# ==================== EXPORTS ====================

@api_bp.route('/api/export/csv', methods=['GET'])
def export_logs_csv():
    logs = DailyLog.query.order_by(DailyLog.date.desc()).all()
    csv_str = export_csv(logs)
    return Response(
        csv_str,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=lifetrack_export.csv"}
    )

@api_bp.route('/api/export/excel', methods=['GET'])
def export_logs_excel():
    logs = DailyLog.query.order_by(DailyLog.date.desc()).all()
    excel_bytes = export_excel(logs)
    return send_file(
        BytesIO(excel_bytes),
        download_name="lifetrack_export.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@api_bp.route('/api/export/pdf', methods=['GET'])
def export_logs_pdf():
    logs = DailyLog.query.order_by(DailyLog.date.desc()).all()
    stats = get_dashboard_metrics()
    report = generate_monthly_report()
    pdf_bytes = export_pdf(logs, stats, report)
    return send_file(
        BytesIO(pdf_bytes),
        download_name="lifetrack_monthly_report.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

# ==================== BACKUP & RESTORE ====================

@api_bp.route('/api/backup/export-json', methods=['GET'])
def export_json():
    json_str = export_json_backup()
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename=lifetrack_backup_{datetime.now().strftime('%Y%m%d')}.json"}
    )

@api_bp.route('/api/backup/import-json', methods=['POST'])
def import_json():
    if 'backup_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
    file = request.files['backup_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
        
    try:
        content = file.read().decode('utf-8')
        success, msg, count = import_json_backup(content)
        return jsonify({'success': success, 'message': f"{msg} Imported {count} logs."})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Failed to read file: {str(e)}"}), 500

@api_bp.route('/api/backup/create-sqlite-backup', methods=['POST'])
def create_sqlite_backup():
    # SQLite file sits in instance folder
    instance_path = current_app.instance_path
    db_file = os.path.join(instance_path, 'database.db')
    backup_dir = os.path.join(current_app.root_path, 'backups')
    
    success, msg = create_db_backup(db_file, backup_dir)
    return jsonify({'success': success, 'message': msg})

# ==================== DEVELOPER DEBUG TOOLS ====================

@api_bp.route('/api/debug/reset-database', methods=['POST'])
def reset_database():
    try:
        DailyLog.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Database reset successfully. All logs deleted.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Reset failed: {str(e)}'}), 500

@api_bp.route('/api/debug/populate-dummy', methods=['POST'])
def populate_dummy():
    try:
        # Delete existing logs to avoid unique constraint collisions
        DailyLog.query.delete()
        
        today = date.today()
        dummy_notes = {
            'q1': ["Read documentation", "Studied algorithms", "Completed Flask tutorial", "Learnt SQLAlchemy joins", "Read Python design patterns"],
            'q2': ["Refactored styles", "Built database schema", "Fixed chart rendering bugs", "Wrote API routes", "Polished sidebar responsiveness"],
            'q3': ["Went for 30m run", "Yoga session", "Gym workout (Leg day)", "15-minute home workout", "Rode bicycle around park"],
            'q4': ["Updated CV on LinkedIn", "Applied for two backend roles", "Refactored portfolio home", "Sent connect invites to developers", "Practiced system design questions"],
            'q5': ["Blocked YouTube", "Kept phone in drawer", "Logged out of Instagram", "Zero social scrolling today!", "Stayed focused during pomodoros"]
        }
        
        # We will populate the last 30 days
        for i in range(29, -1, -1):
            log_date = today - timedelta(days=i)
            
            # Skip a couple of days to simulate missed logs (e.g. 5 days ago and 15 days ago)
            if i in [5, 16]:
                continue
                
            # Random score weights: high chance of good days
            # We want to create some perfect streaks
            day_type = random.choices(['perfect', 'partial', 'missed'], weights=[60, 30, 10])[0]
            
            if day_type == 'perfect':
                q1, q2, q3, q4, q5 = True, True, True, True, True
            elif day_type == 'missed':
                q1, q2, q3, q4, q5 = False, False, False, False, False
            else:
                # partial day, select random booleans
                q1 = random.choice([True, False])
                q2 = random.choice([True, False])
                q3 = random.choice([True, False])
                q4 = random.choice([True, False])
                q5 = random.choice([True, False])
                # Ensure it's not perfect or zero
                if q1 and q2 and q3 and q4 and q5:
                    q5 = False
                if not (q1 or q2 or q3 or q4 or q5):
                    q1 = True
                    
            score = sum([q1, q2, q3, q4, q5])
            completed = (score == 5)
            
            # Form notes if value is True
            n1 = random.choice(dummy_notes['q1']) if q1 else ""
            n2 = random.choice(dummy_notes['q2']) if q2 else ""
            n3 = random.choice(dummy_notes['q3']) if q3 else ""
            n4 = random.choice(dummy_notes['q4']) if q4 else ""
            n5 = random.choice(dummy_notes['q5']) if q5 else ""
            
            new_log = DailyLog(
                date=log_date,
                q1_val=q1, q1_note=n1,
                q2_val=q2, q2_note=n2,
                q3_val=q3, q3_note=n3,
                q4_val=q4, q4_note=n4,
                q5_val=q5, q5_note=n5,
                score=score,
                completed=completed
            )
            db.session.add(new_log)
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dummy database populated successfully with rolling 30-day data.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Populating dummy data failed: {str(e)}'}), 500
