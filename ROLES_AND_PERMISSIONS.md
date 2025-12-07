# SiteMind Roles & Permissions Guide

## Overview

SiteMind uses a role-based access control system with inheritance:

```
Organization Owner
    └── Organization Admin
        └── Project Manager (PM)
            └── Site Engineer
            └── Consultant (External)
            └── Viewer (Read-only)
```

---

## Role Definitions

### 👑 Owner

**Who:** Company founder, MD, CEO, or primary decision maker

**Typical Person:** Mr. Sharma (Builder/Developer)

**Access:**
- Full access to everything
- Can manage billing and subscription
- Can add/remove admins
- Can view all projects
- Receives executive summaries

**Default Notifications:**
- Morning brief ✅
- Critical red flags ✅
- Weekly reports ✅
- Task updates ❌

---

### 🔑 Admin

**Who:** Company administrator, office manager

**Typical Person:** Office Manager, Accounts Head

**Access:**
- Can manage all projects
- Can add/remove users (except owners)
- Can view reports and analytics
- Cannot manage billing

**Default Notifications:**
- Morning brief ✅
- All red flags ✅
- Weekly reports ✅
- Task updates ✅

---

### 📋 Project Manager (PM)

**Who:** Site-level manager, project coordinator

**Typical Person:** Site PM, Project Coordinator

**Access:**
- Full access to assigned projects only
- Can create and assign tasks
- Can upload documents
- Can view project reports
- Can manage site engineers

**Default Notifications:**
- Morning brief ✅
- Project red flags ✅
- Weekly reports ✅
- All task updates ✅

---

### 👷 Site Engineer

**Who:** On-ground technical staff

**Typical Person:** Site Engineer, Junior Engineer, Supervisor

**Access:**
- Can query blueprints and specs
- Can upload site photos
- Can update task status
- Can record material consumption
- Cannot upload drawings
- Cannot view reports/analytics

**Default Notifications:**
- Morning brief ❌
- Red flags ❌
- Weekly reports ❌
- Task assignments ✅

---

### 🏛️ Consultant

**Who:** External architects, structural consultants

**Typical Person:** Architect, Structural Engineer (external firm)

**Access:**
- Can view project drawings
- Can respond to RFIs
- Can upload documents (their drawings)
- Cannot create tasks
- Cannot record materials
- Cannot view internal reports

**Default Notifications:**
- Morning brief ❌
- Red flags ❌
- Weekly reports ✅ (for their drawings)
- RFI responses ✅

---

### 👁️ Viewer

**Who:** Observers, investors, management

**Typical Person:** Investor, Board Member, Senior Management

**Access:**
- Read-only access
- Can view reports
- Can view progress
- Cannot interact with system

**Default Notifications:**
- Morning brief ❌
- Red flags ❌
- Weekly reports ✅
- Task updates ❌

---

## Permission Matrix

| Permission | Owner | Admin | PM | Site Engineer | Consultant | Viewer |
|-----------|:-----:|:-----:|:--:|:-------------:|:----------:|:------:|
| **QUERIES** |
| Ask questions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View query history | ✅ | ✅ | ✅ | Own | Own | ❌ |
| **DOCUMENTS** |
| Upload drawings | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Upload photos | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Download documents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete documents | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **TASKS** |
| Create tasks | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Assign tasks | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Update task status | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View all tasks | ✅ | ✅ | ✅ | Own | ❌ | ✅ |
| **MATERIALS** |
| Record receipt | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Record consumption | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View inventory | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Create orders | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **REPORTS** |
| View reports | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Export data | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Custom reports | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **TEAM** |
| Add users | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Remove users | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Change roles | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **SETTINGS** |
| Org settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Project settings | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Billing | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **DASHBOARD** |
| Access dashboard | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| View analytics | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| View audit trail | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## Custom Permission Scenarios

### Scenario 1: Trusted Senior Site Engineer

Customer says: "Ramesh has been with us for 10 years, give him more access"

