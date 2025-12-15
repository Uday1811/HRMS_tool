
document.addEventListener('DOMContentLoaded', function () {
    const clockBtn = document.getElementById('clockBtn');
    const liveTimer = document.getElementById('liveTimer');

    // 1. Live Clock
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        if (liveTimer) {
            liveTimer.textContent = `${hours}:${minutes}:${seconds}`;
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
        });
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
});
