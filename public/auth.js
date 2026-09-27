// Authentication JS
// IndexedDB setup for certificate storage
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

async function checkPaidCertificate() {
    try {
        const certificates = await getAllCertificates();
        const now = new Date();

        // Look for valid paid certificate (paid_user or admin)
        const paidCert = certificates.find(cert =>
            (cert.extensions.certificateType === 'paid_user' || cert.extensions.certificateType === 'admin') &&
            new Date(cert.validity.notAfter) > now
        );

        return paidCert;
    } catch (error) {
        console.error('Error checking paid certificate:', error);
        return null;
    }
}

function isPotentialAdmin(username) {
    // Check if username looks like it could be an admin
    // This is a simple heuristic - you might want to adjust this logic
    return username && (username.startsWith('admin') || username.length <= 10);
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.querySelector('input[name="role"]:checked')?.value;

    if (!username || !password) {
        showNotification('Please enter username and password', 'error');
        return;
    }

    // Role is required for students and teachers, but optional for admins
    if (!role && !isPotentialAdmin(username)) {
        showNotification('Please select a role (Student or Teacher)', 'error');
        return;
    }

    // Show loading state
    document.getElementById('btnText').classList.add('hidden');
    document.getElementById('spinner').classList.remove('hidden');

    try {
        // Attempt login - server will check payment status and certificates
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();

        if (data.success) {
            // Store user data in session storage
            sessionStorage.setItem('user', JSON.stringify(data.user));
            sessionStorage.setItem('role', role);
            sessionStorage.setItem('is_admin', data.is_admin || false);

            // Create a simple session cookie
            document.cookie = `mengo_session=${btoa(JSON.stringify({
                userId: data.user.id,
                role: role,
                is_admin: data.is_admin || false,
                timestamp: Date.now()
            }))}; path=/; max-age=86400`;

            // Check if admin access
            const isAdmin = data.is_admin;

            showNotification(data.message, 'success', () => {
                if (isAdmin) {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'dashboard.html';
                }
            });
            ClearInputs();
        } else if (data.requires_payment) {
            // User needs to make payment
            ClearInputs();
            sessionStorage.setItem('pending_user', JSON.stringify({
                username: username,
                role: role,
                user_id: data.user_id,
                user_type: data.user_type
            }));
            sessionStorage.setItem('pending_role', role);
            showNotification('Payment required. Redirecting to payment page...', 'warning');
            setTimeout(() => {
                window.location.href = 'payment.html';
            }, 1200);
        } else {
            showNotification(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Connection error. Please try again.', 'error');
    } finally {
        // Reset button
        document.getElementById('btnText').classList.remove('hidden');
        document.getElementById('spinner').classList.add('hidden');
    }
}

function showNotification(message, type = 'info', callback = null) {
    const notif = document.getElementById('notification');
    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.classList.remove('hidden');

    setTimeout(() => {
        notif.classList.add('hidden');
        if (callback) callback();
    }, 3000);
}

function logout() {
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('role');
    document.cookie = 'mengo_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = 'index.html';
}

// Get URL parameter
function getURLParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

// Pre-fill role if coming from home page
window.addEventListener('load', () => {
    const role = getURLParam('role');
    if (role) {
        document.querySelector(`input[value="${role}"]`).checked = true;
    }

    // Force fresh login when the page is revisited via back-navigation
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('is_admin');
    document.cookie = 'mengo_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('role');
        sessionStorage.removeItem('is_admin');
        document.cookie = 'mengo_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }
});

// Clear form inputs
function ClearInputs() {
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}