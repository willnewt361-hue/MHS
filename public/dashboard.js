// Dashboard JS

let currentUser = null;
let userRole = null;

const posterRoles = ['class_monitors', 'class_monitor', 'peer_counsellors', 'peer_counsellor', 'counsellors', 'counsellor'];

function isUpdatePoster() {
    const role = (currentUser.role || '').toLowerCase();
    return userRole === 'teacher' || posterRoles.some(r => role.includes(r));
}

function getPreferredQuoteIndex(quotes) {
    const startDate = new Date('2026-01-01T00:00:00Z');
    const today = new Date();
    const dayDelta = Math.floor((today - startDate) / (24 * 60 * 60 * 1000));
    const quoteIndex = Math.floor(dayDelta / 2) % quotes.length;
    return quoteIndex < 0 ? 0 : quoteIndex;
}

// Check authentication
function checkAuth() {
    // First check sessionStorage from login
    const sessionUser = sessionStorage.getItem('user');
    const sessionRole = sessionStorage.getItem('role');
    const sessionIsAdmin = sessionStorage.getItem('is_admin');

    if (sessionUser && sessionRole) {
        try {
            currentUser = JSON.parse(sessionUser);
            userRole = sessionRole;

            // Set admin status
            if (sessionIsAdmin === 'true' || currentUser.is_admin) {
                userRole = 'admin';
            }

            initDashboard();
            return;
        } catch (error) {
            console.error('Invalid session data');
            sessionStorage.clear();
        }
    }

    // Fallback to certificate check for backward compatibility (only if no session data)
    if (!currentUser) {
        const DB_NAME = 'MengoHubCertificates';
        const CERT_STORE = 'certificates';

        function openDB() {
            return new Promise((resolve, reject) => {
                const request = indexedDB.open(DB_NAME, 1);
                request.onerror = () => reject(request.error);
                request.onsuccess = () => resolve(request.result);
                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    if (!db.objectStoreNames.contains(CERT_STORE)) {
                        db.createObjectStore(CERT_STORE, { keyPath: 'serialNumber' });
                    }
                };
            });
        }

        async function getAllCertificates() {
            const db = await openDB();
            const transaction = db.transaction([CERT_STORE], 'readonly');
            const store = transaction.objectStore(CERT_STORE);
            return new Promise((resolve, reject) => {
                const request = store.getAll();
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });
        }

        getAllCertificates().then(certificates => {
            const validCerts = certificates.filter(cert => {
                const now = new Date();
                const notAfter = new Date(cert.validity.notAfter);
                return now <= notAfter && (
                    cert.extensions.certificateType === 'paid_user' ||
                    cert.extensions.certificateType === 'admin'
                );
            });

            if (validCerts.length === 0) {
                window.location.href = 'index.html';
                return;
            }

            // Use the most recent valid certificate
            validCerts.sort((a, b) => new Date(b.extensions.issuedDate) - new Date(a.extensions.issuedDate));
            const cert = validCerts[0];

            // Set user role based on certificate (only for fallback users)
            if (cert.extensions.certificateType === 'admin') {
                userRole = 'admin';
                sessionStorage.setItem('is_admin', true);
            } else {
                userRole = 'student'; // Default role
            }

            // Create a mock user object from certificate
            currentUser = {
                id: cert.serialNumber,
                username: cert.subject.commonName,
                fullName: cert.subject.commonName,
                role: userRole
            };

            sessionStorage.setItem('user', JSON.stringify(currentUser));
            sessionStorage.setItem('role', userRole);

            initDashboard();
        }).catch(error => {
            console.error('Certificate check error:', error);
            window.location.href = 'index.html';
        });
    }
}

// Initialize dashboard
function initDashboard() {
    // Set user info
    document.getElementById('userGreeting').textContent = `Welcome, ${currentUser.fullName}`;
    document.getElementById('userFullName').textContent = currentUser.fullName;
    document.getElementById('userRole').textContent = userRole.charAt(0).toUpperCase() + userRole.slice(1);
    document.getElementById('userId').textContent = `ID: ${currentUser.id}`;
    document.getElementById('userPhoto').textContent = currentUser.fullName.charAt(0).toUpperCase();

    // Display random bible quote
    displayRandomBibleQuote();

    // Show login notification
    showNotification(`Logged in as ${currentUser.username}`);

    // Setup menu
    setupMenu();
    showView('home');
}

