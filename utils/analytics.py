from datetime import datetime, timedelta
from sqlalchemy import func
from database.connection import db
from models.log import DailyLog

def get_streak_stats():
    """
    Calculates current streak and longest streak of completed days (score == 5).
    """
    # Get all completed dates in ascending order
    completed_logs = DailyLog.query.filter_by(completed=True).order_by(DailyLog.date.asc()).all()
    if not completed_logs:
        return {'current_streak': 0, 'longest_streak': 0}
        
    completed_dates = {log.date for log in completed_logs}
    sorted_dates = sorted(list(completed_dates))
    
    # Calculate Longest Streak
    longest_streak = 0
    current_temp = 0
    prev_date = None
    
    for d in sorted_dates:
        if prev_date is None:
            current_temp = 1
        elif (d - prev_date).days == 1:
            current_temp += 1
        else:
            if current_temp > longest_streak:
                longest_streak = current_temp
            current_temp = 1
        prev_date = d
    if current_temp > longest_streak:
        longest_streak = current_temp

    # Calculate Current Streak
    today = datetime.date(datetime.now())
    yesterday = today - timedelta(days=1)
    
    current_streak = 0
    if today in completed_dates:
        current_streak = 1
        check_date = today - timedelta(days=1)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    elif yesterday in completed_dates:
        current_streak = 1
        check_date = yesterday - timedelta(days=1)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    else:
        current_streak = 0
        
    return {
        'current_streak': current_streak,
        'longest_streak': max(longest_streak, current_streak)
    }

def get_dashboard_metrics():
    """
    Computes summary statistics for cards on the dashboard.
    """
    total_logs = DailyLog.query.count()
    total_completed = DailyLog.query.filter_by(completed=True).count()
    
    streaks = get_streak_stats()
    
    # Completion %
    completion_percentage = 0
    if total_logs > 0:
        completion_percentage = round((total_completed / total_logs) * 100, 1)
        
    # Average score
    avg_score_raw = db.session.query(func.avg(DailyLog.score)).scalar()
    avg_score = round(float(avg_score_raw), 2) if avg_score_raw is not None else 0.0
    
    # Notes count
    notes_count = 0
    all_logs = DailyLog.query.all()
    latest_notes = []
    for log in sorted(all_logs, key=lambda x: x.date, reverse=True):
        day_notes = []
        from models.question import QuestionConfig
        questions = QuestionConfig.query.order_by(QuestionConfig.id).all()
        q_map = {q.id: q.short_title for q in questions}
        
        if log.q1_note: day_notes.append((q_map.get(1, 'Study'), log.q1_note))
        if log.q2_note: day_notes.append((q_map.get(2, 'Project'), log.q2_note))
        if log.q3_note: day_notes.append((q_map.get(3, 'Exercise'), log.q3_note))
        if log.q4_note: day_notes.append((q_map.get(4, 'Career'), log.q4_note))
        if log.q5_note: day_notes.append((q_map.get(5, 'Social Media'), log.q5_note))
        
        for q_type, note in day_notes:
            if len(latest_notes) < 5:
                latest_notes.append({
                    'date': log.date.strftime('%b %d, %Y'),
                    'task': q_type,
                    'note': note
                })
    
    return {
        'total_logged_days': total_logs,
        'total_completed_days': total_completed,
        'current_streak': streaks['current_streak'],
        'longest_streak': streaks['longest_streak'],
        'completion_percentage': completion_percentage,
        'avg_score': avg_score,
        'latest_notes': latest_notes
    }

