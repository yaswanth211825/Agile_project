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

    // Save activity to server
    fetch('/save_activity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ activity: newActivity })
    }).then(response => {
        if (response.ok) {
            console.log('Activity saved');
        } else {
            console.error('Failed to save activity');
        }
    });

    // Display the new activity
    displayActivity(newActivity);

    // Clear the current session
    localStorage.removeItem('currentSession');
}