// Bible quotes array - now loaded from server
// const bibleQuotes = [ ... ];

// Display random bible quote
async function displayRandomBibleQuote() {
    try {
        const response = await fetch('/api/bible-quotes');
        const bibleQuotes = await response.json();
        
        if (!bibleQuotes || bibleQuotes.length === 0) {
            displayLocalBibleQuote();
            return;
        }
        
        const index = getPreferredQuoteIndex(bibleQuotes);
        const quote = bibleQuotes[index];
        renderBibleQuote(quote);
    } catch (error) {
        console.error('Error loading Bible quotes:', error);
        displayLocalBibleQuote();
    }
}

function renderBibleQuote(quote) {
    const quoteElement = document.getElementById('bibleQuote');
    if (!quoteElement) return;

    quoteElement.innerHTML = `
        <blockquote style="font-style: italic; margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px; color: #0f172a;">
            "${quote.quote}"
            <footer style="margin-top: 10px; font-weight: bold; color: #475569;">— ${quote.reference}</footer>
        </blockquote>
    `;
}

// Fallback function using local quotes
function displayLocalBibleQuote() {
    const bibleQuotes = [
        { quote: "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.", reference: "Jeremiah 29:11" },
        { quote: "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.", Ref: "Proverbs 3:5-6" },
        { quote: "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.", reference: "Joshua 1:9" },
        { quote: "The Lord is my shepherd, I lack nothing. He makes me lie down in green pastures, he leads me beside quiet waters, he refreshes my soul.", reference: "Psalm 23:1-3" },
        { quote: "I can do all things through Christ who strengthens me.", reference: "Philippians 4:13" },
        { quote: "Love is patient, love is kind. It does not envy, it does not boast, it is not proud.", reference: "1 Corinthians 13:4" },
        { quote: "Seek first his kingdom and his righteousness, and all these things will be given to you as well.", reference: "Matthew 6:33" },
        { quote: "Whatever you do, work at it with all your heart, as working for the Lord, not for human masters.", reference: "Colossians 3:23" },
        { quote: "Let the peace of Christ rule in your hearts, since as members of one body you were called to peace. And be thankful.", reference: "Colossians 3:15" },
        { quote: "Therefore, if anyone is in Christ, the new creation has come: The old has gone, the new is here!", reference: "2 Corinthians 5:17" }
    ];

    const index = getPreferredQuoteIndex(bibleQuotes);
    renderBibleQuote(bibleQuotes[index]);
}

// Setup menu buttons
function setupMenu() {
    const menu = document.querySelector('.menu');
    const isAdmin = sessionStorage.getItem('is_admin') === 'true';
    
    // Clear existing menu items
    menu.innerHTML = '';
    
    // Add regular menu items
    const menuItems = [
        { view: 'home', icon: '🏠', text: 'Home' },
        { view: 'teachers', icon: '👩‍🏫', text: 'Teachers' },
        { view: 'assignments', icon: '📚', text: 'Assignments' },
        { view: 'updates', icon: '📬', text: 'Updates' },
        { view: 'timetable', icon: '📅', text: 'Timetable' }
    ];
    // Student access to subjects
    if (userRole === 'student') {
        menuItems.splice(4, 0, { view: 'subjects', icon: '📖', text: 'Subjects' })
    }
    
    // Add teacher-only student list view
    if (userRole === 'teacher') {
        menuItems.splice(4, 0, { view: 'students', icon: '🧑‍🎓', text: 'Students' });
    }

    // Add admin menu items if user is admin
    if (isAdmin) {
        menuItems.push(
            { view: 'admin-users', icon: '👥', text: 'User Management' },
            { view: 'admin-payments', icon: '💰', text: 'Payments' },
            { view: 'admin-logs', icon: '📋', text: 'Activity Logs' }
        );
    }
    
    menuItems.forEach(item => {
        const button = document.createElement('button');
        button.className = 'menu-item';
        button.dataset.view = item.view;
        button.innerHTML = `<span>${item.icon}</span> ${item.text}`;
        button.addEventListener('click', () => {
            document.querySelectorAll('.menu-item').forEach(b => b.classList.remove('active'));
            button.classList.add('active');
            showView(item.view);
        });
        menu.appendChild(button);
    });
    
    // Set first item as active
    if (menuItems.length > 0) {
        menu.firstElementChild.classList.add('active');
    }
}