```json
{
  "user_id": "user_xxx",
  "role": "site_engineer",
  "permissions": {
    "can_query": true,
    "can_upload_documents": true,  // Upgraded
    "can_upload_photos": true,
    "can_create_tasks": true,      // Upgraded
    "can_view_reports": true,      // Upgraded
    "can_record_materials": true
  }
}
```

### Scenario 2: Restricted Consultant

Customer says: "Architect should only see structural drawings, not MEP"

```json
{
  "user_id": "user_xxx",
  "role": "consultant",
  "permissions": {
    "can_query": true,
    "can_upload_documents": true,
    "visible_disciplines": ["structural", "architectural"]  // Restricted
  }
}
```

### Scenario 3: Store Keeper Role

Customer says: "Store keeper should only handle materials, nothing else"

```json
{
  "user_id": "user_xxx",
  "role": "site_engineer",  // Base role
  "permissions": {
    "can_query": false,           // Restricted
    "can_upload_documents": false,
    "can_upload_photos": false,
    "can_create_tasks": false,
    "can_view_reports": false,
    "can_record_materials": true  // Only this
  }
}
```

### Scenario 4: Junior PM

Customer says: "New PM, give limited access until trained"

```json
{
  "user_id": "user_xxx",
  "role": "pm",
  "permissions": {
    "can_create_tasks": true,
    "can_assign_tasks": false,    // Restricted until trained
    "can_view_reports": true,
    "can_manage_team": false      // Restricted
  }
}
```

---

## Multi-Project Access

For users who work across multiple sites:

```json
{
  "user_id": "user_xxx",
  "organization_role": "pm",  // Default role
  "project_roles": {
    "proj_001": "pm",           // Full PM on this project
    "proj_002": "pm",           // Full PM on this project
    "proj_003": "viewer"        // Just observing this one
  }
}
```

---

## Notification Customization

Each user can customize their notifications:

```json
{
  "user_id": "user_xxx",
  "notification_preferences": {
    "morning_brief": true,
    "morning_brief_time": "06:30",  // Custom time
    "red_flags": {
      "critical": true,
      "high": true,
      "medium": false,
      "low": false
    },
    "task_updates": {
      "assigned_to_me": true,
      "created_by_me": true,
      "all_project": false
    },
    "weekly_reports": true,
    "daily_summary": false
  }
}
```

---

## Common Permission Questions

### "Can a Site Engineer see reports?"

**Default:** No
**Customizable:** Yes, set `can_view_reports: true`

### "Can a PM add new sites?"

**Default:** No (only Admin/Owner)
**Why:** Sites affect billing, need admin approval

### "Can Consultants see material data?"

**Default:** No
**Customizable:** Yes, but not recommended (internal data)

### "Can we have multiple Owners?"

**Yes**, set additional users with role "owner"

### "Can we restrict access to specific floors/areas?"

**Coming soon** - Area-based access control is on the roadmap

---

## Audit Trail

All permission changes are logged:

```
2024-12-07 10:30:15 | user_abc | permission_changed
  Changed by: admin_xyz
  User: Ramesh Kumar (user_abc)
  Permission: can_upload_documents
  Old value: false
  New value: true
  Reason: "Promoted to senior engineer"
```

---

## API Endpoints for Permission Management

```bash
# Get user permissions
GET /api/admin/users/{user_id}/permissions

# Update specific permissions
POST /api/admin/users/{user_id}/permissions
{
  "can_upload_documents": true,
  "can_view_reports": true
}

# Reset to role defaults
POST /api/admin/users/{user_id}/permissions/reset

# Get role defaults
GET /api/admin/roles/{role}/permissions
```

---

## Best Practices

1. **Start Restrictive:** Give minimum permissions, add as needed
2. **Role First:** Assign correct role, then customize if needed
3. **Document Changes:** Note why permissions were changed
4. **Review Quarterly:** Check if permissions still make sense
5. **Offboarding:** Remove access immediately when someone leaves

