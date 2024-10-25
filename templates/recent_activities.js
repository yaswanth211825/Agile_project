document.addEventListener('DOMContentLoaded', () => {
    loadActivities();
    setInterval(loadActivities, 5000); // Update every 5 seconds
});

function loadActivities() {
    fetch('/recent_activities')
        .then(response => response.json())
        .then(data => {
            const activityList = document.getElementById('activity-list');
            activityList.innerHTML = ''; // Clear the existing list
            data.forEach(activity => {
                const newActivityItem = document.createElement('li');
                newActivityItem.textContent = activity;
                activityList.appendChild(newActivityItem);
            });
        })
        .catch(error => console.error('Error:', error));
}

function startPlaying(instrument, url) {
    const startTime = new Date();
    const startData = {
        instrument: instrument,
        startTime: startTime.getTime()
    };

    // Save start time to localStorage
    localStorage.setItem('currentSession', JSON.stringify(startData));

    // Redirect to the playing page
    window.location.href = url;
}

function stopPlaying() {
    const sessionData = JSON.parse(localStorage.getItem('currentSession'));
    if (!sessionData) {
        return;
    }

    const endTime = new Date();
    const duration = Math.round((endTime.getTime() - sessionData.startTime) / 1000); // Duration in seconds
    const startDate = new Date(sessionData.startTime);
    const dateString = startDate.toLocaleDateString();
    const timeString = startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const newActivity = `Played ${sessionData.instrument} for ${duration} seconds on ${dateString} at ${timeString}`;

    // Save activity to localStorage
    saveActivity(newActivity);

    // Display the new activity
    displayActivity(newActivity);

    // Clear the current session
    localStorage.removeItem('currentSession');
}

function saveActivity(activity) {
    let activities = JSON.parse(localStorage.getItem('activities')) || [];
    activities.unshift(activity);
    localStorage.setItem('activities', JSON.stringify(activities));
}

function displayActivity(activity) {
    const activityList = document.getElementById('activity-list');
    const newActivityItem = document.createElement('li');
    newActivityItem.textContent = activity;
    activityList.insertBefore(newActivityItem, activityList.firstChild);
}

// Call stopPlaying when the page is loaded, if there is an ongoing session
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('currentSession')) {
        stopPlaying();
    }
});
