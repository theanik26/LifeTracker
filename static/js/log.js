// LifeTrack Daily Log Questionnaire Wizard

document.addEventListener('DOMContentLoaded', function() {
    const wizardForm = document.getElementById('wizard-form');
    if (!wizardForm) return; // Exit if not on questionnaire page

    const steps = document.querySelectorAll('.wizard-step');
    const progressBar = document.getElementById('wizard-progress-bar');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.getElementById('btn-submit');
    
    // Celebration overlay elements
    const celebrationOverlay = document.getElementById('celebration-overlay');
    const btnCelebrationContinue = document.getElementById('btn-celebration-continue');

    let currentStep = 0;
    
    // Form state values
    const answers = {
        q1_val: null, q1_note: '',
        q2_val: null, q2_note: '',
        q3_val: null, q3_note: '',
        q4_val: null, q4_note: '',
        q5_val: null, q5_note: ''
    };

    // Pre-populate if editing existing log
    // We can extract data from global script tags or attributes in the template
    try {
        const existingDataElem = document.getElementById('existing-log-data');
        if (existingDataElem && existingDataElem.value) {
            const data = JSON.parse(existingDataElem.value);
            for (let i = 1; i <= 5; i++) {
                answers[`q${i}_val`] = data[`q${i}_val`];
                answers[`q${i}_note`] = data[`q${i}_note`];
                
                // Set UI state for this question
                const val = data[`q${i}_val`];
                const yesBtn = document.querySelector(`.option-btn[data-q="q${i}"][data-val="yes"]`);
                const noBtn = document.querySelector(`.option-btn[data-q="q${i}"][data-val="no"]`);
                const textarea = document.querySelector(`textarea[data-q="q${i}"]`);
                
                const isInverted = yesBtn ? yesBtn.getAttribute('data-inverted') === 'true' : false;
                if (isInverted) {
                    if (val === true && noBtn) noBtn.classList.add('selected-yes');
                    if (val === false && yesBtn) yesBtn.classList.add('selected-no');
                } else {
                    if (val === true && yesBtn) yesBtn.classList.add('selected-yes');
                    if (val === false && noBtn) noBtn.classList.add('selected-no');
                }
                if (textarea) textarea.value = data[`q${i}_note`] || '';
            }
        }
    } catch(e) {
        console.error("Error reading existing log data:", e);
    }

    // 1. Wizard navigation logic
    function updateStepUI() {
        steps.forEach((step, idx) => {
            if (idx === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Progress bar percentage
        const progressPct = ((currentStep) / (steps.length - 1)) * 100;
        progressBar.style.width = `${progressPct}%`;

        // Button visibilities
        if (currentStep === 0) {
            btnPrev.style.visibility = 'hidden';
        } else {
            btnPrev.style.visibility = 'visible';
        }

        if (currentStep === steps.length - 1) {
            btnNext.style.display = 'none';
            btnSubmit.style.display = 'block';
        } else {
            btnNext.style.display = 'block';
            btnSubmit.style.display = 'none';
        }
    }

    // Bind Option buttons (Yes/No selections)
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const q = this.getAttribute('data-q');
            const valStr = this.getAttribute('data-val');
            const isInverted = this.getAttribute('data-inverted') === 'true';
            
            let val;
            if (isInverted) {
                val = (valStr === 'no');
            } else {
                val = (valStr === 'yes');
            }

            answers[`${q}_val`] = val;

            // Toggle active styling
            const yesBtn = document.querySelector(`.option-btn[data-q="${q}"][data-val="yes"]`);
            const noBtn = document.querySelector(`.option-btn[data-q="${q}"][data-val="no"]`);

            if (isInverted) {
                if (valStr === 'no') {
                    noBtn.classList.add('selected-yes');
                    yesBtn.classList.remove('selected-no');
                } else {
                    noBtn.classList.remove('selected-yes');
                    yesBtn.classList.add('selected-no');
                }
            } else {
                if (val) {
                    yesBtn.classList.add('selected-yes');
                    noBtn.classList.remove('selected-no');
                } else {
                    yesBtn.classList.remove('selected-yes');
                    noBtn.classList.add('selected-no');
                }
            }
        });
    });

    // Bind textareas (Explanations)
    document.querySelectorAll('.custom-textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            const q = this.getAttribute('data-q');
            answers[`${q}_note`] = this.value;
        });
    });

    // Navigation triggers
    btnNext.addEventListener('click', () => {
        const qKey = `q${currentStep + 1}_val`;
        
        // Validation: Must select Yes or No before proceeding
        if (answers[qKey] === null) {
            LifeTrackToast.show("Please select Yes or No to proceed.", "warning");
            return;
        }

        if (currentStep < steps.length - 1) {
            currentStep++;
            updateStepUI();
        }
    });

    btnPrev.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            updateStepUI();
        }
    });

    // Form submission
    wizardForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Final step validation
        if (answers.q5_val === null) {
            LifeTrackToast.show("Please answer the final question.", "warning");
            return;
        }

        // Post answers to local Flask database
        btnSubmit.disabled = true;
        btnSubmit.innerText = "Saving...";

        fetch('/api/submit-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(answers)
        })
        .then(res => res.json())
        .then(data => {
            btnSubmit.disabled = false;
            btnSubmit.innerText = "Submit Daily Log";

            if (data.success) {
                LifeTrackToast.show(data.message, "success");
                
                // Perfect day validation
                if (data.completed) {
                    showCelebration();
                } else {
                    // Redirect to dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1200);
                }
            } else {
                LifeTrackToast.show(data.message || "Failed to submit log.", "error");
            }
        })
        .catch(err => {
            btnSubmit.disabled = false;
            btnSubmit.innerText = "Submit Daily Log";
            console.error("Submission error:", err);
            LifeTrackToast.show("Network error. Could not connect to local server.", "error");
        });
    });

    // 2. Celebration Screen trigger
    function showCelebration() {
        celebrationOverlay.style.display = 'flex';
        
        // Trigger canvas particles
        if (window.LifeTrackConfetti) {
            window.LifeTrackConfetti.start(5); // Play for 5 seconds
        }
    }

    btnCelebrationContinue.addEventListener('click', () => {
        celebrationOverlay.style.display = 'none';
        window.location.href = '/dashboard';
    });

    // Init UI
    updateStepUI();
});
