from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, date
from database.connection import db
from models.log import DailyLog
from utils.analytics import get_dashboard_metrics, generate_monthly_report, get_rolling_30_days

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
def dashboard():
    stats = get_dashboard_metrics()
    return render_template('dashboard.html', stats=stats, page='dashboard')

@main_bp.route('/log')
def log_today():
    today = date.today()
    # Check if a log already exists for today
    existing_log = DailyLog.query.filter_by(date=today).first()
    
    log_dict = None
    already_completed_today = False
    
    if existing_log:
        log_dict = existing_log.to_dict()
        already_completed_today = existing_log.completed
        
    return render_template(
        'log.html', 
        existing_log=log_dict, 
        already_completed_today=already_completed_today,
        today_str=today.strftime('%A, %b %d, %Y'),
        page='log'
    )

@main_bp.route('/analytics')
def analytics():
    # Pass standard details to charts page if needed, otherwise loaded via JS API
    return render_template('analytics.html', page='analytics')

@main_bp.route('/reports')
def reports():
    report_data = generate_monthly_report()
    return render_template('reports.html', report=report_data, page='reports')

@main_bp.route('/settings')
def settings():
    # Helper to pass current date for manual simulation testing
    today_str = date.today().strftime('%Y-%m-%d')
    return render_template('settings.html', today_str=today_str, page='settings')
