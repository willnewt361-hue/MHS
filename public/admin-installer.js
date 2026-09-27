// Certificate Installer JavaScript
let certificateData = null;
let generatedCertificate = null;

// IndexedDB setup for certificate storage
const DB_NAME = 'MengoHubCertificates';
const DB_VERSION = 1;
const CERT_STORE = 'certificates';

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

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

async function storeCertificate(cert) {
    const db = await openDB();
    const transaction = db.transaction([CERT_STORE], 'readwrite');
    const store = transaction.objectStore(CERT_STORE);
    await new Promise((resolve, reject) => {
        const request = store.put(cert);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function getCertificate(serialNumber) {
    const db = await openDB();
    const transaction = db.transaction([CERT_STORE], 'readonly');
    const store = transaction.objectStore(CERT_STORE);
    return new Promise((resolve, reject) => {
        const request = store.get(serialNumber);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
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

// Check if user has valid access certificate
async function checkAccessCertificate() {
    try {
        const certificates = await getAllCertificates();
        const now = new Date();

        // Look for valid access certificate
        const accessCert = certificates.find(cert =>
            cert.extensions.certificateType === 'access' &&
            new Date(cert.validity.notAfter) > now
        );

        const statusDiv = document.getElementById('accessStatus');
        const installBtn = document.getElementById('installAccessBtn');

        if (accessCert) {
            statusDiv.innerHTML = `
                <p style="color: green;">✅ Access certificate installed and valid</p>
                <p>Expires: ${new Date(accessCert.validity.notAfter).toLocaleDateString()}</p>
            `;
            installBtn.style.display = 'none';
        } else {
            statusDiv.innerHTML = `
                <p style="color: orange;">⚠️ No valid access certificate found</p>
                <p>Install one below to access the website</p>
            `;
            installBtn.style.display = 'block';
        }
    } catch (error) {
        console.error('Error checking access certificate:', error);
        document.getElementById('accessStatus').innerHTML = `
            <p style="color: red;">❌ Error checking certificate status</p>
        `;
    }
}

async function checkAllCertificates() {
    try {
        const certificates = await getAllCertificates();
        const now = new Date();
        const summary = {
            access: 0,
            admin: 0,
            paid_user: 0,
            valid: 0
        };

        const rows = certificates.map(cert => {
            const expires = new Date(cert.validity.notAfter);
            const isValid = expires > now;
            if (isValid) summary.valid++;

            const type = cert.extensions?.certificateType || 'unknown';
            if (summary[type] !== undefined) summary[type]++;

            return `
                <div class="certificate-row ${isValid ? 'valid' : 'expired'}">
                    <div><strong>${cert.serialNumber}</strong> (${type.replace('_', ' ')})</div>
                    <div>${cert.subject?.commonName || ''}</div>
                    <div>${isValid ? 'Valid until ' + expires.toLocaleDateString() : 'Expired'}</div>
                </div>
            `;
        });

        document.getElementById('certificateSummary').innerHTML = `
            <div class="certificate-summary-row"><strong>Total certificates:</strong> ${certificates.length}</div>
            <div class="certificate-summary-row"><strong>Valid certificates:</strong> ${summary.valid}</div>
            <div class="certificate-summary-row"><strong>Access:</strong> ${summary.access}</div>
            <div class="certificate-summary-row"><strong>Admin:</strong> ${summary.admin}</div>
            <div class="certificate-summary-row"><strong>Paid user:</strong> ${summary.paid_user}</div>
        `;

        document.getElementById('certificateList').innerHTML = rows.length > 0 ? rows.join('') : '<p>No certificates installed yet.</p>';
    } catch (error) {
        console.error('Error checking all certificates:', error);
        document.getElementById('certificateSummary').innerHTML = '<p style="color:red;">Unable to read certificates.</p>';
    }
}

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

async function installCertificateFromQuery() {
    const certParam = getQueryParam('cert');
    if (!certParam) return;

    try {
        const parsed = JSON.parse(decodeURIComponent(certParam));
        if (parsed && parsed.serialNumber) {
            await storeCertificate(parsed);
            showNotification('Certificate imported from URL and saved locally.', 'success');
            window.history.replaceState({}, document.title, 'admin-install.html');
            await checkAllCertificates();
            await checkAccessCertificate();
        }
    } catch (error) {
        console.error('Failed to import certificate from URL:', error);
        showNotification('Invalid certificate URL parameter', 'error');
    }
}

async function installPastedCertificate() {
    const raw = document.getElementById('pasteCertificateJson').value.trim();
    if (!raw) {
        showNotification('Please paste the certificate JSON', 'error');
        return;
    }

    try {
        const cert = JSON.parse(raw);
        if (!cert || !cert.serialNumber) {
            showNotification('Invalid certificate JSON', 'error');
            return;
        }

        await storeCertificate(cert);
        showNotification('Certificate installed successfully', 'success');
        document.getElementById('pasteCertificateJson').value = '';
        await checkAllCertificates();
    } catch (error) {
        console.error('Paste install error:', error);
        showNotification('Failed to install pasted certificate', 'error');
    }
}

// Auto-install access certificate for everyone
async function installAccessCertificate() {
    const now = new Date();
    const expiryDate = new Date(now.getTime() + (35 * 24 * 60 * 60 * 1000));

    const accessCertificate = {
        "version": 3,
        "serialNumber": `ACCESS_CERT_${Date.now()}`,
        "signature": { "algorithm": "sha256WithRSAEncryption" },
        "issuer": { "countryName": "UG", "organizationName": "Mengo-Hub Certificate Authority", "commonName": "Mengo-Hub CA" },
        "validity": { "notBefore": now.toISOString(), "notAfter": expiryDate.toISOString() },
        "subject": { "countryName": "UG", "organizationName": "Mengo-Hub System", "organizationalUnitName": "Website Access", "commonName": "access.mengo-hub.local" },
        "subjectPublicKeyInfo": { "algorithm": "rsaEncryption", "publicKey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..." },
        "extensions": {
            "keyUsage": ["digitalSignature"],
            "extendedKeyUsage": ["clientAuth"],
            "certificateType": "access",
            "permissions": ["website_access"],
            "accessLevel": "basic",
            "description": "Basic website access certificate - allows visiting the site",
            "issuedBy": "Mengo-Hub System",
            "issuedDate": now.toISOString().split('T')[0],
            "expiryDays": 35
        },
        "signatureValue": `MENGO_ACCESS_SIGNATURE_${Date.now()}`
    };

    try {
        // Check if access certificate already exists
        const certificates = await getAllCertificates();
        const existingAccess = certificates.find(cert => cert.extensions.certificateType === 'access');

        if (existingAccess) {
            showNotification('Access certificate already installed', 'warning');
            return;
        }

        // Store certificate in IndexedDB
        await storeCertificate(accessCertificate);

        showNotification('Access certificate installed successfully! You can now visit the website.', 'success', () => {
            window.location.href = 'index.html';
        });

    } catch (error) {
        console.error('Certificate installation error:', error);
        showNotification('Failed to install access certificate', 'error');
    }
}

// Generate specific certificate based on form input
function generateCertificate(event) {
    event.preventDefault();

    const userId = document.getElementById('userId').value.trim();
    const userType = document.getElementById('userType').value;
    const certType = document.getElementById('certType').value;

    if (!userId) {
        showNotification('Please enter a User ID', 'error');
        return;
    }

    const now = new Date();
    let expiryDate;
    let permissions = [];
    let accessLevel = 'basic';

    // Set expiry and permissions based on certificate type
    switch (certType) {
        case 'paid_user':
            expiryDate = new Date(now.getTime() + (120 * 24 * 60 * 60 * 1000)); // 120 days
            permissions = ['website_access', 'login', 'dashboard', 'payments'];
            accessLevel = 'paid';
            break;
        case 'admin':
            expiryDate = new Date(now.getTime() + (365 * 24 * 60 * 60 * 1000)); // 1 year
            permissions = ['full_access', 'user_management', 'payment_management', 'system_monitoring', 'certificate_generation'];
            accessLevel = 'admin';
            break;
    }

    // Create certificate
    generatedCertificate = {
        "version": 3,
        "serialNumber": `${certType.toUpperCase()}_${userId}_${Date.now()}`,
        "signature": { "algorithm": "sha256WithRSAEncryption" },
        "issuer": { "countryName": "UG", "organizationName": "Mengo-Hub Certificate Authority", "commonName": "Mengo-Hub CA" },
        "validity": { "notBefore": now.toISOString(), "notAfter": expiryDate.toISOString() },
        "subject": {
            "countryName": "UG",
            "organizationName": "Mengo-Hub System",
            "organizationalUnitName": userType === 'student' ? 'Students' : 'Teachers',
            "commonName": `${userId}.mengo-hub.local`
        },
        "subjectPublicKeyInfo": { "algorithm": "rsaEncryption", "publicKey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..." },
        "extensions": {
            "keyUsage": ["digitalSignature", "keyEncipherment"],
            "extendedKeyUsage": ["serverAuth", "clientAuth"],
            "subjectAltName": [`DNS:${userId}.mengo-hub.local`],
            "certificateType": certType,
            "permissions": permissions,
            "accessLevel": accessLevel,
            "userId": userId,
            "userType": userType,
            "description": `${certType.replace('_', ' ').toUpperCase()} certificate for ${userType} ${userId}`,
            "issuedBy": "Mengo-Hub System",
            "issuedDate": now.toISOString().split('T')[0],
            "expiryDays": certType === 'paid_user' ? 120 : 365
        },
        "signatureValue": `MENGO_${certType.toUpperCase()}_SIGNATURE_${Date.now()}`
    };

    // Display generated certificate
    document.getElementById('certificateJson').value = JSON.stringify(generatedCertificate, null, 2);
    document.getElementById('certificateDisplay').style.display = 'block';

    showNotification(`Certificate generated for ${userId}`, 'success');
}

// Copy certificate to clipboard
async function copyCertificate() {
    if (!generatedCertificate) {
        showNotification('No certificate to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(JSON.stringify(generatedCertificate, null, 2));
        showNotification('Certificate copied to clipboard', 'success');
    } catch (error) {
        console.error('Failed to copy certificate:', error);
        showNotification('Failed to copy certificate', 'error');
    }
}

// Install the generated certificate
async function installGeneratedCertificate() {
    if (!generatedCertificate) {
        showNotification('No certificate to install', 'error');
        return;
    }

    try {
        // Check if certificate already exists
        const existingCert = await getCertificate(generatedCertificate.serialNumber);
        if (existingCert) {
            showNotification('Certificate already installed', 'warning');
            return;
        }

        // Store certificate in IndexedDB
        await storeCertificate(generatedCertificate);

        showNotification('Certificate installed successfully!', 'success', () => {
            // Redirect based on certificate type
            if (generatedCertificate.extensions.certificateType === 'admin') {
                window.location.href = 'admin.html';
            } else if (generatedCertificate.extensions.certificateType === 'paid_user') {
                window.location.href = 'dashboard.html';
            } else {
                window.location.href = 'login.html';
            }
        });

    } catch (error) {
        console.error('Certificate installation error:', error);
        showNotification('Failed to install certificate', 'error');
    }
}

function showNotification(message, type = 'info', callback = null) {
    // Create notification element if it doesn't exist
    let notif = document.getElementById('notification');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'notification';
        notif.className = 'notification';
        document.body.appendChild(notif);
    }

    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.classList.remove('hidden');

    setTimeout(() => {
        notif.classList.add('hidden');
        if (callback) callback();
    }, 5000);
}

function goBack() {
    window.location.href = 'index.html';
}

function goToTest() {
    window.location.href = 'test.html';
}

// Initialize page
window.addEventListener('load', function() {
    checkAccessCertificate();
    checkAllCertificates();
    installCertificateFromQuery();
});