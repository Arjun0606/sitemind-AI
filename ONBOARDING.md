# SiteMind Customer Onboarding Guide

## Overview

This guide covers how to set up SiteMind for a new customer. The system is designed to be:
- **Modular**: Config-driven, not code changes
- **Scalable**: Same process whether 1 site or 100 sites
- **Flexible**: Accommodate different customer needs

---

## The 30-Minute Setup

For your first customers, you'll do "white-glove" setup. Here's the exact flow:

### Pre-Call Checklist

Before the onboarding call, get from customer:
```
□ Company name
□ Primary contact (name, email, phone)
□ Number of sites to onboard
□ For each site:
  □ Site name
  □ Site address
  □ Site engineers (name + phone)
  □ Project Manager (name + phone)
□ Existing drawings (Drive link / will share on WhatsApp)
□ Billing contact email
```

### The Onboarding Call (30 min)

```
0-5 min:  Quick intro, confirm details
5-15 min: You set up their account (they watch)
15-25 min: Demo - they send first query
25-30 min: Explain what happens next, Q&A
```

---

## Step-by-Step Setup Process

### Step 1: Create Organization (2 min)

```bash
# Via Admin Dashboard or API call

POST /api/admin/organizations
{
  "name": "ABC Builders Pvt Ltd",
  "slug": "abc-builders",
  "plan": "pilot",  # or "standard"
  "billing_email": "accounts@abcbuilders.com",
  "settings": {
    "language": "hinglish",
    "morning_brief_time": "07:00",
    "timezone": "Asia/Kolkata"
  }
}
```

### Step 2: Create Admin User (1 min)

```bash
POST /api/admin/users
{
  "organization_id": "org_xxx",
  "name": "Mr. Rajesh Sharma",
  "email": "rajesh@abcbuilders.com",
  "phone": "+919876543210",
  "role": "owner"
}
```

They'll receive WhatsApp: "Welcome to SiteMind! You're set up as admin for ABC Builders."

### Step 3: Create Project/Site (2 min per site)

```bash
POST /api/admin/projects
{
  "organization_id": "org_xxx",
  "name": "Skyline Towers",
  "code": "SKY-001",
  "address": "Plot 45, Sector 62, Noida",
  "city": "Noida",
  "project_type": "residential",
  "settings": {
    "disciplines": ["structural", "architectural", "mep"],
    "notification_settings": {
      "morning_brief": true,
      "red_flags": true,
      "daily_summary": false
    }
  }
}
```

### Step 4: Add Team Members (1 min per person)

```bash
POST /api/admin/project-members
{
  "project_id": "proj_xxx",
  "members": [
    {
      "name": "Ramesh Kumar",
      "phone": "+919876543211",
      "role": "site_engineer",
      "permissions": ["query", "upload_photos", "report_progress"]
    },
    {
      "name": "Priya Singh",
      "phone": "+919876543212",
      "role": "pm",
      "permissions": ["all"]
    }
  ]
}
```

Each member receives WhatsApp: "You've been added to Skyline Towers on SiteMind. Send any question about the project!"

### Step 5: Upload Initial Drawings (5-10 min)

**Option A: Customer shares Drive link**
```bash
POST /api/admin/integrations/google-drive
{
  "project_id": "proj_xxx",
  "folder_url": "https://drive.google.com/...",
  "auto_sync": true
}
```

**Option B: Customer shares on WhatsApp during call**
- They forward drawings to SiteMind number
- System processes automatically
- You verify: "Got 12 drawings, all processed"

**Option C: You upload via dashboard**
- Drag & drop in admin panel
- Bulk upload supported

### Step 6: Initial Memory Seeding (Optional, 5 min)

If customer has key decisions already made:
```bash
POST /api/admin/memories/bulk
{
  "project_id": "proj_xxx",
  "memories": [
    {
      "content": "All beams on Floor 1-5 are 300x600mm unless noted",
      "type": "decision",
      "source": "initial_setup"
    },
    {
      "content": "Rebar supplier: Tata Steel. Contact: 9876543213",
      "type": "instruction",
      "source": "initial_setup"
    }
  ]
}
```

### Step 7: First Query Demo (2 min)

Ask customer to send first message:
```
Customer: "Beam size B3 floor 2?"
SiteMind: "Based on drawing SK-003, B3 at Floor 2 is 300x600mm.
          Main bars: 4-20mm top, 4-20mm bottom
          Stirrups: 8mm @ 150 c/c"
```

