async function submitFeedback(event) {
    event.preventDefault();

    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();
    const user = JSON.parse(sessionStorage.getItem('user') || 'null');

    if (!fullName || !message) {
        showNotification('Please enter your name and message.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: user?.id || null,
                user_type: sessionStorage.getItem('role') || null,
                fullName,
                email,
                message
            })
        });

        const data = await response.json();
        if (data.success) {
            showNotification('Thank you! Your feedback has been submitted.', 'success');
            document.getElementById('feedbackForm').reset();
        } else {
            showNotification(data.message || 'Could not submit feedback.', 'error');
        }
    } catch (error) {
        console.error('Feedback submission error:', error);
        showNotification('Submission failed. Please try again later.', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notif = document.getElementById('feedbackNotification');
    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.classList.remove('hidden');
    setTimeout(() => notif.classList.add('hidden'), 4000);
}
