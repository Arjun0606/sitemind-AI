# SiteMind - Final Business Plan

> **THE PROJECT BRAIN FOR CONSTRUCTION**
> 
> *Information leakage = Money leakage. We fix that.*

---

## 🎯 THE ONE-LINER

**SiteMind connects every drawing, decision, and photo on your project. AI catches expensive mistakes before they happen.**

---

## 💡 THE INSIGHT

Every construction project leaks money because **information is scattered**:

| Where Info Lives | What Gets Lost |
|-----------------|----------------|
| WhatsApp groups (10+) | Decisions, approvals |
| Email threads | Change orders |
| Individual phones | Site photos |
| File servers | Drawing revisions |
| Excel sheets | BOQ, material orders |

**Result:** Wrong work gets done. Rework costs ₹5-15 lakh per incident. Change orders go unbilled. Material gets over-ordered. Disputes can't be resolved.

---

## 🧠 THE SOLUTION: CONNECTED INTELLIGENCE

**One place where everything lives. AI that connects it all.**

```
┌──────────────────────────────────────────────────────────────────┐
│                    SITEMIND = PROJECT BRAIN                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DUMP EVERYTHING                    AI CONNECTS EVERYTHING       │
│  ─────────────────                  ─────────────────────────    │
│  • Drawings/PDFs                    • Photo ↔ Stored specs       │
│  • Site photos                      • Question ↔ Past decisions  │
│  • Decisions                        • Order ↔ BOQ quantities     │
│  • Change orders                    • Change ↔ Original scope    │
│  • Questions                                                     │
│                                     CATCHES EXPENSIVE MISTAKES   │
│  Everything stored forever          ─────────────────────────    │
│  Everything searchable              • Rebar mismatch: ₹5L saved  │
│  Everything citeable                • Cover wrong: ₹3L saved     │
│                                     • Over-order: ₹2L saved      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 💰 THE VALUE

### What SiteMind Catches (Per Incident)

| Catch Type | Cost Prevented |
|-----------|---------------|
| Rebar diameter mismatch | ₹3-5 lakh |
| Concrete grade wrong | ₹2-4 lakh |
| Dimension mismatch | ₹2-5 lakh |
| Cover insufficient | ₹1.5-3 lakh |
| Unbilled change order | ₹50K-5 lakh |
| Material over-order | ₹10K-1 lakh |

**Conservative: 5-10 catches/month = ₹10-30 lakh saved**

---

## 🏷️ PRICING

### Single Plan: $1,000/month

```
SITEMIND ENTERPRISE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$1,000 USD/month (₹83,000)

INCLUDED:
✓ Unlimited projects
✓ Unlimited users
✓ 1,000 AI queries/month
✓ 50 document uploads/month
✓ 200 photo analyses/month
✓ 50 GB storage

USAGE OVERAGES (90% margin):
• Additional query: $0.25
• Additional document: $0.45
• Additional photo: $0.15
• Additional storage: $2.00/GB

DISCOUNTS:
• Annual payment: 17% off ($10,000/year)
• Founding customer: 25% off first year
```

### 🎁 Pilot Program (First 3 Customers)

```
PILOT OFFER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Month 1: FREE (full access, no limits)
Month 2+: $1,000/month (or 25% off as founding customer)

WHAT WE NEED FROM THEM:
• Upload existing drawings/specs
• Use daily for real projects
• Honest feedback
• Testimonial if happy

WHAT THEY GET:
• Full product access
• Priority support (direct WhatsApp)
• Input on features
• Founding customer pricing forever
```

### Why This Pricing Works

```
COST TO CUSTOMER:      ₹83,000/month

LESS THAN:
• 1 site engineer salary (₹50-80K)
• 1 day of crane rental (₹15-25K/day)
• 1 cement truck (₹50K)

VALUE DELIVERED:
• 1 rebar mismatch caught = ₹3-5L saved
• 1 dimension error caught = ₹2-5L saved
• 5-10 catches/month = ₹10-30L saved