🎉 **They're live!**

---

## Configuration Options (Modular)

### Organization-Level Config

```json
{
  "organization_settings": {
    // Language preferences
    "primary_language": "hinglish",  // en, hi, hinglish
    "ai_response_style": "professional",  // professional, friendly, brief
    
    // Notifications
    "morning_brief_enabled": true,
    "morning_brief_time": "07:00",
    "timezone": "Asia/Kolkata",
    
    // Features (can enable/disable per customer)
    "features": {
      "red_flags": true,
      "task_management": true,
      "material_tracking": true,
      "progress_photos": true,
      "office_site_sync": true,
      "integrations": true
    },
    
    // Branding (for enterprise)
    "branding": {
      "assistant_name": "SiteMind",  // or custom name
      "logo_url": null
    },
    
    // Limits
    "max_sites": 10,
    "max_users_per_site": 50,
    "storage_gb": 100
  }
}
```

### Project-Level Config

```json
{
  "project_settings": {
    // Project specifics
    "disciplines": ["structural", "architectural", "mep", "electrical", "plumbing"],
    "grid_system": "alphanumeric",  // A1, B2, etc.
    "floor_naming": "numeric",  // Floor 1, Floor 2 OR Ground, First, Second
    
    // Notifications for this project
    "notifications": {
      "morning_brief_recipients": ["pm", "owner"],
      "red_flag_recipients": ["pm", "owner", "consultant"],
      "daily_summary_recipients": ["pm"]
    },
    
    // Feature toggles
    "enable_material_tracking": true,
    "enable_task_management": true,
    "enable_progress_photos": true,
    
    // AI behavior
    "ai_config": {
      "include_drawing_references": true,
      "include_revision_warnings": true,
      "safety_emphasis": "high"
    }
  }
}
```

### User-Level Config

```json
{
  "user_settings": {
    // Personal preferences
    "language": "hi",  // Override org default
    "notification_preferences": {
      "morning_brief": true,
      "task_assignments": true,
      "red_flags": false  // Site engineer doesn't need all red flags
    },
    
    // Permissions (what they can do)
    "permissions": {
      "can_query": true,
      "can_upload_documents": false,
      "can_upload_photos": true,
      "can_create_tasks": false,
      "can_view_reports": false,
      "can_record_materials": true
    }
  }
}
```

---

## Handling Different Customer Types

### Type 1: Small Builder (1-3 sites)

```
Setup time: 15 minutes
Config:
- Simple setup, all features enabled
- Owner + PM + 2-3 site engineers
- Shared drawings via WhatsApp
- No integrations needed

Price: $500/site standard
```

### Type 2: Medium Builder (5-15 sites)

```
Setup time: 30-45 minutes
Config:
- Multiple projects under one org
- Clear role hierarchy
- Google Drive integration for drawings
- Weekly reports to management

Price: $500/site with volume discount
```

### Type 3: Large Developer (20+ sites)

```
Setup time: 1-2 hours initial + ongoing
Config:
- Enterprise settings
- Multiple PMs, consultants
- ERP integration (SAP/Tally)
- Custom reporting
- Dedicated support channel

Price: Custom enterprise deal
```

### Type 4: Consultant/Architect (works with multiple builders)

```
Setup time: 15 minutes
Config:
- Access to specific projects only
- Can receive queries about their drawings
- Gets notified when their drawings are updated

Price: Free (comes with builder's subscription)
```

---

## Post-Setup: First Week Success

### Day 1: Setup complete
- All team members receive welcome message
- First query answered successfully
- Customer knows basic usage

### Day 2-3: Monitor & Support
```
You check dashboard daily:
- Are they sending queries? (Target: 5+ per site per day)
- Any errors? Any unanswered queries?
- Proactively message: "How's SiteMind working? Any questions?"
```

### Day 4-7: Optimize
```
Based on their usage:
- Add missing drawings they ask about
- Seed memories for common questions
- Adjust notification settings if too many/few
```

### Week 2+: Autopilot
```
System runs itself:
- Morning briefs go out automatically
- Red flags detected and alerted
- Weekly reports generated
- You check dashboard weekly
```

---

## Handling Special Requests

