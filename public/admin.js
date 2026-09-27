// Admin Panel JavaScript
let currentView = 'overview';
const DB_NAME = 'MengoHubCertificates';
const CERT_STORE = 'certificates';
const ADMIN_API_TOKEN = 'MengoAdminAPIToken2026';

function adminFetch(url, options = {}) {
    const token = sessionStorage.getItem('adminToken') || ADMIN_API_TOKEN;
    const headers = options.headers || {};
    headers.Authorization = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
}

//function openDB() {
//    return new Promise((resolve, reject) => {
//        const request = indexedDB.open(DB_NAME, 1);
//        request.onerror = () => reject(request.error);
//        request.onsuccess = () => resolve(request.result);
//        request.onupgradeneeded = (event) => {
//            const db = event.target.result;
//            if (!db.objectStoreNames.contains(CERT_STORE)) {
//                db.createObjectStore(CERT_STORE, { keyPath: 'serialNumber' });
//            }
//        };
//    });
//}

//async function getAllCertificates() {
//    const db = await openDB();
//    const transaction = db.transaction([CERT_STORE], 'readonly');
//    const store = transaction.objectStore(CERT_STORE);
//    return new Promise((resolve, reject) => {
//        const request = store.getAll();
//        request.onsuccess = () => resolve(request.result);
//        request.onerror = () => reject(request.error);
//    });
//}

function getCurrentAdminInfo() {
    const userId = sessionStorage.getItem('adminUserId') || '';
    const username = sessionStorage.getItem('adminUserName') || '';
    return {
        userId,
        username,
        isSuperAdmin: userId === 'A000' || username.toLowerCase() === 'newton'
    };
}

//async function verifyAdminAccess() {
//    try {
//        const response = await adminFetch('/api/admin');
//        const data = await response.json();
//        if (!data.success) {
//            throw new Error('Admin verification failed');
//        }
//    } catch (error) {
//        console.error('Admin access verification failed:', error);
//        alert('Admin access could not be verified. Please reinstall the certificate or contact support.');
//        window.location.href = 'install.html';
//    }
//}


function applyAdminRestrictions() {
    const { isSuperAdmin } = getCurrentAdminInfo();
    const restricted = ['users', 'account-check'];

    restricted.forEach(view => {
        const menuItem = document.querySelector(`[data-view="${view}"]`);
        if (menuItem) {
            menuItem.style.display = isT000 ? 'flex' : 'none';
        }
    });
}

function denyRestrictedView(contentArea, viewName) {
    contentArea.innerHTML = `
        <h2>Restricted Access</h2>
        <p>The <strong>${viewName}</strong> section is available only to the admin account <strong>Newton (T000)</strong>.</p>
        <p>Please use the overview, payments, logs, and other general admin tools.</p>
    `;
}

//window.addEventListener('load', () => {
//    loadAdminData();
//    setupMenuHandlers();
//});

function setupMenuHandlers() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const view = e.currentTarget.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    currentView = view;
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    // Load view content
    loadView(view);
}

async function loadView(view) {
    const contentArea = document.getElementById('content-area');

    try {
        switch (view) {

            case 'overview':
                await loadOverview();
                break;

            case 'users':
                if (!getCurrentAdminInfo().isT000) {
                    denyRestrictedView(contentArea, 'User Accounts');
                    break;
                }
                await loadUsers();
                break;

            case 'account-check':
                if (!getCurrentAdminInfo().isT000) {
                    denyRestrictedView(contentArea, 'Account Check');
                    break;
                }
                await loadAccountCheck();
                break;

            case 'payments':
                await loadPayments();
                break;

            case 'feedback':
                await loadFeedbacks();
                break;

            case 'logs':
                await loadLogs();
                break;

            case 'system-health':
                await loadSystemHealth();
                break;

            case 'audit':
                await loadSecurityAudit();
                break;

            case 'add-account':
                loadAddAccount();
                break;

            case 'media':
                loadMediaManager();
                break;

            case 'refresh':
                loadSystemRefresh();
                break;

            case 'recovery':
                loadRecovery();
                break;

            case 'certificates':
                //loadCertificates();
            case 'certificates':
                contentArea.innerHTML = `
                <div class="card">
                    <h2>Certificate Management</h2>
                    <p>Certificate management is temporarily disabled.</p>
                    <p>We will implement this module later.</p>
                </div>
            `;
            break;

            case 'feature-controls':
                await loadFeatureToggles();
                break;

            case 'email-management':
                await loadEmailManagement();
                break;

            case 'ai-configuration':
                await loadAIConfiguration();
                break;

            case 'certificate-manager':
                await loadCertificateManager();
                break;

            case 'system-logs':
                await loadSystemLogs();
                break;

            case 'n8n-webhooks':
                await loadN8NWebhooks();
                break;

            case '3d-models':
                await load3DModels();
                break;

            case 'audio-beats':
                await loadAudioBeats();
                break;

            default:
                contentArea.innerHTML = `
                    <div class="card">
                        <h2>Unknown Admin View</h2>
                        <p>No handler exists for:</p>
                        <code>${view}</code>
                    </div>
                `;
        }

    } catch (error) {
        console.error(`Error loading view "${view}":`, error);

        contentArea.innerHTML = `
            <div class="card">
                <h2>Tool Error</h2>
                <p>Could not load <strong>${view}</strong>.</p>
                <pre>${error.message}</pre>
            </div>
        `;
    }
}