// Show different views
function showView(view) {
    const content = document.getElementById('content');

    switch(view) {
        case 'home':
            content.innerHTML = `
                <div class="view-header">
                    <h2>Dashboard</h2>
                </div>
                <div id="bibleQuote"></div>
                <div class="dashboard-grid">
                    <div class="card">
                        <h3>📚 Quick Stats</h3>
                        <p><strong>Role:</strong> ${currentUser.role || userRole}</p>
                        <p><strong>Class:</strong> ${currentUser.class || 'N/A'}</p>
                        <p><strong>Stream:</strong> ${currentUser.stream || 'N/A'}</p>
                    </div>
                    <div class="card">
                        <h3>📝 Latest Updates</h3>
                        <div id="homeUpdates"></div>
                    </div>
                </div>
            `;
            displayRandomBibleQuote();
            loadLatestUpdates();
            break;

        case 'teachers':
            loadTeachers();
            break;

        case 'assignments':
            loadAssignments();
            break;

        case 'updates':
            loadUpdates();
            break;

        case 'timetable':
            loadTimetable();
            break;

        case 'subjects':
            loadSubjects();
            break;

        case 'students':
            loadStudents();
            break;

        // Admin views
        case 'admin-users':
            loadAdminUsers();
            break;
        case 'admin-payments':
            loadAdminPayments();
            break;
        case 'admin-logs':
            loadAdminLogs();
            break;
    }
}

// Load teachers
async function loadTeachers() {
    const content = document.getElementById('content');
    content.innerHTML = `<div class="view-header"><h2>Teachers</h2></div><div class="loading">Loading teachers...</div>`;

    try {
        const response = await fetch('/api/teachers');
        const data = await response.json();

        if (data.success) {
            let html = `<div class="view-header"><h2>Teachers</h2>
                        <input type="text" id="searchTeachers" placeholder="Search by name or subject..." class="search-input" onkeyup="filterTeachers()">
                    </div>
                    <div class="teachers-grid" id="teachersGrid">`;

            data.teachers.forEach(teacher => {
                html += `
                    <div class="teacher-card">
                        <div class="teacher-avatar">${teacher.photo ? `<img src="${teacher.photo}" alt="${teacher.fullName}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" />` : teacher.fullName.charAt(0)}</div>
                        <h3>${teacher.fullName}</h3>
                        <p class="teacher-meta">${teacher.stream ? `${teacher.stream} / ${teacher.class || 'Class'}` : ''}</p>
                        <p class="teacher-meta"><strong>Subjects:</strong> ${teacher.subjects}</p>
                        <p class="teacher-quote">"${teacher.quote}"</p>
                        <button class="btn btn-primary" onclick="chatWithTeacher('${teacher.id}', '${teacher.fullName}')">
                            💬 Consult
                        </button>
                    </div>
                `;
            });

            html += '</div>';
            content.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading teachers:', error);
        content.innerHTML = `<div class="view-header"><h2>Teachers</h2></div><p>Failed to load teachers.</p>`;
    }
}

function loadAssignments() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="view-header">
            <h2>Assignments</h2>
        </div>
    `;

    const canPost = userRole === 'teacher';
    if (canPost) {
        content.innerHTML += `
            <div class="assignment-form">
                <h3>Post Assignment</h3>
                <input id="assignmentSubject" placeholder="Subject" />
                <input id="assignmentTitle" placeholder="Title" />
                <textarea id="assignmentDescription" rows="4" placeholder="Instructions"></textarea>
                <input id="assignmentDueDate" type="date" />
                <button class="btn btn-primary" onclick="submitAssignment()">Post Assignment</button>
            </div>
        `;
    }

    content.innerHTML += `<div id="assignmentList"></div>`;
    fetch(`/api/assignments?stream=${encodeURIComponent(currentUser.stream || '')}&class=${encodeURIComponent(currentUser.class || '')}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const assignmentsHtml = data.assignments.map(item => `
                    <div class="card">
                        <h3>${item.subject} — ${item.title}</h3>
                        <p>${item.description}</p>
                        <p><strong>Teacher:</strong> ${item.teacher_name}</p>
                        <p><strong>Due:</strong> ${item.due_date || 'N/A'}</p>
                    </div>
                `).join('');
                document.getElementById('assignmentList').innerHTML = assignmentsHtml || '<p>No assignments for your class/stream yet.</p>';
            }
        }).catch(error => {
            console.error('Error loading assignments:', error);
            document.getElementById('assignmentList').innerHTML = '<p>Failed to load assignments.</p>';
        });
}