ROI: 12-36x
```

---

## 🎯 TARGET MARKET: WHALES

### Primary Target
Large real estate developers in India with 10+ active sites.

| Customer Type | Sites | Monthly Revenue | Annual Revenue |
|--------------|-------|-----------------|----------------|
| Mid-size developer | 5-10 | $1,000-2,000 | $12K-24K |
| Large developer | 20-50 | $1,000 + overages | $15K-25K |
| **Whale (Urbanrise-level)** | 100+ | $1,000 + heavy overages | $20K-50K |

### Revenue Projections

| Milestone | Customers | Monthly Revenue |
|-----------|-----------|-----------------|
| MVP | 3 (pilot) | $0 (free) |
| Month 3 | 10 | $10,000 |
| Month 6 | 30 | $35,000 |
| Month 12 | 50 | $60,000 |
| Month 18 | 100 | $120,000+ |

**Goal: $100K/month by Month 12**

---

## 🛠️ TECH STACK

### Core Services (All Integrated)

| Service | Purpose | Cost |
|---------|---------|------|
| **Gemini 3 Pro** | AI brain - understands everything | ~$0.008/query |
| **Supermemory.ai** | Project memory - stores everything forever | $19/month + overages |
| **Supabase** | Database + file storage | $25/month + overages |
| **Twilio** | WhatsApp Business API | ~$0.005/message |
| **Dodo Payments** | Billing (India-focused) | TBD |

### Architecture

```
WhatsApp (Twilio)
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                       │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  WhatsApp   │  │ Connected   │  │  Dashboard  │    │
│  │   Router    │  │Intelligence │  │    API      │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│         │                │                │            │
│         ▼                ▼                ▼            │
│  ┌─────────────────────────────────────────────────┐  │
│  │              CORE SERVICES                       │  │
│  │  • Gemini Service (AI)                          │  │
│  │  • Memory Service (Supermemory)                 │  │
│  │  • Storage Service (Supabase)                   │  │
│  │  • Billing Service                              │  │
│  └─────────────────────────────────────────────────┘  │
│                          │                             │
└──────────────────────────│─────────────────────────────┘
                           ▼
              ┌─────────────────────────┐
              │       SUPABASE          │
              │  • PostgreSQL (data)    │
              │  • Storage (files)      │
              └─────────────────────────┘
```

---

## 🔥 THE MAGIC: AI-FIRST, NO PATTERN MATCHING

### How It Works

```
1. SITE ENGINEER SENDS PHOTO
   ─────────────────────────
   Photo of column rebar received via WhatsApp
   
2. AI ANALYZES + CROSS-REFERENCES
   ───────────────────────────────
   Gemini: "I see 10mm rebar @ 200mm spacing"
   Supermemory: "Drawing STR-07 says 12mm @ 150mm c/c"
   
3. MISMATCH DETECTED
   ──────────────────
   ⚠️ "Photo shows 10mm @ 200mm"
   📐 "Spec says 12mm @ 150mm (STR-07, Dec 5)"
   💰 "Fix now or ₹4-5 lakh rework"
   
4. VALUE DELIVERED
   ─────────────────
   Caught before concrete pour
   ₹5 lakh saved
   Paid for 5 months of SiteMind
```

### Key Principle: AI Does Everything

- **NO** regex for detecting change orders
- **NO** keyword matching for issues
- **NO** hardcoded rules
- **EVERYTHING** goes through Gemini
- **EVERYTHING** gets stored in Supermemory
- **EVERYTHING** has citations

---

## 📱 USER EXPERIENCE

### Site Engineers (WhatsApp)

```
Just chat. Send anything. Get answers with citations.

User: "column size at B2?"
SiteMind: "450mm x 450mm with 12T16 bars
          (per Drawing STR-07, uploaded Dec 5 by Rajesh)"

User: [sends photo]
SiteMind: "⚠️ MISMATCH: Rebar appears to be 10mm, 
          spec requires 12mm. Stop work and verify.
          Potential cost if poured: ₹3-5 lakh"
```

### Management (Web Dashboard)

```
┌─────────────────────────────────────────────────────────────┐
│  SITEMIND DASHBOARD                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VALUE PROTECTED          MISMATCHES CAUGHT                 │
│  ₹28.4 Lakh              12 this month                      │
│                                                             │
│  🔴 OPEN ALERTS                                             │
│  ────────────────────────────────────────────────────────   │
│  [CRITICAL] Rebar mismatch Grid B2 - ₹4.5L at risk         │
│  [HIGH] Column dimension undersized - ₹2.8L at risk        │
│                                                             │
│  PROJECTS                 RECENT ACTIVITY                   │
│  ────────────             ─────────────────                 │
│  Skyline Towers (2 alerts)   Photo analyzed - matched      │
│  Green Valley (0 alerts)     Question answered             │
│  Phoenix Mall (1 alert)      Drawing uploaded              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

---

## ⚡ THE $1000 WOW FACTOR

### Why It's Worth $1000/month

```
SCALE OF THEIR PROJECTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Large Developer (20+ projects):
• Monthly construction spend:     ₹50-200 crore
• Site engineer salaries:         ₹20-50 lakh/month
• Crane/equipment rental:         ₹10-30 lakh/month
• One rework incident:            ₹5-50 lakh

SiteMind:                         ₹83,000/month
                                  = 0.004% of spend
                                  = Less than 1 engineer
                                  = Less than 1 day equipment

ONE CATCH PAYS FOR THE YEAR.
```

