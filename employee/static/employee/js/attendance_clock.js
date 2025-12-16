
document.addEventListener('DOMContentLoaded', function () {
    const clockBtn = document.getElementById('clockBtn');
    const liveTimer = document.getElementById('liveTimer');

    // 1. Live Clock
    // 1. Live Stopwatch
    let notificationShown = false;

    function updateClock() {
        if (!liveTimer) return;

        const startTimeStr = liveTimer.getAttribute('data-start-time');

        if (startTimeStr) {
            // User is clocked in -> Show Stopwatch
            const startTime = new Date(startTimeStr).getTime();
            const now = new Date().getTime();
            const elapsed = now - startTime;

            if (elapsed < 0) {
                // Future time (clock drift?), default 0
                liveTimer.textContent = "00:00:00";
                return;
            }

            const totalSeconds = Math.floor(elapsed / 1000);
            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);
            const seconds = totalSeconds % 60;

            const hStr = String(hours).padStart(2, '0');
            const mStr = String(minutes).padStart(2, '0');
            const sStr = String(seconds).padStart(2, '0');

            liveTimer.textContent = `${hStr}:${mStr}:${sStr}`;

            // Check conditions
            // 9 hours = 9 * 3600 = 32400 seconds
            if (totalSeconds >= 32400) {
                liveTimer.style.color = 'red';
            } else {
                liveTimer.style.color = ''; // Reset
            }

            // 9.5 hours = 9.5 * 3600 = 34200 seconds
            if (totalSeconds >= 34200 && !notificationShown) {
                alert("You have exceeded 9:30 hours. Please remember to clock out!");
                notificationShown = true;
            }

        } else {
            // User is clocked out -> Show 00:00:00 as per request (or maybe simple clock? Request implies "start like stopwatch")
            // "from that tym to start like stopwatch" implies it runs when clocked in.
            // When clocked out, usually we show static 00:00:00 or current time. 
            // Given the screenshot shows 00:00:00, let's stick to that to be clean.
            liveTimer.textContent = "00:00:00";
            liveTimer.style.color = '';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 2. Click Handler
    if (clockBtn) {
        clockBtn.addEventListener('click', function () {
            const isClockIn = clockBtn.innerText.includes('Clock-In');
            const action = isClockIn ? 'in' : 'out';

            // Get Location
            getLocationAndSend(action);
        });
    }

    // New Buttons Handlers
    const remoteClockInBtn = document.getElementById('remoteClockInBtn');

    if (remoteClockInBtn) {
        remoteClockInBtn.addEventListener('click', function (e) {
            e.preventDefault();
            getLocationAndSend('in');
        });
    }

    function getLocationAndSend(action) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                sendAttendance(action, lat, lng);
            }, error => {
                alert("Location access is required for attendance.");
                console.error(error);
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }


    // 3. Dynamic Date
    const liveDate = document.getElementById('liveDate');
    function updateDate() {
        if (liveDate) {
            const now = new Date();
            const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
            liveDate.textContent = now.toLocaleDateString('en-US', options);
        }
    }
    // Update date every minute
    setInterval(updateDate, 60000);
    updateDate();

    // 4. Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const root = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        root.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.setAttribute('name', 'moon-outline');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = root.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                root.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (themeIcon) themeIcon.setAttribute('name', 'sunny-outline');
            } else {
                root.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) themeIcon.setAttribute('name', 'moon-outline');
            }
        });
    }

    // 5. Existing Send Attendance
    function sendAttendance(action, lat, lng) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/attendance/ajax-clock/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                action: action,
                lat: lat,
                lng: lng
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload(); // Reload to update table and button state
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
    }

    // 6. Auto-Tracking (Hourly)
    // clockBtn is already defined above
    if (clockBtn && clockBtn.innerText.includes('Clock Out')) {
        // User is clocked in
        console.log("User is clocked in. Starting hourly tracker.");

        setInterval(() => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;

                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                    fetch('/attendance/auto-clock-log/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            latitude: lat,
                            longitude: lng
                        })
                    })
                        .then(res => res.json())
                        .then(data => console.log('Auto-log success:', data))
                        .catch(err => console.error('Auto-log error:', err));

                }, err => console.error(err));
            }
        }, 3600000); // 1 hour = 3600000 ms
    }
});
