# Admin Dashboard Controls & Enhancement Guide
## New Admin Endpoints
### Feature Toggles Management
**GET/POST** `/api/admin/feature-toggles`

Toggle premium features on/off:
```bash
curl -X POST https://localhost:5000/api/admin/feature-toggles \
  -H "Authorization: Bearer MengoAdminAPIToken2026" \
  -H "Content-Type: application/json" \
  -d '{
    "smart_revision": true,
    "weakness_detector": true,
    "exam_predictor": true,
    "gamification": true,
    "ai_chat": true,
    "audio_beats": true,
    "3d_visualization": true
  }'
```

### Certificate Management
**GET** `/api/admin/validate-certificate?user_id=A001`
Verify admin access without blocking on null certificate.

### Email Configuration
**GET/POST** `/api/admin/email-config`
Configure email provider settings in admin UI.

**POST** `/api/admin/email-config/test`
Send test email to verify setup.

**POST** `/api/admin/send-admin-alert`
Send alerts to all admin users.
---

---
## Dashboard Stats Widget
Add to admin overview to show:
- Active students
- Quiz completion rate
- Average performance
- System health

```javascript
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
```

---
## Admin Actions Reference
|        Action       |               Endpoint            | Method | Admin Token |
|---------------------|-----------------------------------|--------|-------------|
| Get Feature Toggles | `/api/admin/feature-toggles`      |   GET  |     Yes     |
| Update Features     | `/api/admin/feature-toggles`      |  POST  |     Yes     |
| Email Config        | `/api/admin/email-config`         |GET/POST|     Yes     | 
| Test Email          | `/api/admin/email-config/test`    |  POST  |     Yes     |
| Admin Alert         | `/api/admin/send-admin-alert`     |  POST  |     Yes     |
| Validate Certificate| `/api/admin/validate-certificate` |   GET  |     Yes     |
| Manage Users        | `/api/admin/users`                |   GET  |     Yes     |
| Admin Reports       | `/api/admin/reports`              |   GET  |     Yes     |
---

## Dashboard Layout Recommendations
Organize admin panel into tabs:
1. **Overview** - Stats, recent activity
2. **Users** - Manage student/teacher/admin accounts
3. **Features** - Toggle premium features
4. **Email** - Configure email provider
5. **AI** - Set AI provider and settings
6. **Certificates** - Manage user certificates
7. **Logs** - View system logs
8. **N8N** - Webhook configuration
9. **System** - Health, settings, backups
---
## Integration with Existing Admin
- The new endpoints integrate seamlessly
- No breaking changes to existing functionality
- All controls use existing admin token authentication
- Feature toggles stored in `system_settings` table
- Email configuration stored in `email_configuration` table