### "Can you change the AI's name?"

```json
// Update organization settings
{
  "branding": {
    "assistant_name": "BuildBot"  // Instead of SiteMind
  }
}
```
No code change needed.

### "We want reports in Hindi"

```json
// Update organization settings
{
  "report_language": "hi"
}
```
Reports generated in Hindi.

### "Our site engineers should only ask questions, not upload"

```json
// Update user permissions
{
  "permissions": {
    "can_query": true,
    "can_upload_documents": false,
    "can_upload_photos": false
  }
}
```

### "We use Primavera for scheduling"

```bash
POST /api/admin/integrations/primavera
{
  "organization_id": "org_xxx",
  "api_endpoint": "https://primavera.company.com/api",
  "credentials": { ... },
  "sync_settings": {
    "milestones": true,
    "progress_push": true
  }
}
```

### "Can we get custom reports?"

```json
// Create custom report template
{
  "report_template": {
    "name": "Weekly Management Report",
    "sections": ["progress_summary", "red_flags", "material_status", "cost_overview"],
    "recipients": ["owner", "cfo"],
    "schedule": "every_monday_9am"
  }
}
```

---

## Troubleshooting Common Issues

### "Messages not being received"

1. Check user's phone number format (+91...)
2. Verify Twilio WhatsApp connection
3. Check if user blocked SiteMind number
4. Test with your own phone first

### "AI giving wrong answers"

1. Check if drawings are uploaded correctly
2. Verify drawing was analyzed (check ai_analyzed flag)
3. Check if there are conflicting memories
4. Manually seed correct information

### "Customer wants to add more sites"

```bash
# Just create new project, same organization
POST /api/admin/projects
{
  "organization_id": "org_xxx",  # Same org
  "name": "New Site Name",
  ...
}

# Update billing if needed
PUT /api/admin/organizations/org_xxx/billing
{
  "sites_count": 5  # Updated count for billing
}
```

### "Customer wants to cancel"

```bash
# Soft delete - data preserved for 90 days
PUT /api/admin/organizations/org_xxx
{
  "subscription_status": "cancelled",
  "cancellation_reason": "...",
  "data_retention_until": "2025-03-07"
}
```

---

## Onboarding Checklist Template

```markdown
## Customer: [Name]
## Date: [Date]
## Sites: [Count]

### Pre-Call
- [ ] Received company details
- [ ] Received site list
- [ ] Received team contacts
- [ ] Scheduled onboarding call

### During Call
- [ ] Created organization
- [ ] Created admin user
- [ ] Created project(s)
- [ ] Added team members
- [ ] Uploaded initial drawings
- [ ] Completed first query demo
- [ ] Explained next steps

### Post-Call
- [ ] Sent welcome email with docs
- [ ] Scheduled Day 3 check-in
- [ ] Added to customer success tracker

### Week 1 Follow-up
- [ ] Day 3: Check-in call/message
- [ ] Day 7: Review usage, optimize
- [ ] Confirmed they're self-sufficient
```

---

## Scaling: From White-Glove to Self-Service

### Phase 1: You do everything (First 10 customers)
- Personal onboarding calls
- Manual setup via admin panel
- Direct WhatsApp support
- **Learn what customers need**

### Phase 2: Guided self-service (Customers 11-50)
- Customer fills onboarding form
- You review and approve
- Automated account creation
- You upload drawings
- Video tutorials for team

### Phase 3: Full self-service (50+ customers)
- Sign up on website
- Self-service dashboard
- Automated drawing processing
- In-app onboarding flow
- Support via chat/ticket

---

## The Pitch Script for Onboarding Call

```
"Let me set you up right now - it takes about 30 minutes.

First, I'll create your company account and add your sites.
Then I'll add your team members - they'll each get a WhatsApp message.
We'll upload your drawings - you can share a Drive link or forward on WhatsApp.
Finally, we'll test it together - you send a question, see how it works.

By the end of this call, your team can start using SiteMind.

Ready? Let me share my screen and we'll get started..."
```

---

## Files Updated for Modularity

The codebase is designed so all customization happens through:

1. **Database configs** - Organization/Project/User settings
2. **Admin API** - Create/update via API calls
3. **Dashboard** - UI for all management
4. **NO CODE CHANGES** for customer customization

This means you can onboard 100 different customers with 100 different configurations without touching the code.

