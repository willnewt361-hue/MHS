// Payment verification JavaScript
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

async function storeCertificate(certificate) {
    try {
        const db = await openDB();
        const tx = db.transaction([CERT_STORE], 'readwrite');
        const store = tx.objectStore(CERT_STORE);
        store.put(certificate);
        return new Promise((resolve, reject) => {
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    } catch (error) {
        console.error('Could not store certificate in browser:', error);
    }
}

async function verifyPayment(event) {
    event.preventDefault();
    const transactionId = document.getElementById('transactionId').value;

    if (!transactionId.trim()) {
        showNotification('Please enter a transaction ID', 'error');
        return;
    }

    // Show loading state
    document.getElementById('verifyBtnText').classList.add('hidden');
    document.getElementById('verifySpinner').classList.remove('hidden');

    try {
        // Get user data from session storage (set during login)
        const pendingUser = JSON.parse(sessionStorage.getItem('pending_user'));
        const role = sessionStorage.getItem('pending_role') || pendingUser?.user_type;

        if (!pendingUser || !role) {
            showNotification('Session expired. Please login again.', 'error');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        const response = await fetch('/api/pay', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: pendingUser.user_id,
                user_type: role,
                amount: 1000,
                transaction_id: transactionId,
                payment_method: 'airtel'
            })
        });

        const data = await response.json();

        if (data.success) {
            // Payment successful - issue certificate
            const certificate = {
                certificate_id: `PAID_${pendingUser.user_id}_${Date.now()}`,
                type: 'paid_user',
                user_id: pendingUser.user_id,
                user_type: role,
                issued_by: 'Mengo-Hub System',
                issued_date: new Date().toISOString().split('T')[0],
                valid_until: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                permissions: ['full_access', 'paid_features'],
                payment_status: 'verified',
                amount_paid: 1000,
                currency: 'UGX',
                transaction_id: transactionId,
                expiry_days: 120,
                signature: 'MENGO_PAID_SIGNATURE_2026'
            };

            // Store certificate in browser
            localStorage.setItem('mengo_certificate', JSON.stringify(certificate));
            await storeCertificate(certificate);

            // Clear pending data
            sessionStorage.removeItem('pending_user');
            sessionStorage.removeItem('pending_role');

            showNotification('Payment verified! Redirecting to dashboard...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showNotification(data.message || 'Payment verification failed', 'error');
        }
    } catch (error) {
        console.error('Payment verification error:', error);
        showNotification('Connection error. Please try again.', 'error');
    } finally {
        // Reset button
        document.getElementById('verifyBtnText').classList.remove('hidden');
        document.getElementById('verifySpinner').classList.add('hidden');
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
    }, 5000);
}

function goBack() {
    window.location.href = 'login.html';
}

function contactSupport() {
    alert('Contact support at: support@mengo-hub.com or call 0757550965(Newton)');
}

// Check if user should be here
window.addEventListener('load', function() {
    const user = sessionStorage.getItem('pending_user');
    const role = sessionStorage.getItem('pending_role');

    if (!user || !role) {
        // No pending payment - redirect to login
        window.location.href = 'login.html';
    }
});