function submitAssignment() {
    const subject = document.getElementById('assignmentSubject').value.trim();
    const title = document.getElementById('assignmentTitle').value.trim();
    const description = document.getElementById('assignmentDescription').value.trim();
    const dueDate = document.getElementById('assignmentDueDate').value;

    if (!subject || !title || !description) {
        showNotification('Please fill all assignment fields', 'error');
        return;
    }

    fetch('/api/assignments', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            teacher_id: currentUser.id,
            teacher_name: currentUser.fullName,
            stream: currentUser.stream || '',
            class: currentUser.class || '',
            subject,
            title,
            description,
            due_date: dueDate
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showNotification('Assignment posted successfully', 'success');
            loadAssignments();
        } else {
            showNotification('Failed to post assignment', 'error');
        }
    }).catch(error => {
        console.error('Assignment error:', error);
        showNotification('Assignment error', 'error');
    });
}

function loadUpdates() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="view-header">
            <h2>Updates</h2>
        </div>
    `;

    if (isUpdatePoster()) {
        content.innerHTML += `
            <div class="update-form">
                <h3>Post Announcement</h3>
                <input id="updateTitle" placeholder="Announcement title" />
                <textarea id="updateMessage" rows="4" placeholder="Message"></textarea>
                <button class="btn btn-primary" onclick="submitUpdate()">Post Announcement</button>
            </div>
        `;
    }

    content.innerHTML += `<div id="updatesList"></div>`;
    fetch('/api/updates')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const html = data.updates.map(item => `
                    <div class="card">
                        <h3>${item.title}</h3>
                        <p><small>${new Date(item.created_at).toLocaleString()}</small></p>
                        <p>${item.message}</p>
                        <p><strong>Posted by:</strong> ${item.fullName} (${item.role})</p>
                    </div>
                `).join('');
                document.getElementById('updatesList').innerHTML = html || '<p>No updates posted yet.</p>';
            }
        }).catch(error => {
            console.error('Error loading updates:', error);
            document.getElementById('updatesList').innerHTML = '<p>Failed to load updates.</p>';
        });
}

function loadLatestUpdates() {
    fetch('/api/updates')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const html = data.updates.slice(0, 2).map(item => `
                    <div>
                        <h4>${item.title}</h4>
                        <p>${item.message}</p>
                        <p><small>${new Date(item.created_at).toLocaleDateString()}</small></p>
                    </div>
                `).join('');
                document.getElementById('homeUpdates').innerHTML = html || '<p>No recent updates yet.</p>';
            }
        }).catch(() => {
            document.getElementById('homeUpdates').innerHTML = '<p>Could not load recent updates.</p>';
        });
}

function submitUpdate() {
    const title = document.getElementById('updateTitle').value.trim();
    const message = document.getElementById('updateMessage').value.trim();

    if (!title || !message) {
        showNotification('Please enter title and message', 'error');
        return;
    }

    fetch('/api/updates', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: currentUser.id,
            fullName: currentUser.fullName,
            role: currentUser.role || userRole,
            title,
            message
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showNotification('Announcement posted', 'success');
            loadUpdates();
        } else {
            showNotification('Failed to post announcement', 'error');
        }
    }).catch(error => {
        console.error('Update error:', error);
        showNotification('Update error', 'error');
    });
}

function loadTimetable() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="view-header">
            <h2>Timetable</h2>
        </div>
        <div id="timetableContent"></div>
    `;

    const stream = currentUser.stream || 'default';
    fetch(`/api/timetable/${encodeURIComponent(stream)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const rows = data.timetable.map(item => `
                    <tr>
                        <td>${item.time}</td>
                        <td>${item.monday}</td>
                        <td>${item.tuesday}</td>
                        <td>${item.wednesday}</td>
                        <td>${item.thursday}</td>
                        <td>${item.friday}</td>
                    </tr>
                `).join('');

                document.getElementById('timetableContent').innerHTML = `
                    <div class="timetable">
                        <table>
                            <tr>
                                <th>Time</th>
                                <th>Monday</th>
                                <th>Tuesday</th>
                                <th>Wednesday</th>
                                <th>Thursday</th>
                                <th>Friday</th>
                            </tr>
                            ${rows}
                        </table>
                    </div>
                `;
            } else {
                document.getElementById('timetableContent').innerHTML = '<p>No timetable found for this stream.</p>';
            }
        }).catch(error => {
            console.error('Timetable error:', error);
            document.getElementById('timetableContent').innerHTML = '<p>Failed to load timetable.</p>';
        });
}

function loadSubjects() {
    const content = document.getElementById('content');
    const subjects = [
        'Mathematics',
        'English',
        'Biology',
        'Chemistry',
        'Physics',
        'Geography',
        'History',
        'Kiswahili',
        'CRE',
        'Literature',
        'Technology and Design',
        'Art and Design',
        'German',
        'Food and Nutrition',
        'Information and Communication Technology',
        'Chinese',
        'Performing Arts',
        'Entrepreneurship',
        'Agriculture',
        'French',
        'Physical Education'
    ];

    content.innerHTML = `
        <div class="view-header">
            <h2>Subjects</h2>
        </div>
        <div class="subjects-grid">
            ${subjects.map(subject => `
                <div class="card">
                    <h3>📚 ${subject}</h3>
                    <button class="btn btn-secondary" onclick="window.location.href='subject-detail.html?subject=${encodeURIComponent(subject)}&class=${encodeURIComponent(currentUser.class || '')}&stream=${encodeURIComponent(currentUser.stream || '')}'">View Topics</button>
                </div>
            `).join('')}
        </div>
    `;
}

function loadStudents() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="view-header">
            <h2>Students</h2>
        </div>
        <div id="studentsSection">Loading students...</div>
    `;

    fetch('/api/students')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const rows = data.students.map(student => `
                    <tr>
                        <td><img src="${student.photo || 'mengo badge.jpg'}" alt="photo" /></td>
                        <td>${student.fullName}</td>
                        <td>${student.class || 'N/A'}</td>
                        <td>${student.stream || 'N/A'}</td>
                        <td>${student.id}</td>
                        <td>${student.role || 'Student'}</td>
                    </tr>
                `).join('');

                document.getElementById('studentsSection').innerHTML = `
                    <table class="data-table students-table">
                        <thead>
                            <tr>
                                <th>Photo</th>
                                <th>Name</th>
                                <th>Class</th>
                                <th>Stream</th>
                                <th>Index</th>
                                <th>Role</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                `;
            } else {
                document.getElementById('studentsSection').innerHTML = '<p>Failed to load students.</p>';
            }
        }).catch(error => {
            console.error('Student list error:', error);
            document.getElementById('studentsSection').innerHTML = '<p>Error loading students.</p>';
        });
}

