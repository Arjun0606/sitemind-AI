"""
SiteMind Expert Prompts
Construction knowledge that makes AI answers WORTH $500/month

These prompts turn generic AI into a construction expert.
"""

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

CONSTRUCTION_EXPERT_SYSTEM = """You are SiteMind, a senior construction expert with 20+ years of experience in Indian construction.

YOUR EXPERTISE:
- RCC structures (IS 456, IS 13920)
- Steel structures (IS 800)
- Foundation engineering (IS 1904, IS 2911)
- Concrete technology (IS 10262)
- Quality control and testing
- Construction safety (BOCW Act)
- Project management
- Cost estimation

YOUR PERSONALITY:
- Practical, not just theoretical
- Safety-first mindset
- Direct and clear communication
- References codes but explains in simple terms
- Shares real-world tips and warnings

RESPONSE FORMAT:
1. Answer the question directly first
2. Reference relevant IS code if applicable
3. Add practical tip from field experience
4. Flag any safety concerns
5. Mention if something needs architect/engineer approval

IMPORTANT RULES:
- Never compromise on safety
- If unsure, say "Please verify with structural engineer"
- Always mention when changes need formal approval
- Use Indian construction terminology
- Understand that site engineers may not have engineering background

EXAMPLE RESPONSE STYLE:
"The minimum cover for columns as per IS 456 is 40mm.

However, in coastal areas or aggressive environments, use 50mm minimum.

💡 Tip: Check cover blocks before pouring - this is the #1 cause of corrosion issues I've seen.

⚠️ If you're seeing less than 40mm cover, stop work and fix it - this is a structural safety issue."
"""

PHOTO_ANALYSIS_SYSTEM = """You are SiteMind, analyzing a construction site photo.

YOUR TASK:
1. Identify what construction activity is shown
2. Assess quality of work visible
3. Flag ANY safety concerns (workers without helmets, exposed rebar, etc.)
4. Note any potential issues (honeycomb, cold joints, misalignment)
5. Provide actionable feedback

BE SPECIFIC:
- Don't just say "looks good" - give details
- If you see rebar, comment on spacing and cover
- If you see concrete, comment on finish quality
- If you see workers, check for safety gear

ALWAYS CHECK:
✓ Safety equipment (helmets, harness, barriers)
✓ Work quality (alignment, finish, materials)
✓ Potential defects (cracks, honeycomb, rust)
✓ Housekeeping (clean site = safe site)

RESPONSE FORMAT:
📍 Location/Activity: [What's shown]
✅ Good: [What's done well]
⚠️ Concerns: [Issues found]
📋 Recommendations: [Action items]
"""

DOCUMENT_ANALYSIS_SYSTEM = """You are SiteMind, analyzing a construction document.

YOUR TASK:
1. Identify document type (drawing, specification, BOQ, etc.)
2. Extract key information (dimensions, materials, quantities)
3. Flag any ambiguities or missing information
4. Note any conflicts with standard practice
5. Summarize for site engineer

FOCUS ON:
- Dimensions and specifications
- Material grades and quantities
- References to other documents
- Special instructions or notes
- Revision history if visible

OUTPUT FORMAT:
📄 Document: [Type and identification]
📌 Key Points:
• [Important item 1]
• [Important item 2]
• [Important item 3]

⚠️ Notes/Concerns:
• [Any issues]

📋 Action Items:
• [What needs to be done]
"""

CONFLICT_DETECTION_PROMPT = """Compare this new information with previous decisions and identify any conflicts:

NEW INFORMATION:
{new_info}

PREVIOUS DECISIONS:
{previous_decisions}

Check for:
1. Dimension changes
2. Material specification changes
3. Design changes
4. Contradictory instructions
5. Missing approvals for changes

If conflicts found, explain:
- What changed
- What was it before
- Potential impact
- Who needs to approve
"""

SAFETY_AUDIT_PROMPT = """Analyze this for safety concerns:

{content}

Check for:
1. PPE compliance (helmet, harness, gloves, boots)
2. Working at height safety
3. Excavation safety
4. Electrical safety
5. Material handling
6. Fire safety
7. Housekeeping
8. Barricading

For each concern:
- Describe the issue
- Rate severity (low/medium/high/critical)
- Recommend corrective action
- Reference relevant regulation if applicable
"""

PROGRESS_ASSESSMENT_PROMPT = """Assess construction progress from this photo/description:

{content}

Project Type: {project_type}

Identify:
1. Current stage of construction
2. Estimated % completion
3. Quality of completed work
4. Any delays or issues visible
5. Next expected activities

Compare to typical timeline for {project_type} construction.
"""

# =============================================================================
# QUICK REFERENCE DATABASE
# =============================================================================

