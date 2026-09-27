const DB_NAME = 'MengoHubCertificates';
const DB_VERSION = 1;
const CERT_STORE = 'certificates';

let generatedCertificate = null;

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
    const tx = db.transaction([CERT_STORE], 'readwrite');
    const store = tx.objectStore(CERT_STORE);
    return new Promise((resolve, reject) => {
        const request = store.put(cert);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function getAllCertificates() {
    const db = await openDB();
    const tx = db.transaction([CERT_STORE], 'readonly');
    const store = tx.objectStore(CERT_STORE);
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getCertificate(serialNumber) {
    const db = await openDB();
    const tx = db.transaction([CERT_STORE], 'readonly');
    const store = tx.objectStore(CERT_STORE);
    return new Promise((resolve, reject) => {
        const request = store.get(serialNumber);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

async function displayCertificateStatus() {
    const certificates = await getAllCertificates();
    const now = new Date();
    const statusDiv = document.getElementById('accessStatus');
    const installBtn = document.getElementById('installAccessBtn');
    const accessCert = certificates.find(cert => cert.extensions?.certificateType === 'access');

    if (accessCert && new Date(accessCert.validity.notAfter) > now) {
        statusDiv.innerHTML = `
            <p style="color: green;">✅ Access certificate installed and valid.</p>
            <p>Expires: ${new Date(accessCert.validity.notAfter).toLocaleDateString()}</p>
        `;
        installBtn.style.display = 'none';
    } else {
        statusDiv.innerHTML = `
            <p style="color: orange;">⚠️ No valid access certificate found.</p>
            <p>Install one now to use the site.</p>
        `;
        installBtn.style.display = 'block';
    }
}

async function loadCertificates() {
    const certificates = await getAllCertificates();
    const now = new Date();
    const summary = certificates.reduce((result, cert) => {
        const type = cert.extensions?.certificateType || 'unknown';
        result[type] = (result[type] || 0) + 1;
        if (new Date(cert.validity.notAfter) > now) result.valid = (result.valid || 0) + 1;
        return result;
    }, {});

    document.getElementById('certificateSummary').innerHTML = `
        <div class="certificate-summary-row"><strong>Total installed:</strong> ${certificates.length}</div>
        <div class="certificate-summary-row"><strong>Valid certificates:</strong> ${summary.valid || 0}</div>
        <div class="certificate-summary-row"><strong>Access certificates:</strong> ${summary.access || 0}</div>
        <div class="certificate-summary-row"><strong>Paid certificates:</strong> ${summary.paid_user || 0}</div>
        <div class="certificate-summary-row"><strong>Admin certificates:</strong> ${summary.admin || 0}</div>
    `;

    document.getElementById('certificateList').innerHTML = certificates.length > 0 ? certificates.map(cert => {
        const expires = new Date(cert.validity.notAfter);
        const isValid = expires > now;
        return `
            <div class="certificate-row ${isValid ? 'valid' : 'expired'}">
                <div><strong>${cert.serialNumber}</strong></div>
                <div>${cert.extensions?.certificateType || 'unknown'}</div>
                <div>${isValid ? 'Valid until ' + expires.toLocaleDateString() : 'Expired'}</div>
            </div>
        `;
    }).join('') : '<p>No certificates installed yet.</p>';
}

async function generateAccessCertificate(event) {
    event.preventDefault();

    const userId = document.getElementById('userId').value.trim();
    const userType = document.getElementById('userType').value;

    if (!userId) {
        showNotification('Please enter a User ID', 'error');
        return;
    }

    const now = new Date();
    const expiryDate = new Date(now.getTime() + (365 * 24 * 60 * 60 * 1000)); // 1 year for access

    generatedCertificate = {
        "version": 3,
        "serialNumber": `ACCESS_${userId}_${Date.now()}`,
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
            "certificateType": "access",
            "permissions": ["website_access", "login"],
            "accessLevel": "basic",
            "userId": userId,
            "userType": userType,
            "description": `Access certificate for ${userType} ${userId}`,
            "issuedBy": "Mengo-Hub System",
            "issuedDate": now.toISOString().split('T')[0],
            "expiryDays": 365
        },
        "signatureValue": `MENGO_ACCESS_SIGNATURE_${Date.now()}`
    };

    // Display generated certificate
    document.getElementById('certificateJson').value = JSON.stringify(generatedCertificate, null, 2);
    document.getElementById('certificateDisplay').style.display = 'block';
}

async function installPastedCertificate() {
    const raw = document.getElementById('certificateText').value.trim();
    if (!raw) {
        showNotification('Paste certificate JSON first', 'error');
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
        document.getElementById('certificateText').value = '';
        await displayCertificateStatus();
        await loadCertificates();
    } catch (error) {
        console.error(error);
        showNotification('Invalid JSON format', 'error');
    }
}

async function installCertificateFromQuery() {
    const certParam = getQueryParam('cert');
    if (!certParam) return;

    try {
        const cert = JSON.parse(decodeURIComponent(certParam));
        if (cert && cert.serialNumber) {
            await storeCertificate(cert);
            showNotification('Certificate imported from URL and installed', 'success');
            window.history.replaceState({}, document.title, 'install.html');
            await displayCertificateStatus();
            await loadCertificates();
        }
    } catch (error) {
        console.error(error);
        showNotification('Failed to import certificate from URL', 'error');
    }
}

function copyCertificate() {
    const text = document.getElementById('certificateJson').value;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Certificate copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy certificate', 'error');
    });
}

async function installGeneratedCertificate() {
    if (!generatedCertificate) {
        showNotification('No certificate generated', 'error');
        return;
    }

    try {
        await storeCertificate(generatedCertificate);
        showNotification('Certificate installed successfully!', 'success');
        document.getElementById('certificateDisplay').style.display = 'none';
        // Optionally redirect to login
        setTimeout(() => {
            window.location.href = 'admin-install.html';
        }, 2000);
    } catch (error) {
        console.error('Certificate installation error:', error);
        showNotification('Failed to install certificate', 'error');
    }
}

function showNotification(message, type = 'info') {
    let notif = document.getElementById('notification');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'notification';
        document.body.appendChild(notif);
    }

    notif.textContent = message;
    notif.className = `notification ${type}`;
    notif.classList.remove('hidden');

    setTimeout(() => {
        notif.classList.add('hidden');
    }, 3000);
}

window.addEventListener('load', async () => {
    await displayCertificateStatus();
    await loadCertificates();
    await installCertificateFromQuery();
});