def get_rolling_30_days():
    """
    Returns calendar data for the last 30 days up to today.
    """
    today = datetime.date(datetime.now())
    days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    
    # Query logs in this range
    logs = DailyLog.query.filter(DailyLog.date.between(days[0], days[-1])).all()
    logs_by_date = {log.date: log for log in logs}
    
    calendar_days = []
    for d in days:
        if d in logs_by_date:
            log = logs_by_date[d]
            status = 'completed' if log.completed else 'partial' if log.score > 0 else 'missed'
            score = log.score
        else:
            # If the date has passed (prior to today), it is considered "missed". If it's today, it's "pending".
            status = 'pending' if d == today else 'missed'
            score = 0
            
        calendar_days.append({
            'date': d.strftime('%Y-%m-%d'),
            'day_num': d.day,
            'weekday': d.strftime('%a'),
            'status': status,
            'score': score
        })
        
    return calendar_days

def get_analytics_data():
    """
    Generates data formats suited for Chart.js charts.
    """
    all_logs = DailyLog.query.order_by(DailyLog.date.asc()).all()
    if not all_logs:
        return {}
        
    # 1. Daily trends (last 15 days score)
    trend_logs = all_logs[-15:]
    trend_dates = [log.date.strftime('%b %d') for log in trend_logs]
    trend_scores = [log.score for log in trend_logs]
    
    # 2. Task completion percentages
    total = len(all_logs)
    q1_pct = round((sum(1 for l in all_logs if l.q1_val) / total) * 100, 1)
    q2_pct = round((sum(1 for l in all_logs if l.q2_val) / total) * 100, 1)
    q3_pct = round((sum(1 for l in all_logs if l.q3_val) / total) * 100, 1)
    q4_pct = round((sum(1 for l in all_logs if l.q4_val) / total) * 100, 1)
    q5_pct = round((sum(1 for l in all_logs if l.q5_val) / total) * 100, 1)
    
    # 3. Productive weekdays (Avg score by day of week)
    # Mon = 0, Sun = 6
    weekday_scores = {i: [] for i in range(7)}
    for log in all_logs:
        weekday_scores[log.date.weekday()].append(log.score)
        
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekday_averages = []
    for i in range(7):
        scores = weekday_scores[i]
        weekday_averages.append(round(sum(scores) / len(scores), 2) if scores else 0.0)
        
    # Find most productive day
    best_day_idx = weekday_averages.index(max(weekday_averages)) if any(weekday_averages) else None
    most_productive_day = weekday_names[best_day_idx] if best_day_idx is not None else "N/A"
    
    # 4. Missed vs Completed Days
    completed_count = sum(1 for l in all_logs if l.completed)
    partial_count = sum(1 for l in all_logs if 0 < l.score < 5)
    zero_count = sum(1 for l in all_logs if l.score == 0)
    
    return {
        'trend_dates': trend_dates,
        'trend_scores': trend_scores,
        'task_percentages': {
            q_map.get(1, 'Study'): q1_pct,
            q_map.get(2, 'Project'): q2_pct,
            q_map.get(3, 'Exercise'): q3_pct,
            q_map.get(4, 'Career'): q4_pct,
            q_map.get(5, 'Social Media Avoidance'): q5_pct
        },
        'weekday_labels': weekday_names,
        'weekday_scores': weekday_averages,
        'most_productive_day': most_productive_day,
        'pie_data': [completed_count, partial_count, zero_count]
    }

