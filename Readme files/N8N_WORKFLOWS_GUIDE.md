# N8N Workflow Integration Guide for Mengo-Hub
N8N enables powerful educational workflow automation without coding. This guide shows how to set up N8N with Mengo-Hub.

---
## Quick Setup
1. **Install N8N locally or use cloud**
   ```bash
   npm install -g n8n
   n8n
   # Access at http://localhost:5678
   ```

2. **Connect to Mengo-Hub Webhook**
   - Webhook URL: `https://mengo-hub.local/webhooks/n8n/mengo`
   - Authentication: Configure in N8N workflow

---
## Available Webhook Actions
### 1. Send Admin Alert
Trigger immediate admin notifications for critical events.

**Payload:**
```json
{
  "action": "send_admin_alert",
  "data": {
    "title": "Low Performance Alert",
    "message": "Student A001 scored below 50% on Math",
    "severity": "warning",
    "affected_student": "A001"
  }
}
```

**Use Cases:**
- Alert admins of failing students
- Notify on payment failures
- Flag security issues

---
### 2. Create Assignment
Automatically create and assign study materials.
**Payload:**
```json
{
  "action": "create_assignment",
  "data": {
    "teacher_id": "T001",
    "class_id": "C001",
    "subject": "Mathematics",
    "title": "Chapter 5: Quadratic Equations",
    "description": "Practice problems on solving quadratic equations",
    "due_date": "2024-12-20",
    "materials": [
      "https://mengo-hub.local/materials/qe-notes.pdf",
      "https://mengo-hub.local/materials/qe-practice.pdf"
    ]
  }
}
```

**Use Cases:**
- Automated assignment distribution
- Batch create assignments for multiple classes
- Schedule assignments based on curriculum
---

## N8N Workflow Templates
### Workflow 1: Daily Performance Summary
**Trigger**: Cron job (Daily at 8 AM)
```
1. HTTP Request → GET https://mengo-hub.local/api/admin/reports
2. Filter for students with avg < 60%
3. Format HTML email
4. Send Email → all_admins@mengo-hub.com
5. Log to N8N
```

**Configuration:**
```
- Trigger: Cron (0 8 * * *)
- Headers: Authorization: Bearer MengoAdminAPIToken2026
- Email template: HTML with student names, scores, subjects
```

---
### Workflow 2: Auto-Create Remedial Assignments
**Trigger**: When student fails quiz
```
1. Webhook trigger (quiz_failed event)
2. Query weakness_detector API
3. Extract weak topics
4. Create assignment via N8N webhook
5. Notify student via email
6. Update student progress
```

**Configuration:**
```json
{
  "trigger": "webhook",
  "webhook_url": "/webhooks/n8n/mengo",
  "action": "create_assignment",
  "data": {
    "teacher_id": "SYSTEM_AUTO",
    "class_id": "{{student.class_id}}",
    "subject": "{{weak_topic}}",
    "title": "Remedial: {{weak_topic}}",
    "due_date": "{{today + 7 days}}"
  }
}
```

---
### Workflow 3: Send Motivational Messages
**Trigger**: Cron job (Weekly)
```
1. Query gamification API for this week's top performers
2. For each top 10 student:
   - Generate personalized message
   - Send via email/SMS
   - Award bonus points
3. Log achievements
```

**Configuration:**
```
- Trigger: Cron (0 9 * * MON)
- Request: GET /api/gamification/leaderboard?limit=10
- Message template: "Great job this week! You've earned X points."
- Award +10 bonus points per student
```

---
### Workflow 4: Attendance Auto-Check & Alert
**Trigger**: API endpoint called by mobile app
```
1. Webhook receives attendance check-in
2. Log attendance in Mengo-Hub
3. If absence detected:
   - Send alert to guardian
   - Notify teacher
   - Update student record
4. Generate daily report
```

**Configuration:**
```json
{
  "action": "send_admin_alert",
  "data": {
    "title": "Attendance: Student Absent",
    "message": "{{student_name}} was absent from {{subject}}",
    "severity": "info",
    "affected_student": "{{student_id}}"
  }
}
```

---
### Workflow 5: Certificate & Credential Generation
**Trigger**: Course completion webhook
```
1. Webhook: course_completed event
2. Generate certificate PDF using ReportLab
3. Upload to student dashboard
4. Send congratulation email
5. Update transcript
6. Award badge/points
```