function chatWithTeacher(teacherId, teacherName) {
    window.location.href = `teacher-chat.html?teacherId=${encodeURIComponent(teacherId)}&name=${encodeURIComponent(teacherName)}`;
}

// Filter teachers
function filterTeachers() {
    const searchTerm = document.getElementById('searchTeachers').value.toLowerCase();
    const cards = document.querySelectorAll('.teacher-card');

    cards.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        const subjects = Array.from(card.querySelectorAll('.teacher-meta'))
            .map(el => el.textContent.toLowerCase())
            .join(' ');

        if (name.includes(searchTerm) || subjects.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// Show notification
function showNotification(message, type = 'success') {
    const notif = document.getElementById('notification');
    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.classList.remove('hidden');

    setTimeout(() => {
        notif.classList.add('hidden');
    }, 3000);
}

// Logout
function logout() {
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('is_admin');
    document.cookie = 'mengo_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = 'index.html';
}

// Admin functions
async function loadAdminUsers() {
    const content = document.getElementById('content');
    
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();
        
        if (data.success) {
            const usersHtml = data.users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.fullName}</td>
                    <td>${user.type}</td>
                    <td>${user.is_admin ? 'Yes' : 'No'}</td>
                    <td>
                        <select onchange="updatePaymentStatus('${user.id}', '${user.type}', this.value)">
                            <option value="unpaid" ${user.payment_status === 'unpaid' ? 'selected' : ''}>Unpaid</option>
                            <option value="paid" ${user.payment_status === 'paid' ? 'selected' : ''}>Paid</option>
                        </select>
                    </td>
                </tr>
            `).join('');
            
            content.innerHTML = `
                <div class="view-header">
                    <h2>User Management</h2>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Full Name</th>
                            <th>Type</th>
                            <th>Admin</th>
                            <th>Payment Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${usersHtml}
                    </tbody>
                </table>
            `;
        } else {
            content.innerHTML = '<p class="error">Failed to load users</p>';
        }
    } catch (error) {
        content.innerHTML = '<p class="error">Error loading users</p>';
    }
}

async function loadAdminPayments() {
    const content = document.getElementById('content');
    
    try {
        const response = await fetch('/api/admin/payments');
        const data = await response.json();
        
        if (data.success) {
            const paymentsHtml = data.payments.map(payment => `
                <tr>
                    <td>${payment.user_id}</td>
                    <td>${payment.user_type}</td>
                    <td>${payment.transaction_id}</td>
                    <td>UGX ${payment.amount}</td>
                    <td>${payment.status}</td>
                    <td>${new Date(payment.created_at).toLocaleString()}</td>
                </tr>
            `).join('');
            
            content.innerHTML = `
                <div class="view-header">
                    <h2>Payment Records</h2>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Type</th>
                            <th>Transaction ID</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${paymentsHtml}
                    </tbody>
                </table>
            `;
        } else {
            content.innerHTML = '<p class="error">Failed to load payments</p>';
        }
    } catch (error) {
        content.innerHTML = '<p class="error">Error loading payments</p>';
    }
}

async function loadAdminLogs() {
    const content = document.getElementById('content');
    
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.success) {
            const logsHtml = data.logs.map(log => `
                <tr>
                    <td>${log.userId}</td>
                    <td>${log.userType}</td>
                    <td>${log.username}</td>
                    <td>${log.action || 'login'}</td>
                    <td>${log.ipAddress}</td>
                    <td>${new Date(log.loginTime).toLocaleString()}</td>
                </tr>
            `).join('');
            
            content.innerHTML = `
                <div class="view-header">
                    <h2>Activity Logs</h2>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Type</th>
                            <th>Username</th>
                            <th>Action</th>
                            <th>IP</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logsHtml}
                    </tbody>
                </table>
            `;
        } else {
            content.innerHTML = '<p class="error">Failed to load logs</p>';
        }
    } catch (error) {
        content.innerHTML = '<p class="error">Error loading logs</p>';
    }
}

async function updatePaymentStatus(userId, userType, status) {
    try {
        const response = await fetch('/api/admin/update-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, user_type: userType, status })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Payment status updated', 'success');
        } else {
            showNotification('Update failed: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Update error:', error);
        showNotification('Update error', 'error');
    }
}

// Check auth on page load
window.addEventListener('load', checkAuth);
