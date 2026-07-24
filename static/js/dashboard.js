// LifeTrack Dashboard Javascript

document.addEventListener('DOMContentLoaded', function() {
    const calendarGrid = document.getElementById('calendar-grid');
    if (!calendarGrid) return; // Exit if not on dashboard page
    
    // Modal elements
    const dayModal = new bootstrap.Modal(document.getElementById('dayDetailsModal'));
    const modalDateTitle = document.getElementById('modal-date-title');
    const modalScoreBadge = document.getElementById('modal-score-badge');
    const modalNotesContainer = document.getElementById('modal-notes-container');
    const modalLogDetails = document.getElementById('modal-log-details');
    const modalNoLog = document.getElementById('modal-no-log');

    // 1. Fetch Calendar Grid Data
    function loadCalendar() {
        fetch('/api/calendar-days')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderCalendar(data.days);
                }
            })
            .catch(err => console.error("Failed to load calendar days:", err));
    }

    // 2. Render Calendar Grid cells
    function renderCalendar(days) {
        // Clear previous grid elements (keeping header cells if any, but our grid is empty at first)
        calendarGrid.innerHTML = '';
        
        // Add Weekday Headers
        const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        weekdays.forEach(day => {
            const dayHead = document.createElement('div');
            dayHead.className = 'calendar-header-day';
            dayHead.innerText = day;
            calendarGrid.appendChild(dayHead);
        });

        // Determine offset for alignment
        // Let's align rolling days by their weekday.
        // Actually, just listing them sequentially from oldest to newest makes a beautiful 30-day block.
        // Let's align them by weekday of the first element to make it look like a real calendar grid!
        if (days.length > 0) {
            const firstDayObj = new Date(days[0].date);
            // js getDay() is 0 (Sun) to 6 (Sat)
            // convert to 0 (Mon) to 6 (Sun)
            let firstDayOfWeek = firstDayObj.getDay() - 1;
            if (firstDayOfWeek === -1) firstDayOfWeek = 6;
            
            // Add blank cells for padding
            for (let i = 0; i < firstDayOfWeek; i++) {
                const emptyCell = document.createElement('div');
                emptyCell.className = 'calendar-day-cell cell-pending';
                emptyCell.style.opacity = '0.15';
                emptyCell.style.pointerEvents = 'none';
                calendarGrid.appendChild(emptyCell);
            }
        }

        // Render cell for each day
        days.forEach(day => {
            const cell = document.createElement('div');
            let statusClass = 'cell-pending';
            
            if (day.status === 'completed') statusClass = 'cell-completed';
            else if (day.status === 'partial') statusClass = 'cell-partial';
            else if (day.status === 'missed') statusClass = 'cell-missed';
            
            cell.className = `calendar-day-cell ${statusClass}`;
            cell.setAttribute('title', `${day.date} | Score: ${day.score}/5 | ${day.status.toUpperCase()}`);
            
            // Click Handler
            cell.addEventListener('click', () => {
                showDayDetails(day.date);
            });
            
            calendarGrid.appendChild(cell);
        });
    }

    // 3. Show Details of Selected Day in Modal
    function showDayDetails(dateStr) {
        modalDateTitle.innerText = formatDateString(dateStr);
        
        fetch(`/api/log-details/${dateStr}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.logged) {
                        modalLogDetails.style.display = 'block';
                        modalNoLog.style.display = 'none';
                        renderModalDetails(data.data);
                    } else {
                        modalLogDetails.style.display = 'none';
                        modalNoLog.style.display = 'block';
                        modalScoreBadge.className = 'status-badge badge-missed';
                        modalScoreBadge.innerText = 'Not Logged';
                    }
                    dayModal.show();
                }
            })
            .catch(err => {
                console.error("Error fetching day details:", err);
                LifeTrackToast.show("Failed to load details for this day.", "error");
            });
    }

    // 4. Render checklist and notes in the modal
    function renderModalDetails(logData) {
        // Set Badge Score
        if (logData.completed) {
            modalScoreBadge.className = 'status-badge badge-completed';
            modalScoreBadge.innerText = 'Completed (5/5)';
        } else if (logData.score > 0) {
            modalScoreBadge.className = 'status-badge badge-partial';
            modalScoreBadge.innerText = `Partially Completed (${logData.score}/5)`;
        } else {
            modalScoreBadge.className = 'status-badge badge-missed';
            modalScoreBadge.innerText = 'Missed Day (0/5)';
        }

        // Render checklist items
        const questions = [
            { key: 'q1', text: 'Studied today', val: logData.q1_val, note: logData.q1_note },
            { key: 'q2', text: 'Worked on a project', val: logData.q2_val, note: logData.q2_note },
            { key: 'q3', text: 'Exercised today', val: logData.q3_val, note: logData.q3_note },
            { key: 'q4', text: 'Applied for job / Career build', val: logData.q4_val, note: logData.q4_note },
            { key: 'q5', text: 'Avoided wasting time on social media', val: logData.q5_val, note: logData.q5_note }
        ];

        modalNotesContainer.innerHTML = '';
        
        questions.forEach(q => {
            const item = document.createElement('div');
            item.className = 'p-3 mb-3 glass-card d-flex flex-column gap-2';
            item.style.background = 'rgba(255,255,255,0.02)';
            
            const header = document.createElement('div');
            header.className = 'd-flex align-items-center justify-content-between';
            
            const titleSpan = document.createElement('span');
            titleSpan.className = 'fw-semibold';
            titleSpan.innerText = q.text;
            
            const badge = document.createElement('span');
            badge.className = `status-badge ${q.val ? 'badge-completed' : 'badge-missed'}`;
            badge.innerHTML = q.val ? '✓ Completed' : '✗ Missed';
            
            header.appendChild(titleSpan);
            header.appendChild(badge);
            item.appendChild(header);
            
            if (q.note) {
                const noteBox = document.createElement('div');
                noteBox.className = 'p-2 rounded';
                noteBox.style.background = 'rgba(255,255,255,0.03)';
                noteBox.style.fontSize = '13px';
                noteBox.style.color = '#cbd5e1';
                noteBox.innerHTML = `<strong>Note:</strong> <em>${q.note}</em>`;
                item.appendChild(noteBox);
            }
            
            modalNotesContainer.appendChild(item);
        });
    }

    // Helper to format date
    function formatDateString(dateStr) {
        const d = new Date(dateStr);
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return d.toLocaleDateString('en-US', options);
    }

    // Load on init
    loadCalendar();
});
