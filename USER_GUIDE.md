# SiteMind User Guide

## How to Use SiteMind to Its Full Potential

---

## Quick Start (2 Minutes)

SiteMind is already in your WhatsApp. Just talk to it like you would a colleague.

**Try these right now:**

1. **Ask a question:**
   > "What is the column size at B2?"

2. **Log a decision:**
   > "Decision: Client approved marble flooring"

3. **Create an RFI:**
   > "RFI: Need clarification on balcony railing design"

4. **Get today's summary:**
   > "/summary"

That's it. You're using SiteMind.

---

## The Golden Rules

### Rule 1: Just Talk Normally

SiteMind understands natural language. You don't need special commands.

✅ **Good:** "What did the architect say about the staircase?"
✅ **Good:** "Show me the latest structural drawing"
✅ **Good:** "Who approved the tile change?"

❌ **Not needed:** Complex commands or specific formats

### Rule 2: Log Important Phone Calls

After any important call, send a quick message:

```
Call log: Spoke to [person]
- [What was discussed]
- [What was decided]
- [Any amounts/dates]
```

**Example:**
```
Call log: Spoke to client Mr. Sharma
- Approved kitchen cabinet upgrade
- Additional cost ₹2.5L accepted
- Delivery by end of month
```

### Rule 3: Start Decisions with "Decision:" or "Approved:"

When something is approved or decided, be explicit:

```
Decision: [What was decided] by [Who]
```

**Examples:**
```
Decision: Tile changed from ceramic to vitrified - approved by client
Decision: Extra waterproofing layer added - cost ₹1.2L
Approved: Balcony extension as per revised drawing
```

### Rule 4: Share Drawings Properly

When sharing a drawing, add a caption:

```
[Send PDF/Image]
Caption: STR-07 Revision R3 - Structural drawing for Block A
```

SiteMind will:
- Index the drawing
- Track the revision
- Alert if a newer version exists later

---

## Complete Command Reference

### 📋 Getting Information

| What You Want | What to Say |
|---------------|-------------|
| Ask about specs | "What is the beam size at C3?" |
| Find a drawing | "Show me the plumbing drawing for Floor 5" |
| Check who approved | "Who approved the tile change?" |
| Find old discussion | "What did consultant say about waterproofing?" |
| Check pending items | "What's pending for electrical work?" |

### ✅ Logging Decisions

| What You Want | What to Say |
|---------------|-------------|
| Log a decision | "Decision: [description]" |
| Log an approval | "Approved: [what was approved]" |
| Log a rejection | "Rejected: [what was rejected] - reason: [why]" |
| Log from a call | "Call log: [summary of call]" |

### 📝 Managing RFIs

| What You Want | What to Say |
|---------------|-------------|
| Create RFI | "RFI: [your question] @[who should answer]" |
| Check open RFIs | "/rfi" or "Show open RFIs" |
| Respond to RFI | "RFI response: [RFI number] - [your answer]" |
| Close RFI | "Close RFI: [RFI number]" |

### ⚠️ Reporting Issues

| What You Want | What to Say |
|---------------|-------------|
| Report issue | Just describe it: "Leakage found in unit 1204" |
| High priority | "URGENT: [issue description]" |
| Check issues | "/issues" or "Show open issues" |
| Resolve issue | "Resolved: [issue description]" |

### 📊 Getting Summaries

| What You Want | What to Say |
|---------------|-------------|
| Daily summary | "/summary" |
| Weekly report | "/report" |
| Project risks | "/risks" |
| Check progress | "What's the progress on Floor 5?" |

### 📐 Drawing Management

| What You Want | What to Say |
|---------------|-------------|
| Check revision | "/revision STR-07" |
| Find latest | "Latest structural drawing for Block B" |
| Compare versions | "What changed between R1 and R3 of STR-07?" |

---

## Best Practices by Role

### For Site Engineers

**Every morning:**
```
1. Check: /summary
2. Review any pending items
3. Plan your day
```

**When you need information:**
```
Don't call office. Just ask:
"What is [specification]?"
"Where is [drawing]?"
"Who approved [decision]?"
```

**When something happens:**
```
Just share in the group as usual.
SiteMind captures:
- Problems you mention
- Updates you share
- Questions you ask
```

**After important phone calls:**
```
Always log: "Call log: [summary]"
This creates a permanent record.
```

---

### For Project Managers

**Every morning:**
```
1. Review: /summary for each project
2. Check: /rfi for pending items
3. Check: /issues for problems
4. Check: /risks for upcoming concerns
```

**When making decisions:**
```
Always document:
"Decision: [description] - approved by [name]"

For money decisions:
"Decision: Extra work approved - ₹[amount]"
```

**Weekly:**
```
Generate report: /report
Share with management
```

---

### For Management

**Daily check (5 minutes):**
```
1. Login to dashboard
2. Review attention items
3. Check project health scores
```

**What to look for:**
```
🔴 Overdue RFIs (someone not responding)
🟡 High-severity issues (need escalation)
⚠️ Drawing conflicts (version problems)
📉 Low project health (needs attention)
```

---

## Real Scenarios & How to Handle Them

### Scenario 1: Client Approves Something on Phone

**What happens:**
Client calls and approves extra work worth ₹5 lakh.

**What to do immediately after the call:**
```
Call log: Client Mr. Sharma approved extra waterproofing
- Scope: All balconies + terraces
- Additional cost: ₹5.2 lakh
- Timeline: 2 weeks additional
- Payment: With next bill
```