def generate_monthly_report():
    """
    Computes report insights and recommendations.
    """
    today = datetime.date(datetime.now())
    first_day_of_month = today.replace(day=1)
    
    # Fetch logs for the current calendar month
    logs = DailyLog.query.filter(DailyLog.date >= first_day_of_month).order_by(DailyLog.date.asc()).all()
    
    total_days_in_month = (today - first_day_of_month).days + 1
    total_logged = len(logs)
    completed_days = sum(1 for l in logs if l.completed)
    partial_days = sum(1 for l in logs if 0 < l.score < 5)
    missed_days = total_days_in_month - completed_days
    
    if not logs:
        return {
            'month_name': today.strftime('%B %Y'),
            'total_logged': 0,
            'completed_days': 0,
            'missed_days': 0,
            'avg_score': 0,
            'consistency_score': 0,
            'best_week': 'N/A',
            'worst_week': 'N/A',
            'recommendations': ["No data logged yet for this month. Start logging today to receive insights!"]
        }
        
    avg_score = round(sum(l.score for l in logs) / total_logged, 2)
    consistency_score = round((completed_days / total_logged) * 100, 1) if total_logged > 0 else 0
    
    # Calculate best and worst weeks
    # Group by calendar week (isocalendar week number)
    weeks = {}
    for log in logs:
        week_num = log.date.isocalendar()[1]
        if week_num not in weeks:
            weeks[week_num] = []
        weeks[week_num].append(log.score)
        
    week_averages = {w: sum(s)/len(s) for w, s in weeks.items()}
    
    best_week_num = max(week_averages, key=week_averages.get) if week_averages else None
    worst_week_num = min(week_averages, key=week_averages.get) if week_averages else None
    
    best_week_str = f"Week {best_week_num} (Avg Score: {round(week_averages[best_week_num], 2)}/5)" if best_week_num else "N/A"
    worst_week_str = f"Week {worst_week_num} (Avg Score: {round(week_averages[worst_week_num], 2)}/5)" if worst_week_num else "N/A"
    
    # Task analysis for recommendations
    from models.question import QuestionConfig
    questions = QuestionConfig.query.order_by(QuestionConfig.id).all()
    q_map = {q.id: q.short_title for q in questions}
    
    q1_pct = (sum(1 for l in logs if l.q1_val) / total_logged) * 100
    q2_pct = (sum(1 for l in logs if l.q2_val) / total_logged) * 100
    q3_pct = (sum(1 for l in logs if l.q3_val) / total_logged) * 100
    q4_pct = (sum(1 for l in logs if l.q4_val) / total_logged) * 100
    q5_pct = (sum(1 for l in logs if l.q5_val) / total_logged) * 100
    
    recommendations = []
    
    # Heuristics
    if q1_pct < 60:
        recommendations.append(f"Your progress rate for '{q_map.get(1, 'Study')}' is slightly low ({round(q1_pct, 1)}%). Try dedicating just 15 minutes to it right after breakfast.")
    if q2_pct < 60:
        recommendations.append(f"Consistency for '{q_map.get(2, 'Project')}' is below target ({round(q2_pct, 1)}%). Commit to the '2-minute rule': start with just one small task daily.")
    if q3_pct < 60:
        recommendations.append(f"Your execution for '{q_map.get(3, 'Exercise')}' is trailing ({round(q3_pct, 1)}%). Remember that even a 10-minute session counts as a daily win!")
    if q4_pct < 60:
        recommendations.append(f"Progress on '{q_map.get(4, 'Career')}' can be improved ({round(q4_pct, 1)}%). Try setting a recurring reminder to check in on progress twice a week.")
    if q5_pct < 60:
        if questions and len(questions) >= 5 and questions[4].is_inverted:
            recommendations.append(f"Distractions relating to '{q_map.get(5, 'Avoided social media')}' are high. Try configuring app limits or screen-free times.")
        else:
            recommendations.append(f"Performance for '{q_map.get(5, 'Avoided social media')}' is low ({round(q5_pct, 1)}%). Focus on removing friction and building focus blocks.")
        
    # Positive feedback
    if consistency_score >= 80:
        recommendations.append("Outstanding monthly performance! You are showing stellar self-discipline and consistency.")
    elif len(recommendations) == 0:
        recommendations.append("Solid progress this month! Focus on maintaining your current routine and protecting your streaks.")
        
    return {
        'month_name': today.strftime('%B %Y'),
        'total_logged': total_logged,
        'completed_days': completed_days,
        'missed_days': missed_days,
        'avg_score': avg_score,
        'consistency_score': consistency_score,
        'best_week': best_week_str,
        'worst_week': worst_week_str,
        'recommendations': recommendations
    }
