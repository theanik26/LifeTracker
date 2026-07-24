// Offline Canvas Confetti Particle System
// Designed to run completely local and offline.

window.LifeTrackConfetti = {
    start: function(durationSeconds = 4) {
        let canvas = document.getElementById('confetti-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'confetti-canvas';
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100vw';
            canvas.style.height = '100vh';
            canvas.style.pointerEvents = 'none';
            canvas.style.zIndex = '9999';
            document.body.appendChild(canvas);
        }

        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        // Resize handler
        const handleResize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', handleResize);

        // Particle configuration
        const colors = [
            '#6366f1', // Indigo
            '#06b6d4', // Cyan
            '#10b981', // Emerald Green
            '#fbbf24', // Amber Yellow
            '#ec4899', // Pink
            '#a855f7'  // Purple
        ];
        
        const particles = [];
        const maxParticles = 150;

        class ConfettiParticle {
            constructor() {
                this.x = Math.random() * width;
                // Start slightly above screen
                this.y = Math.random() * -100 - 20;
                this.size = Math.random() * 8 + 6;
                this.color = colors[Math.floor(Math.random() * colors.length)];
                
                // Physics
                this.vx = Math.random() * 4 - 2;
                this.vy = Math.random() * 6 + 4;
                
                // Rotation
                this.rotation = Math.random() * 360;
                this.rotationSpeed = Math.random() * 4 - 2;
                
                this.opacity = 1;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.rotation += this.rotationSpeed;
                
                // Slight wind drift
                this.vx += Math.sin(this.y / 30) * 0.05;
                
                // Fade out near bottom
                if (this.y > height - 100) {
                    this.opacity -= 0.015;
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation * Math.PI / 180);
                ctx.globalAlpha = Math.max(0, this.opacity);
                ctx.fillStyle = this.color;
                
                // Draw a small rectangle/ribbon
                ctx.fillRect(-this.size / 2, -this.size / 4, this.size, this.size / 2);
                
                ctx.restore();
            }
        }

        // Spawn initial batch
        for (let i = 0; i < maxParticles; i++) {
            particles.push(new ConfettiParticle());
        }

        let animationFrameId;
        let startTime = Date.now();
        const endTime = startTime + (durationSeconds * 1000);

        function animate() {
            ctx.clearRect(0, 0, width, height);

            // Filter out dead particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.update();
                p.draw();

                // If particle is off screen or faded out
                if (p.y > height || p.opacity <= 0) {
                    // Respawn if timer hasn't expired
                    if (Date.now() < endTime) {
                        particles[i] = new ConfettiParticle();
                    } else {
                        particles.splice(i, 1);
                    }
                }
            }

            if (particles.length > 0) {
                animationFrameId = requestAnimationFrame(animate);
            } else {
                // Cleanup
                window.removeEventListener('resize', handleResize);
                if (canvas.parentNode) {
                    canvas.parentNode.removeChild(canvas);
                }
            }
        }

        animate();
    }
};