**Why this matters:**
6 months later when client says "I never approved this", you have proof with exact date and time.

---

### Scenario 2: Someone Asks for Drawing

**What happens:**
Site engineer needs the structural drawing for Column C3.

**Old way:**
- Message in group
- Wait for someone to find it
- Hope it's the latest version
- 4 hours wasted

**New way:**
```
"What is the latest structural drawing for Column C3?"

SiteMind: "Drawing STR-08, Revision R3
          Column C3 details on Page 12
          Uploaded: 10-Dec-2024 by Priya
          
          Key specs:
          - Size: 500mm x 500mm
          - Rebar: 16T20
          - Concrete: M35"
```

**Time saved:** 4 hours → 10 seconds

---

### Scenario 3: Consultant Not Responding

**What happens:**
You asked architect about railing design 4 days ago. No response.

**How to track it:**
```
Original message:
"RFI: Need clarification on balcony railing design @Architect"

Check status:
"/rfi"

SiteMind shows:
"RFI-2024-0045: Balcony railing design
 Status: 🔴 OVERDUE (4 days)
 Assigned to: Architect
 
 Escalation recommended."
```

**What to do:**
Forward the RFI status to architect's manager.

---

### Scenario 4: Wrong Drawing Used

**What happens:**
Site built something with the wrong drawing version.

**How SiteMind prevents this:**

When someone shares a drawing:
```
SiteMind: "📐 Drawing received: STR-07

          ⚠️ VERSION WARNING
          This is Revision R1
          Current latest is Revision R3 (uploaded 5 days ago)
          
          Changes in R3:
          - Column C3 size changed 400→500mm
          - Rebar updated for Column B2
          
          Please confirm you want to use R1"
```

---

### Scenario 5: Finding Old Information

**What happens:**
Need to find what was discussed about waterproofing 3 months ago.

**Old way:**
- Scroll through thousands of messages
- Check multiple groups
- Ask people if they remember
- Maybe find it after 2 hours

**New way:**
```
"What was discussed about waterproofing in September?"

SiteMind: "Found 5 related conversations:

          1. 15-Sep: Consultant recommended Dr. Fixit
          2. 18-Sep: Decision - Use 2 coats for balconies
          3. 22-Sep: RFI about terrace waterproofing (Resolved)
          4. 25-Sep: Material ordered from ABC Suppliers
          5. 28-Sep: First coat applied Floor 3
          
          Most relevant: Decision on 18-Sep by PM Rajesh"
```

---

### Scenario 6: Management Needs Update

**What happens:**
Director asks "What's happening on Skyline project?"

**Old way:**
- Call PM
- PM calls site engineers
- Compile information
- 2 hours later, incomplete picture

**New way:**
```
Director checks dashboard or asks:
"/summary Skyline"

Instant response with:
- Progress updates
- Issues reported
- Decisions made
- Pending items
- Upcoming risks
```

---

## Tips for Maximum Value

### Tip 1: Be Specific in Decisions

**Weak:**
```
"Approved the change"
```

**Strong:**
```
"Decision: Approved changing floor tile from ceramic 
to vitrified in all bedrooms - additional cost ₹3.5L 
- approved by client Mr. Sharma"
```

The strong version is searchable and has all details for audit.

---

### Tip 2: Log Money Decisions Separately

Anything involving cost should be explicitly logged:

```
Cost decision: Extra plumbing points in kitchen
- 4 additional points
- Cost: ₹12,000
- Approved by: Client
- Reason: Kitchen layout change
```

---

### Tip 3: Use RFIs for External Questions

Any question that goes outside your team:

```
RFI: [Question] @[Architect/Consultant/Client]
```

This ensures:
- Question is tracked
- Reminder sent if no response
- Full history maintained

---

### Tip 4: Share Context with Drawings

When uploading drawings:

```
[Send PDF]
Caption: STR-12 R3 - Structural drawing Block B
         Changes from R2: Column grid shifted
         For: Floors 5-10
```

---

### Tip 5: Daily Summary Check

Start every day with:
```
/summary
```

Takes 2 minutes. Saves 2 hours.

---

## Troubleshooting

### "SiteMind didn't understand me"

**Try being more specific:**
```
Instead of: "What about the columns?"
Try: "What is the size of column at grid B2?"
```

### "I can't find a drawing"

**Try different searches:**
```
"Latest STR-07"
"Structural drawing Floor 5"
"Drawing uploaded by Priya last week"
```

### "Decision not logged properly"

**Always start with Decision: or Approved:**
```
"Decision: [clear description]"
```

### "RFI not created"

**Include RFI: at the start:**
```
"RFI: [your question] @[person]"
```

---

## Getting Help

**In WhatsApp:**
```
/help - Shows all commands
```

**Common commands:**
```
/help      - Show help
/summary   - Daily summary
/rfi       - List RFIs
/issues    - List issues
/risks     - Show risks
/report    - Weekly report
/revision  - Check drawing version
/project   - Switch projects
```

---

## Remember

> **SiteMind works best when you work naturally.**
> 
> Don't overthink it. Just:
> - Ask questions normally
> - Share drawings normally
> - Log important decisions
> - Log important phone calls
> 
> SiteMind handles the rest.

---

*Questions? Just ask SiteMind: "Help with [topic]"*