//async function loadAdminData() {
    // Check for admin certificate in IndexedDB
//    const DB_NAME = 'MengoHubCertificates';
//    const CERT_STORE = 'certificates';
//
//    function openDB() {
//        return new Promise((resolve, reject) => {
//            const request = indexedDB.open(DB_NAME, 1);
//            request.onerror = () => reject(request.error);
//            request.onsuccess = () => resolve(request.result);
//            request.onupgradeneeded = (event) => {
//                const db = event.target.result;
//                if (!db.objectStoreNames.contains(CERT_STORE)) {
//                    db.createObjectStore(CERT_STORE, { keyPath: 'serialNumber' });
//                }
//            };
//        });
//    }

//    try {
//        const certificates = await getAllCertificates();
//        const adminCerts = certificates.filter(cert =>
//            cert.extensions.certificateType === 'admin'
//        );

//        if (adminCerts.length === 0) {
//            // No admin certificate found, redirect to install
//            alert('Admin certificate required. Redirecting to certificate installation.');
//            window.location.href = 'install.html';
//            return;
//        }

        // Find the most recent valid admin certificate
//        const now = new Date();
//        const validAdminCerts = adminCerts.filter(cert => {
//            const notAfter = new Date(cert.validity.notAfter);
//            return now <= notAfter;
//        });

//        if (validAdminCerts.length === 0) {
//            alert('Admin certificate expired. Redirecting to certificate renewal.');
//            window.location.href = 'install.html';
//            return;
//        }

        // Use the most recent admin certificate
//        const adminCert = validAdminCerts.sort((a, b) =>
//            new Date(b.extensions.issuedDate) - new Date(a.extensions.issuedDate)
//        )[0];

        // Admin access granted
//        sessionStorage.setItem('is_admin', true);
//        sessionStorage.setItem('adminUserId', adminCert.extensions.userId || '');
//        sessionStorage.setItem('adminUserName', adminCert.subject?.commonName || '');
//        sessionStorage.setItem('adminToken', ADMIN_API_TOKEN);
//        applyAdminRestrictions();
//        await verifyAdminAccess();
//        loadView('overview');
//    } catch (error) {
//        console.error('Certificate check error:', error);
//        alert('Certificate verification failed. Redirecting to installation.');
//        window.location.href = 'install.html';
//    }
//}