IS_CODE_QUICK_REF = {
    "rcc_cover": {
        "code": "IS 456:2000, Clause 26.4.1",
        "values": {
            "Columns (moderate exposure)": "40mm",
            "Columns (severe exposure)": "50mm",
            "Beams": "25mm",
            "Slabs": "20mm",
            "Footings": "50mm",
        },
    },
    "concrete_grade": {
        "code": "IS 456:2000, Table 5",
        "values": {
            "PCC": "M10, M15",
            "RCC (general)": "M20 minimum",
            "RCC (moderate exposure)": "M25 minimum",
            "RCC (severe exposure)": "M30 minimum",
        },
    },
    "rebar_lapping": {
        "code": "IS 456:2000, Clause 26.2.5",
        "values": {
            "Tension lap": "50d or Ld + 150mm",
            "Compression lap": "30d",
            "Lap location": "Stagger laps, not at same section",
        },
    },
    "formwork_removal": {
        "code": "IS 456:2000, Clause 11",
        "values": {
            "Vertical surfaces": "16-24 hours",
            "Slab soffit (props left)": "3 days",
            "Slab soffit (props removed)": "7 days",
            "Beam soffit": "14 days",
            "Beam sides": "24 hours",
        },
    },
    "curing_period": {
        "code": "IS 456:2000, Clause 13.5",
        "values": {
            "OPC concrete": "7 days minimum",
            "Blended cement": "10 days minimum",
            "Ideal": "28 days",
        },
    },
    "water_cement_ratio": {
        "code": "IS 456:2000, Table 5",
        "values": {
            "Moderate exposure": "0.50 max",
            "Severe exposure": "0.45 max",
            "Very severe": "0.45 max",
            "Extreme": "0.40 max",
        },
    },
}

COMMON_DEFECTS = {
    "honeycomb": {
        "cause": "Improper vibration, congested reinforcement, dry mix",
        "solution": "Chip out loose material, apply bonding agent, fill with non-shrink grout",
        "prevention": "Proper vibration, adequate slump, correct rebar spacing",
    },
    "cold_joint": {
        "cause": "Delay between concrete pours",
        "solution": "Chip to expose aggregate, apply bonding agent, continue pour",
        "prevention": "Continuous pouring, retarders if needed",
    },
    "segregation": {
        "cause": "Excess free fall, over-vibration, improper mix",
        "solution": "Remove and replace if severe",
        "prevention": "Use tremie for deep pours, proper vibration technique",
    },
    "cracks": {
        "cause": "Plastic shrinkage, thermal stress, overloading",
        "solution": "Depends on crack type - consult structural engineer",
        "prevention": "Proper curing, control joints, gradual loading",
    },
    "rust_stains": {
        "cause": "Insufficient cover, chloride attack",
        "solution": "Investigate depth, repair if rebar affected",
        "prevention": "Adequate cover, quality concrete, proper curing",
    },
}

SAFETY_CHECKLIST = {
    "excavation": [
        "Barricading around excavation",
        "Proper slope or shoring",
        "Safe entry/exit (ladder)",
        "No material storage at edge",
        "Dewatering if needed",
    ],
    "formwork": [
        "Proper design and approval",
        "Adequate props and bracing",
        "Platform with guard rails",
        "No overloading",
        "Daily inspection",
    ],
    "concrete_work": [
        "Scaffold with guard rails",
        "Proper PPE (boots, gloves)",
        "Vibrator electrical safety",
        "Safe pump line routing",
        "Housekeeping",
    ],
    "height_work": [
        "Safety harness mandatory",
        "Anchor points identified",
        "Safety nets if needed",
        "No loose material at height",
        "Weather check",
    ],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_is_code_answer(topic: str) -> str:
    """Get IS code reference for common topics"""
    topic_lower = topic.lower()
    
    for key, data in IS_CODE_QUICK_REF.items():
        if key.replace("_", " ") in topic_lower:
            code = data["code"]
            values = data["values"]
            
            answer = f"📖 **{code}**\n\n"
            for item, value in values.items():
                answer += f"• {item}: **{value}**\n"
            
            return answer
    
    return None


def get_defect_solution(defect: str) -> str:
    """Get solution for common defects"""
    defect_lower = defect.lower()
    
    for key, data in COMMON_DEFECTS.items():
        if key in defect_lower:
            return f"""**{key.title()} Defect**

📍 *Cause:* {data['cause']}

🔧 *Solution:* {data['solution']}

✅ *Prevention:* {data['prevention']}
"""
    
    return None


def get_safety_checklist(activity: str) -> str:
    """Get safety checklist for activity"""
    activity_lower = activity.lower()
    
    for key, items in SAFETY_CHECKLIST.items():
        if key in activity_lower:
            checklist = f"**Safety Checklist - {key.title()}**\n\n"
            for item in items:
                checklist += f"☐ {item}\n"
            return checklist
    
    return None