**Configuration:**
```
- Trigger: Webhook from course completion
- Generate: PDF certificate with student name, course, date, score
- Email template: "Congratulations on completing [Course]!"
- Award: 100 points + certificate badge
```

---
### Workflow 6: Real-time Quiz Feedback via AI
**Trigger**: Quiz submission
```
1. Webhook: quiz_submitted event
2. Call AI service → /api/ai/explain
3. Generate personalized feedback
4. Send to student immediately
5. Flag misconceptions for teacher
```

**Configuration:**
```
- Trigger: Webhook on quiz submission
- AI Prompt: "Explain why this answer is incorrect for a high school student"
- Send feedback: Email + dashboard notification
- Teacher alert: If >30% got answer wrong
```

---
### Workflow 7: Study Plan Auto-Generator
**Trigger**: Weekly analysis (Sunday night)
```
1. Query all students' performance
2. For each student:
   - Get weakness analysis
   - Call AI study plan generator
   - Store in database
3. Notify students: "Your personalized study plan is ready"
```

**Configuration:**
```
- Trigger: Cron (0 20 * * SUN)
- For each student:
  - GET /api/premium/weakness-detector/:student_id
  - POST /api/premium/study-plans/generate
  - Email: "Your study plan for next week is ready"
```

---
## N8N Workflow Best Practices
1. **Error Handling**
   - Always add error handlers
   - Retry failed webhooks with exponential backoff
   - Log errors to monitoring system

2. **Performance**
   - Use batch operations for multiple students
   - Schedule heavy operations during off-peak hours
   - Implement rate limiting on webhook calls

3. **Security**
   - Store API tokens in N8N secrets, not in workflow
   - Validate webhook source (IP whitelist if possible)
   - Log all webhook calls for audit trail

4. **Testing**
   - Test workflows with sample data first
   - Use N8N's debug mode to inspect data flow
   - Monitor webhook logs in Mengo-Hub

---
## Webhook Response Format
All webhooks respond with:
```json
{
  "success": true,
  "message": "Action processed successfully",
  "action": "send_admin_alert",
  "notified_count": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Or on error:

```json
{
  "success": false,
  "message": "Action failed: Invalid student_id",
  "action": "create_assignment",
  "error": "Student A999 not found",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---
## Example: Full N8N Workflow JSON
```json
{
  "name": "Mengo-Hub: Daily Performance Report",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "intervalValue": 1,
              "intervalUnit": "days"
            }
          ]
        }
      },
      "name": "Trigger - Daily at 8 AM",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "https://mengo-hub.local/api/admin/reports",
        "authentication": "genericCredentialType",
        "genericCredentialType": {
          "credentialsType": "httpHeaderAuth",
          "genericCredentials": {
            "name": "Authorization",
            "value": "Bearer MengoAdminAPIToken2026"
          }
        },
        "options": {}
      },
      "name": "Fetch Admin Reports",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    },
    {
      "parameters": {
        "operation": "filter",
        "simple": true,
        "conditions": {
          "string": [
            {
              "value1": "{{ $json.report.average_performance }}",
              "operation": "<",
              "value2": "60"
            }
          ]
        }
      },
      "name": "Filter Low Performers",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 1,
      "position": [650, 300]
    }
  ],
  "connections": {
    "Trigger - Daily at 8 AM": {
      "main": [
        [
          {
            "node": "Fetch Admin Reports",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch Admin Reports": {
      "main": [
        [
          {
            "node": "Filter Low Performers",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---
## Mengo-Hub N8N Integration Checklist
- [ ] N8N installed and running
- [ ] Mengo-Hub webhook endpoint tested
- [ ] Admin token generated and stored in N8N secrets
- [ ] First workflow created (Performance Report)
- [ ] Webhook logs monitored
- [ ] Error handling configured
- [ ] Email notifications tested
- [ ] Batch operations optimized
- [ ] Security measures implemented
- [ ] Workflows scheduled and active

---
## Support & Troubleshooting
**Webhook not triggering?**
- Check N8N is running: `http://localhost:5678`
- Verify webhook URL in N8N matches Mengo-Hub
- Check firewall/network connectivity

**Actions not executing?**
- Review N8N logs: `journalctl -u n8n -f`
- Test webhook payload manually with curl
- Enable debug mode in workflow

**Need help?**
- N8N docs: https://docs.n8n.io/
- Mengo-Hub webhook format: See COMPLETE_IMPLEMENTATION_GUIDE.md
- Check `/logs/mengo_hub.log` for webhook activity

