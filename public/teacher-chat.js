function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function renderChatMessage(message, sender) {
    const chatHistory = document.getElementById('chatHistory');
    const messageBox = document.createElement('div');
    messageBox.style.marginBottom = '16px';
    messageBox.style.padding = '14px';
    messageBox.style.borderRadius = '14px';
    messageBox.style.background = sender === 'teacher' ? 'rgba(37, 99, 235, 0.1)' : 'rgba(15, 23, 42, 0.9)';
    messageBox.innerHTML = `
        <div style="font-size: 0.9rem; color: ${sender === 'teacher' ? '#1d4ed8' : '#f8fafc'};"><strong>${sender === 'teacher' ? 'Teacher' : 'You'}</strong></div>
        <p style="margin: 8px 0 0; white-space: pre-line;">${message}</p>
    `;
    chatHistory.appendChild(messageBox);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function loadMessages(teacherId) {
    const student = JSON.parse(sessionStorage.getItem('user') || 'null');
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.innerHTML = '';

    if (!student) {
        renderChatMessage('Please log in again to continue the chat.', 'teacher');
        return;
    }

    try {
        const res = await fetch(`/api/messages?student_id=${encodeURIComponent(student.id)}&teacher_id=${encodeURIComponent(teacherId)}`);
        const data = await res.json();
        if (data.success) {
            data.messages.forEach(msg => renderChatMessage(msg.message, msg.from_role === 'teacher' ? 'teacher' : 'user'));
        } else {
            renderChatMessage('No conversation history yet.', 'teacher');
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        renderChatMessage('Failed to load messages.', 'teacher');
    }
}

async function loadTeacher() {
    const teacherId = getQueryParam('teacherId');
    const teacherName = getQueryParam('name');
    document.getElementById('teacherName').textContent = teacherName ? teacherName : 'Teacher Consultation';
    document.getElementById('teacherTitle').textContent = teacherName ? `Chat with ${teacherName}` : 'Chat with Teacher';

    if (!teacherId) {
        document.getElementById('teacherDetails').textContent = 'Teacher details unavailable.';
        return;
    }

    try {
        const res = await fetch(`/api/user/${teacherId}`);
        const data = await res.json();
        if (data.success && data.role === 'teacher') {
            document.getElementById('teacherDetails').textContent = `${data.user.subjects || 'No subjects listed'} — ${data.user.stream || 'Stream unavailable'}`;
        } else {
            document.getElementById('teacherDetails').textContent = 'Teacher profile could not be loaded.';
        }
    } catch (error) {
        console.error(error);
        document.getElementById('teacherDetails').textContent = 'Teacher profile could not be loaded.';
    }

    loadMessages(teacherId);
}

async function sendChatMessage() {
    const messageInput = document.getElementById('consultMessage');
    const fileInput = document.getElementById('consultFile');
    const teacherId = getQueryParam('teacherId');
    const teacherName = getQueryParam('name');
    const student = JSON.parse(sessionStorage.getItem('user') || 'null');

    const message = messageInput.value.trim();
    const fileName = fileInput.files.length ? fileInput.files[0].name : '';

    if (!message && !fileName) {
        alert('Please enter a message or select a document.');
        return;
    }

    if (!student) {
        alert('Please login before sending messages.');
        window.location.href = 'login.html';
        return;
    }

    const sentText = `${message}${fileName ? `\n\nSent file: ${fileName}` : ''}`;

    try {
        const response = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: student.id,
                teacher_id: teacherId,
                from_role: 'student',
                sender_id: student.id,
                message: sentText,
                attachment_name: fileName
            })
        });

        const data = await response.json();
        if (data.success) {
            renderChatMessage(sentText, 'user');
            messageInput.value = '';
            fileInput.value = '';

            setTimeout(async () => {
                const replyText = `Hello ${student.fullName}, I have received your request and will get back to you soon.`;
                await fetch('/api/messages', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        student_id: student.id,
                        teacher_id: teacherId,
                        from_role: 'teacher',
                        sender_id: teacherId,
                        message: replyText,
                        attachment_name: null
                    })
                });
                renderChatMessage(replyText, 'teacher');
            }, 1600);
        } else {
            alert(data.message || 'Failed to send message.');
        }
    } catch (error) {
        console.error('Chat send error:', error);
        alert('Connection error. Please try again.');
    }
}

window.addEventListener('load', loadTeacher);