### First Hour Experience (WOW Guaranteed)

```
MINUTE 0-5: WELCOME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Professional welcome with company name
Clear setup steps
"Your Project Brain is ready"

MINUTE 5-15: FIRST DRAWING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Upload ONE drawing
AI extracts specs IN REAL-TIME
"I found 12 specifications in this drawing"
Shows exactly what it understood
WOW MOMENT #1 ✓

MINUTE 15-30: FIRST QUESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ask any question about the drawing
AI answers WITH CITATION
"Column B2 is 450mm x 450mm (per Drawing STR-07)"
WOW MOMENT #2 ✓

MINUTE 30-45: FIRST PHOTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Send a site photo
AI cross-references against stored specs
Shows verification even if it matches
"✅ Verified against Drawing STR-07"
WOW MOMENT #3 ✓

MINUTE 45-60: DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Show web dashboard
Already has their data
Professional, enterprise-grade
"This is worth $1000/month"
WOW MOMENT #4 ✓
```

### What Makes It Feel Worth $1000

| Element | How We Deliver |
|---------|----------------|
| **Instant Value** | Specs extracted in 30 seconds |
| **Professional UI** | Enterprise-grade dashboard |
| **Smart AI** | Citations on EVERY answer |
| **Clear ROI** | Value protected shown prominently |
| **Polished Messages** | Structured, branded, consistent |
| **Real Cross-Reference** | Photos verified against specs |

---

## 📈 GO-TO-MARKET

### Phase 1: Pilot (Month 1-2)
- 3 founding customers (free for 3 months)
- Daily hands-on support
- Iterate based on feedback
- Goal: Prove value, get testimonials

### Phase 2: Early Sales (Month 3-6)
- Founding customer discount (25% off)
- Word-of-mouth from pilot customers
- Target: 10-20 paying customers
- Goal: $20K MRR

### Phase 3: Scale (Month 6-12)
- Case studies with ROI data
- Target larger developers
- Expand to adjacent cities
- Goal: $100K MRR

### Phase 4: Whale Hunting (Month 12+)
- Target Urbanrise-level customers
- Custom enterprise deals
- Goal: $200K+ MRR

---

## 💵 UNIT ECONOMICS

### Per Customer

```
REVENUE:
• Base: $1,000/month
• Avg overages: $200/month
• Total: $1,200/month

COST:
• Gemini: ~$15/month (at 1000 queries)
• Supermemory: ~$10/month (share of $19 pro plan)
• Supabase: ~$5/month (share of $25 pro plan)
• Twilio: ~$20/month
• Total: ~$50/month

MARGIN: 96%
```

### At Scale (50 customers)

```
MONTHLY:
• Revenue: $60,000
• COGS: $2,500
• Gross Margin: $57,500 (96%)
• Infrastructure: $1,000 (Railway, monitoring)
• Net: $56,500/month

ANNUAL: $678,000 profit
```

---

## 🎯 SUCCESS METRICS

### Week 1 (Per Customer)
- [ ] 5+ specs uploaded
- [ ] 10+ questions answered
- [ ] 1+ photo analyzed
- [ ] 1+ mismatch caught (or no mismatches = compliant)

### Month 1 (Per Customer)
- [ ] Daily active usage
- [ ] 5+ mismatches caught
- [ ] ₹5L+ value protected
- [ ] "Can't live without it" feedback

### Company-wide
- [ ] Month 3: 10 paying customers
- [ ] Month 6: $50K MRR
- [ ] Month 12: $100K MRR
- [ ] Month 18: $200K MRR

---

## 🏁 IMMEDIATE NEXT STEPS

1. **Clean codebase** - Remove all legacy/redundant code
2. **Test full flow** - WhatsApp → AI → Dashboard
3. **Deploy** - Railway.app for backend, Vercel for dashboard
4. **Onboard pilot customer** - First real test
5. **Iterate** - Based on real usage

---

## 📝 THE PITCH

> "Every construction project leaks money because information is scattered across WhatsApp groups, emails, and phones.
> 
> SiteMind is the Project Brain. One place where every drawing, decision, and photo lives. AI that connects everything and catches expensive mistakes before they happen.
> 
> Our pilot customer caught a ₹4 lakh rebar error from a single site photo. That one catch paid for 4 years of SiteMind.
> 
> Zero information gaps. Zero money leaks."

---

**This is the plan. This is the product. Let's build it.**

*Last updated: December 8, 2025*

