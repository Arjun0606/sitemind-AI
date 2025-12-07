# SiteMind Onboarding Cheatsheet

**Print this and keep it handy during customer calls**

---

## 🚀 Quick Setup (30 min call)

```
BEFORE CALL:
□ Customer intake form filled
□ Drive link ready (if they have drawings)
□ Your laptop + internet ready

DURING CALL:
┌─────────────────────────────────────────────────────┐
│  0-5 min   Confirm details                          │
│  5-15 min  Create accounts (they watch)             │
│  15-25 min Demo - they send first query             │
│  25-30 min Next steps, Q&A                          │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Info to Collect

```
MUST HAVE:
✓ Company name
✓ Admin name + phone + email
✓ Site name(s)
✓ Team member phones

NICE TO HAVE:
○ Site addresses
○ Team member names
○ Drawings (can get later)
```

---

## ⚡ One-Command Setup

```bash
curl -X POST https://api.sitemind.ai/admin/quick-setup \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "COMPANY",
    "admin_name": "NAME",
    "admin_email": "EMAIL",
    "admin_phone": "+91PHONE",
    "sites": [{
      "name": "SITE",
      "team": [
        {"name": "NAME", "phone": "+91PHONE", "role": "site_engineer"}
      ]
    }],
    "plan": "pilot"
  }'
```

---

## 👥 Role Quick Reference

| Role | Who | WhatsApp | Dashboard |
|------|-----|----------|-----------|
| **owner** | MD/CEO | ✅ Full | ✅ Full |
| **admin** | Office mgr | ✅ Full | ✅ No billing |
| **pm** | Site PM | ✅ Full | ✅ Project only |
| **site_engineer** | On-site | ✅ Query + photos | ❌ |
| **consultant** | Architect | ✅ Query + RFI | ✅ Limited |
| **viewer** | Investor | ✅ Query only | ✅ Read-only |

---

## 🔧 Common Customizations

| Customer Says | API Call |
|--------------|----------|
| "Change bot name to XYZ" | `{"branding": {"assistant_name": "XYZ"}}` |
| "Hindi responses" | `{"language": "hi"}` |
| "Brief at 6 AM" | `{"morning_brief_time": "06:00"}` |
| "No material tracking" | `{"enable_material_tracking": false}` |
| "Engineer can't upload" | `{"permissions": {"can_upload_photos": false}}` |

---

## 💬 Scripts

### Opening
> "Let me set you up right now - takes about 30 minutes. By the end, your team can start using SiteMind. Ready?"

### First Demo
> "Perfect, setup done! Now try it - send any question. Like 'beam size B3 floor 2' or just 'khamba B3?'"

### Drawings
> "Do you have drawings in Google Drive? Share the link and I'll sync them. Or just forward PDFs to the WhatsApp number."

### Closing
> "Your team will get welcome messages shortly. I'll check in on Day 3 to see how it's going. Any questions?"

---

## ⚠️ Common Issues

| Issue | Fix |
|-------|-----|
| "Not receiving messages" | Check phone number has +91 |
| "Wrong answers" | Need to upload drawings first |
| "Too many notifications" | Adjust notification settings |
| "Need more users" | Just add them, no limit |
| "Want another site" | Add project, same org |

---

## 📞 Post-Call Checklist

```
□ Welcome messages sent
□ Drawings uploaded (or Drive synced)
□ First query demo successful
□ Day 3 check-in scheduled
□ Added to customer tracker
□ Invoice/pilot docs sent
```

---

## 🎯 Day 3 Check-In Script

> "Hi! Just checking in on SiteMind. How's it working? Any questions from your team?"

**Listen for:**
- Usage frequency (5+ queries/day = good)
- Any confusion
- Missing drawings
- Feature requests

---

## 💰 Pricing Quick Reference

```
STANDARD:
$500/site/month

VOLUME DISCOUNTS:
3+ sites → 10% off = $450/site
6+ sites → 15% off = $425/site
10+ sites → 25% off = $375/site

PILOT:
First 3 months FREE for first 10 customers
```

---

## 🆘 Emergency Contacts

```
Technical issues: [Your phone]
Billing questions: [Your email]
```

---

*Last updated: December 2024*