async function loadAdminData() {
    try {
        const response = await adminFetch('/api/admin/users');
        if (!response.ok) {
            throw new Error(`Admin API returned ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || 'Admin verification failed');
        }

        sessionStorage.setItem('is_admin', 'true');
        applyAdminRestrictions();
        await loadView('overview');

    } catch (error) {
        console.error('[Admin] initialization failed:', error);

        document.getElementById('content-area').innerHTML = `
            <div class="card">
                <h2>Admin Initialization Error</h2>
                <p>${error.message}</p>
                <button class="btn btn-primary" onclick="loadAdminData()">
                    Retry
                </button>
            </div>
        `;
    }
}

// Feature Toggles
async function loadFeatureToggles() {
    try {
        const res = await fetch('/api/admin/feature-toggles', {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        const data = await res.json();
        
        if (data.success) {
            const html = `
                <div class="admin-controls">
                    <h2>Feature Controls</h2>
                    <div class="toggle-grid">
                        ${Object.entries(data.features || {}).map(([key, val]) => `
                            <div class="toggle-item">
                                <label>${key.replace(/_/g, ' ')}</label>
                                <input type="checkbox" 
                                       id="toggle_${key}" 
                                       ${val ? 'checked' : ''} 
                                       onchange="updateFeature('${key}', this.checked)">
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document.getElementById('content-area').innerHTML = html;
        }
    } catch (e) {
        console.error(e);
    }
}

async function updateFeature(key, enabled) {
    const payload = {};
    payload[key] = enabled;
    
    const res = await fetch('/api/admin/feature-toggles', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showNotification(data.message);
}

// Email Configuration
async function configureEmail() {
    const provider = document.getElementById('emailProvider').value;
    const payload = {
        admin_id: 'A000',
        provider: provider,
        config: {
            smtp_server: document.getElementById('smtpServer').value,
            smtp_port: parseInt(document.getElementById('smtpPort').value),
            sender_email: document.getElementById('senderEmail').value
        }
    };
    
    const res = await fetch('/api/admin/email-config', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showNotification(data.message);
}

async function testEmailConfig() {
    const email = document.getElementById('testEmail').value;
    
    const res = await fetch('/api/admin/email-config/test', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ to_email: email })
    });
    const data = await res.json();
    showNotification(data.success ? 'Test email sent!' : 'Failed to send test email');
}

// Certificate Manager
async function validateCertificate() {
    const userId = document.getElementById('userIdToValidate').value;
    
    const res = await fetch(`/api/admin/validate-certificate?user_id=${userId}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    const data = await res.json();
    
    const html = `
        <div class="validation-result">
            <p>User: ${userId}</p>
            <p>Is Admin: ${data.is_admin ? 'YES' : 'NO'}</p>
            <p>Has Certificate: ${data.has_certificate ? 'YES' : 'NO'}</p>
            <p>Status: ${data.message}</p>
        </div>
    `;
    document.getElementById('certResult').innerHTML = html;
}

async function loadOverview() {
    const contentArea = document.getElementById('content-area');
    
    try {
        // Get users count
        const usersResponse = await adminFetch('/api/admin/users');
        const usersData = await usersResponse.json();
        
        // Get payments count
        const paymentsResponse = await adminFetch('/api/admin/payments');
        const paymentsData = await paymentsResponse.json();
        
        // Get logs count
        const logsResponse = await adminFetch('/api/logs');
        const logsData = await logsResponse.json();
        
        const totalUsers = usersData.users ? usersData.users.length : 0;
        const totalPayments = paymentsData.payments ? paymentsData.payments.length : 0;
        const totalLogs = logsData.logs ? logsData.logs.length : 0;
        
        const paidUsers = usersData.users ? usersData.users.filter(u => u.payment_status === 'paid').length : 0;
        
        contentArea.innerHTML = `
            <div class="overview-grid">
                <div class="stat-card">
                    <h3>Total Users</h3>
                    <div class="stat-number">${totalUsers}</div>
                </div>
                <div class="stat-card">
                    <h3>Paid Users</h3>
                    <div class="stat-number">${paidUsers}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Payments</h3>
                    <div class="stat-number">${totalPayments}</div>
                </div>
                <div class="stat-card">
                    <h3>Activity Logs</h3>
                    <div class="stat-number">${totalLogs}</div>
                </div>
            </div>
            <div class="quick-actions">
                <h3>Quick Actions</h3>
                ${getCurrentAdminInfo().isT000 ? `<button class="btn btn-primary" onclick="switchView('users')">Manage Users</button>` : ''}
                <button class="btn btn-primary" onclick="switchView('payments')">View Payments</button>
                <button class="btn btn-primary" onclick="switchView('logs')">View Logs</button>
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML = '<p class="error">Failed to load overview data</p>';
    }
}


async function loadDashboardStats() {
    const res = await fetch('/api/admin/reports', {
        headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    const data = await res.json();
    
    const stats = data.report;
    const html = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>${stats.student_count}</h3>
                <p>Total Students</p>
            </div>
            <div class="stat-card">
                <h3>${stats.teacher_count}</h3>
                <p>Teachers</p>
            </div>
            <div class="stat-card">
                <h3>${stats.admin_count}</h3>
                <p>Admins</p>
            </div>
            <div class="stat-card">
                <h3>${stats.unresolved_payments || 0}</h3>
                <p>Pending Payments</p>
            </div>
        </div>
    `;
    document.getElementById('dashStats').innerHTML = html;
}

async function loadUsers() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>User Accounts</h2>
        <p>This section is for admin review only. Inspect all students, teachers, and admin users carefully before granting access.</p>
        <div id="userCounts" class="overview-grid"></div>
        <div id="userTables"></div>
    `;

    try {
        const [usersResponse, adminsResponse] = await Promise.all([
            adminFetch('/api/admin/users'),
            adminFetch('/api/admin/admins')
        ]);

        const usersData = await usersResponse.json();
        const adminsData = await adminsResponse.json();

        if (!usersData.success || !adminsData.success) {
            contentArea.innerHTML = '<p class="error">Failed to load user accounts</p>';
            return;
        }

        const users = usersData.users || [];
        const admins = adminsData.admins || [];
        const students = users.filter(user => user.type === 'student');
        const teachers = users.filter(user => user.type === 'teacher');

        students.sort((a, b) => (a.fullName || a.username).localeCompare(b.fullName || b.username));
        teachers.sort((a, b) => (a.fullName || a.username).localeCompare(b.fullName || b.username));
        admins.sort((a, b) => (a.fullName || a.username).localeCompare(b.fullName || b.username));

        document.getElementById('userCounts').innerHTML = `
            <div class="stat-card"><h3>Students</h3><div class="stat-number">${students.length}</div></div>
            <div class="stat-card"><h3>Teachers</h3><div class="stat-number">${teachers.length}</div></div>
            <div class="stat-card"><h3>Admins</h3><div class="stat-number">${admins.length}</div></div>
            <div class="stat-card"><h3>Total Users</h3><div class="stat-number">${users.length}</div></div>
        `;

        const renderTable = (title, rows, fields) => `
            <div class="card">
                <h3>${title}</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            ${fields.map(field => `<th>${field.label}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${rows.map(row => `
                            <tr>
                                ${fields.map(field => `<td>${field.render(row)}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        document.getElementById('userTables').innerHTML = `
            ${renderTable('Students', students, [
                { label: 'ID', render: r => r.id },
                { label: 'Username', render: r => r.username },
                { label: 'Full Name', render: r => r.fullName },
                { label: 'Email', render: r => r.email || 'N/A' },
                { label: 'Class', render: r => r.class || 'N/A' },
                { label: 'Stream', render: r => r.stream || 'N/A' },
                { label: 'Role', render: r => r.role || 'Student' },
                { label: 'Admin', render: r => r.is_admin ? 'Yes' : 'No' },
                { label: 'Paid', render: r => r.payment_status || 'unpaid' }
            ])}
            ${renderTable('Teachers', teachers, [
                { label: 'ID', render: r => r.id },
                { label: 'Username', render: r => r.username },
                { label: 'Full Name', render: r => r.fullName },
                { label: 'Email', render: r => r.email || 'N/A' },
                { label: 'Subjects', render: r => r.subjects || 'N/A' },
                { label: 'Class', render: r => r.class || 'N/A' },
                { label: 'Stream', render: r => r.stream || 'N/A' },
                { label: 'Role', render: r => r.role || 'Teacher' },
                { label: 'Admin', render: r => r.is_admin ? 'Yes' : 'No' },
                { label: 'Paid', render: r => r.payment_status || 'unpaid' }
            ])}
            ${renderTable('Admin Users', admins, [
                { label: 'ID', render: r => r.id },
                { label: 'Username', render: r => r.username },
                { label: 'Full Name', render: r => r.fullName },
                { label: 'Email', render: r => r.email || 'N/A' },
                { label: 'Type', render: r => r.type || 'N/A' },
                { label: 'Class', render: r => r.class || 'N/A' },
                { label: 'Stream', render: r => r.stream || 'N/A' },
                { label: 'Role', render: r => r.role || 'N/A' }
            ])}
        `;
    } catch (error) {
        contentArea.innerHTML = '<p class="error">Error loading user accounts</p>';
    }
}

async function loadAccountCheck() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>Account Check</h2>
        <p>Review registered users, their active details, and recent activity logs.</p>
        <div class="overview-grid" id="accountStats"></div>
        <div class="card" id="accountDetails"></div>
        <div class="card" id="recentActivities"></div>
    `;

    try {
        const [usersRes, logsRes] = await Promise.all([
            adminFetch('/api/admin/users'),
            adminFetch('/api/logs')
        ]);
        const usersData = await usersRes.json();
        const logsData = await logsRes.json();

        const users = usersData.users || [];
        const logs = logsData.logs || [];
        const userCount = users.length;
        const paidCount = users.filter(u => u.payment_status === 'paid').length;
        const adminCount = users.filter(u => u.is_admin).length;
        const recentLogs = logs.slice(0, 10);

        document.getElementById('accountStats').innerHTML = `
            <div class="stat-card"><h3>Total Users</h3><div class="stat-number">${userCount}</div></div>
            <div class="stat-card"><h3>Paid Users</h3><div class="stat-number">${paidCount}</div></div>
            <div class="stat-card"><h3>Admins</h3><div class="stat-number">${adminCount}</div></div>
        `;

        document.getElementById('accountDetails').innerHTML = `
            <h3>User Accounts</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Full Name</th>
                        <th>Email</th>
                        <th>Type</th>
                        <th>Role</th>
                        <th>Class</th>
                        <th>Stream</th>
                        <th>Payment</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.username}</td>
                            <td>${user.fullName}</td>
                            <td>${user.email || 'N/A'}</td>
                            <td>${user.type}</td>
                            <td>${user.role || 'N/A'}</td>
                            <td>${user.class || 'N/A'}</td>
                            <td>${user.stream || 'N/A'}</td>
                            <td>${user.payment_status || 'N/A'}</td>
                            <td>${user.is_admin ? 'Yes' : 'No'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        document.getElementById('recentActivities').innerHTML = `
            <h3>Recent Activity Logs</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Username</th>
                        <th>Action</th>
                        <th>IP</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentLogs.map(log => `
                        <tr>
                            <td>${log.userId}</td>
                            <td>${log.username}</td>
                            <td>${log.action || 'login'}</td>
                            <td>${log.ipAddress || 'N/A'}</td>
                            <td>${new Date(log.loginTime).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Account check error:', error);
        contentArea.innerHTML = '<p class="error">Failed to load account check details</p>';
    }
}

async function loadPayments() {
    const contentArea = document.getElementById('content-area');
    
    try {
        const response = await adminFetch('/api/admin/payments');
        const data = await response.json();
        
        if (data.success) {
            const paymentsHtml = data.payments.map(payment => `
                <tr>
                    <td>${payment.user_id}</td>
                    <td>${payment.user_type}</td>
                    <td>${payment.transaction_id}</td>
                    <td>UGX ${payment.amount}</td>
                    <td>${payment.payment_method}</td>
                    <td>${payment.status}</td>
                    <td>${new Date(payment.created_at).toLocaleString()}</td>
                </tr>
            `).join('');
            
            contentArea.innerHTML = `
                <h2>Payment Records</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>User Type</th>
                            <th>Transaction ID</th>
                            <th>Amount</th>
                            <th>Method</th>
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
            contentArea.innerHTML = '<p class="error">Failed to load payments</p>';
        }
    } catch (error) {
        contentArea.innerHTML = '<p class="error">Error loading payments</p>';
    }
}

async function loadFeedbacks() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>Feedback</h2>
        <p>Review user feedback submissions saved in the system.</p>
        <div id="feedbackSection"></div>
    `;

    try {
        const response = await fetch('/api/feedbacks');
        const data = await response.json();

        if (data.success) {
            document.getElementById('feedbackSection').innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>User</th>
                            <th>Email</th>
                            <th>Message</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.feedback.map(item => `
                            <tr>
                                <td>${item.id}</td>
                                <td>${item.fullName || 'Guest'}</td>
                                <td>${item.email || 'N/A'}</td>
                                <td>${item.message}</td>
                                <td>${new Date(item.created_at).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            document.getElementById('feedbackSection').innerHTML = '<p>No feedback available.</p>';
        }
    } catch (error) {
        console.error('Feedback load error:', error);
        document.getElementById('feedbackSection').innerHTML = '<p class="error">Failed to load feedback.</p>';
    }
}

async function loadLogs() {
    const contentArea = document.getElementById('content-area');
    
    try {
        const response = await adminFetch('/api/logs');
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
            
            contentArea.innerHTML = `
                <h2>Activity Logs</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>User Type</th>
                            <th>Username</th>
                            <th>Action</th>
                            <th>IP Address</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logsHtml}
                    </tbody>
                </table>
            `;
        } else {
            contentArea.innerHTML = '<p class="error">Failed to load logs</p>';
        }
    } catch (error) {
        contentArea.innerHTML = '<p class="error">Error loading logs</p>';
    }
}

function loadRecovery() {
    const contentArea = document.getElementById('content-area');
    
    contentArea.innerHTML = `
        <h2>Recovery Tools</h2>
        <div class="recovery-form">
            <h3>Reset User Password</h3>
            <form onsubmit="handlePasswordReset(event)">
                <div class="form-group">
                    <label for="resetUsername">Username</label>
                    <input type="text" id="resetUsername" required>
                </div>
                <div class="form-group">
                    <label for="resetRole">Role</label>
                    <select id="resetRole" required>
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="newPassword">New Password</label>
                    <input type="password" id="newPassword" required>
                </div>
                <button type="submit" class="btn btn-primary">Reset Password</button>
            </form>
        </div>
    `;
}

async function handlePasswordReset(event) {
    event.preventDefault();
    
    const username = document.getElementById('resetUsername').value;
    const role = document.getElementById('resetRole').value;
    const newPassword = document.getElementById('newPassword').value;
    
    try {
        const response = await fetch('/api/recover', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, role, new_password: newPassword })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Password reset successful');
            document.getElementById('resetUsername').value = '';
            document.getElementById('newPassword').value = '';
        } else {
            alert('Password reset failed: ' + data.message);
        }
    } catch (error) {
        console.error('Recovery error:', error);
        alert('Recovery error');
    }
}

async function updatePaymentStatus(userId, userType, status) {
    try {
        const response = await adminFetch('/api/admin/update-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, user_type: userType, status })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Payment status updated');
        } else {
            alert('Update failed: ' + data.message);
        }
    } catch (error) {
        console.error('Update error:', error);
        alert('Update error');
    }
}

function logout() {
    sessionStorage.clear();
    localStorage.removeItem('mengo_certificate');
    document.cookie = 'mengo_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = 'index.html';
}

async function loadSystemHealth() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>System Health</h2>
        <div id="systemHealthSummary" class="overview-grid"></div>
        <div class="card">
            <h3>Database and Memory</h3>
            <pre id="healthDetails">Loading system health data...</pre>
        </div>
    `;

    try {
        const [usersRes, paymentsRes, logsRes] = await Promise.all([
            adminFetch('/api/admin/users'),
            adminFetch('/api/admin/payments'),
            adminFetch('/api/logs')
        ]);

        const usersData = await usersRes.json();
        const paymentsData = await paymentsRes.json();
        const logsData = await logsRes.json();

        const users = usersData.users || [];
        const payments = paymentsData.payments || [];
        const logs = logsData.logs || [];

        const activeUsers = users.filter(u => u.payment_status === 'paid').length;
        const adminUsers = users.filter(u => u.is_admin).length;

        document.getElementById('systemHealthSummary').innerHTML = `
            <div class="stat-card"><h3>Users</h3><div class="stat-number">${users.length}</div></div>
            <div class="stat-card"><h3>Active Paid</h3><div class="stat-number">${activeUsers}</div></div>
            <div class="stat-card"><h3>Admins</h3><div class="stat-number">${adminUsers}</div></div>
            <div class="stat-card"><h3>Recent Logs</h3><div class="stat-number">${logs.length}</div></div>
        `;

        document.getElementById('healthDetails').textContent = JSON.stringify({
            totalUsers: users.length,
            activePaidUsers: activeUsers,
            adminUsers,
            totalPayments: payments.length,
            totalLogs: logs.length,
            lastUpdated: new Date().toISOString()
        }, null, 2);
    } catch (error) {
        document.getElementById('healthDetails').textContent = 'Unable to load health data.';
        console.error('System health error:', error);
    }
}

async function loadSecurityAudit() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>Security Audit</h2>
        <p>Review suspicious login activity and feedback for potential risks.</p>
        <div id="auditResults"></div>
    `;

    try {
        const response = await adminFetch('/api/admin/suspicious');
        const data = await response.json();

        if (data.success) {
            const suspicious = data.suspicious;
            document.getElementById('auditResults').innerHTML = `
                <h3>Failed Login Attempts</h3>
                <table class="data-table">
                    <thead><tr><th>User</th><th>Action</th><th>IP</th><th>Time</th></tr></thead>
                    <tbody>${suspicious.loginAttempts.map(log => `
                        <tr>
                            <td>${log.username || 'N/A'}</td>
                            <td>${log.action || 'failed_login'}</td>
                            <td>${log.ipAddress || 'N/A'}</td>
                            <td>${new Date(log.loginTime).toLocaleString()}</td>
                        </tr>
                    `).join('')}</tbody>
                </table>
                <h3>Brute Force Suspects</h3>
                <table class="data-table">
                    <thead><tr><th>Username</th><th>Attempts</th></tr></thead>
                    <tbody>${suspicious.bruteForce.map(item => `
                        <tr><td>${item.username}</td><td>${item.attempts}</td></tr>
                    `).join('')}</tbody>
                </table>
                <h3>Suspicious Feedback</h3>
                <table class="data-table">
                    <thead><tr><th>User</th><th>Email</th><th>Message</th><th>Date</th></tr></thead>
                    <tbody>${suspicious.suspiciousFeedback.map(item => `
                        <tr>
                            <td>${item.username || 'N/A'}</td>
                            <td>${item.email || 'N/A'}</td>
                            <td>${item.message || ''}</td>
                            <td>${new Date(item.created_at).toLocaleString()}</td>
                        </tr>
                    `).join('')}</tbody>
                </table>
            `;
        } else {
            document.getElementById('auditResults').innerHTML = '<p class="error">Failed to load audit information.</p>';
        }
    } catch (error) {
        console.error('Security audit error:', error);
        document.getElementById('auditResults').innerHTML = '<p class="error">Error loading audit details.</p>';
    }
}

function loadAddAccount() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>Add Account</h2>
        <form id="addAccountForm" class="card">
            <div class="form-group"><label>User Type</label><select id="newAccountType"><option value="student">Student</option><option value="teacher">Teacher</option></select></div>
            <div class="form-group"><label>ID</label><input id="newAccountId" type="text" required></div>
            <div class="form-group"><label>Username</label><input id="newAccountUsername" type="text" required></div>
            <div class="form-group"><label>Password</label><input id="newAccountPassword" type="password" required></div>
            <div class="form-group"><label>Full Name</label><input id="newAccountFullName" type="text" required></div>
            <div class="form-group"><label>Email</label><input id="newAccountEmail" type="email"></div>
            <div class="form-group"><label>Role</label><input id="newAccountRole" type="text" placeholder="e.g. class monitor"></div>
            <div class="form-group"><label>Class</label><input id="newAccountClass" type="text"></div>
            <div class="form-group"><label>Stream</label><input id="newAccountStream" type="text"></div>
            <div class="form-group"><label>Admin?</label><select id="newAccountIsAdmin"><option value="0">No</option><option value="1">Yes</option></select></div>
            <div class="form-group"><label>Payment Status</label><select id="newAccountPaymentStatus"><option value="unpaid">Unpaid</option><option value="paid">Paid</option></select></div>
            <button type="submit" class="btn btn-primary">Create Account</button>
        </form>
        <div id="accountResponse"></div>
    `;

    document.getElementById('addAccountForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = {
            type: document.getElementById('newAccountType').value,
            id: document.getElementById('newAccountId').value,
            username: document.getElementById('newAccountUsername').value,
            password: document.getElementById('newAccountPassword').value,
            fullName: document.getElementById('newAccountFullName').value,
            email: document.getElementById('newAccountEmail').value,
            role: document.getElementById('newAccountRole').value,
            class: document.getElementById('newAccountClass').value,
            stream: document.getElementById('newAccountStream').value,
            is_admin: document.getElementById('newAccountIsAdmin').value,
            payment_status: document.getElementById('newAccountPaymentStatus').value
        };

        try {
            const response = await adminFetch('/api/admin/add-account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            document.getElementById('accountResponse').textContent = result.success ? result.message : `Error: ${result.message}`;
        } catch (error) {
            console.error('Create account error:', error);
            document.getElementById('accountResponse').textContent = 'Failed to create account.';
        }
    });
}

function loadMediaManager() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>Media Manager</h2>
        <p>Upload or update user profile photos for students and teachers.</p>
        <form id="mediaForm" class="card">
            <div class="form-group"><label>User Type</label><select id="mediaUserType"><option value="student">Student</option><option value="teacher">Teacher</option></select></div>
            <div class="form-group"><label>User ID</label><input id="mediaUserId" type="text" required></div>
            <div class="form-group"><label>Photo File</label><input id="mediaPhotoFile" type="file" accept="image/*" required></div>
            <button type="submit" class="btn btn-primary">Upload Photo</button>
        </form>
        <div id="mediaResponse"></div>
    `;

    document.getElementById('mediaForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const userType = document.getElementById('mediaUserType').value;
        const userId = document.getElementById('mediaUserId').value;
        const fileInput = document.getElementById('mediaPhotoFile');

        if (!fileInput.files.length) {
            document.getElementById('mediaResponse').textContent = 'Please choose a file to upload.';
            return;
        }

        const file = fileInput.files[0];
        const reader = new FileReader();

        reader.onload = async () => {
            const payload = {
                user_type: userType,
                user_id: userId,
                filename: file.name,
                fileData: reader.result
            };

            try {
                const response = await adminFetch('/api/admin/upload-photo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                document.getElementById('mediaResponse').textContent = result.success ? result.message : `Error: ${result.message}`;
            } catch (error) {
                console.error('Media upload error:', error);
                document.getElementById('mediaResponse').textContent = 'Failed to upload photo.';
            }
        };

        reader.readAsDataURL(file);
    });
}

function loadSystemRefresh() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <h2>System Refresh</h2>
        <p>Run cleanup tasks, reload CSV imports, and refresh core data.</p>
        <button class="btn btn-primary" id="refreshSystemButton">Trigger Refresh</button>
        <div id="refreshResult" class="mt-3"></div>
    `;

    document.getElementById('refreshSystemButton').addEventListener('click', async () => {
        try {
            const response = await adminFetch('/api/admin/system-refresh', { method: 'POST' });
            const result = await response.json();
            document.getElementById('refreshResult').textContent = result.success ? result.message : `Error: ${result.message}`;
        } catch (error) {
            console.error('System refresh error:', error);
            document.getElementById('refreshResult').textContent = 'Failed to refresh system.';
        }
    });
}

function loadCertificates() {
    const contentArea = document.getElementById('content-area');

    contentArea.innerHTML = `
        <h2>Certificate Management</h2>
        <div class="certificate-section">
            <h3>Certificate Information</h3>
            <p>Certificate generation has been moved to the <a href="admin-install.html" target="_blank">Certificate Installation page</a> for better security and control.</p>
            <p><strong>Access Certificates:</strong> Automatically installed for all users visiting the site.</p>
            <p><strong>Privileged Certificates:</strong> Generated by administrators through the install page for specific users.</p>

            <div class="certificate-stats" id="certificateStats">
                <p>Loading certificate statistics...</p>
            </div>
        </div>

        <div class="certificate-instructions">
            <h3>How to Generate Certificates</h3>
            <ol>
                <li>Go to the <a href="admin-install.html" target="_blank">Certificate Installation page</a></li>
                <li>Access certificates are automatically available for everyone</li>
                <li>For privileged certificates (paid user, admin, regular user):
                    <ul>
                        <li>Enter the User ID</li>
                        <li>Select the User Type (Student/Teacher)</li>
                        <li>Choose the Certificate Type</li>
                        <li>Generate and install the certificate</li>
                    </ul>
                </li>
            </ol>
        </div>
    `;

    loadCertificateStats();
}

//async function loadCertificateStats() {
//    try {
//        // Get all certificates from IndexedDB
//        const certificates = await getAllCertificates();
//        const now = new Date();

        // Count different types
//        const accessCerts = certificates.filter(cert => cert.extensions.certificateType === 'access');
//        const paidUserCerts = certificates.filter(cert => cert.extensions.certificateType === 'paid_user');
//        const adminCerts = certificates.filter(cert => cert.extensions.certificateType === 'admin');

        // Count valid certificates
//        const validAccessCerts = accessCerts.filter(cert => new Date(cert.validity.notAfter) > now);
//        const validPaidUserCerts = paidUserCerts.filter(cert => new Date(cert.validity.notAfter) > now);
//        const validAdminCerts = adminCerts.filter(cert => new Date(cert.validity.notAfter) > now);
//
//        const statsDiv = document.getElementById('certificateStats');
//        statsDiv.innerHTML = `
//            <div class="stats-grid">
//                <div class="stat-item">
//                    <h4>Access Certificates</h4>
//                    <p class="stat-number">${validAccessCerts.length} valid / ${accessCerts.length} total</p>
//                </div>
//                <div class="stat-item">
//                    <h4>Paid User Certificates</h4>
//                    <p class="stat-number">${validPaidUserCerts.length} valid / ${paidUserCerts.length} total</p>
//                </div>
//                <div class="stat-item">
//                    <h4>Admin Certificates</h4>
//                    <p class="stat-number">${validAdminCerts.length} valid / ${adminCerts.length} total</p>
//                </div>
//            </div>
//            <p class="stats-note">Certificates expire automatically. Access certificates are valid for 35 days, paid-user certificates are valid for 120 days, and admin certificates remain valid for 1 year.</p>
//        `;
//    } catch (error) {
//        console.error('Error loading certificate stats:', error);
//        document.getElementById('certificateStats').innerHTML = '<p class="error">Error loading certificate statistics</p>';
//    }
//}