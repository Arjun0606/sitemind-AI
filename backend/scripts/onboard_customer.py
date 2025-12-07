#!/usr/bin/env python3
"""
SiteMind Customer Onboarding CLI
Run this during customer calls for seamless setup

Usage:
    python onboard_customer.py

This will walk you through setting up a new customer interactively.
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, '..')

from services.onboarding_service import onboarding_service
from services.config_service import config_service


# =============================================================================
# TEMPLATES FOR COMMON CUSTOMER TYPES
# =============================================================================

CUSTOMER_TEMPLATES = {
    "small_builder": {
        "name": "Small Builder (1-3 sites)",
        "description": "Simple setup, all features enabled",
        "config": {
            "features": {
                "red_flags": True,
                "task_management": True,
                "material_tracking": True,
                "progress_photos": True,
                "office_site_sync": True,
                "integrations": False,
                "advanced_analytics": False,
            },
            "notifications": {
                "morning_brief": True,
                "red_flags": True,
            }
        }
    },
    "medium_builder": {
        "name": "Medium Builder (5-15 sites)",
        "description": "Full features + Drive integration",
        "config": {
            "features": {
                "red_flags": True,
                "task_management": True,
                "material_tracking": True,
                "progress_photos": True,
                "office_site_sync": True,
                "integrations": True,
                "advanced_analytics": True,
            },
            "notifications": {
                "morning_brief": True,
                "red_flags": True,
                "weekly_reports": True,
            }
        }
    },
    "large_developer": {
        "name": "Large Developer (20+ sites)",
        "description": "Enterprise features + ERP integration",
        "config": {
            "features": {
                "red_flags": True,
                "task_management": True,
                "material_tracking": True,
                "progress_photos": True,
                "office_site_sync": True,
                "integrations": True,
                "advanced_analytics": True,
                "custom_reports": True,
                "api_access": True,
            }
        }
    },
    "consultant": {
        "name": "Consultant/Architect",
        "description": "Limited access to specific projects",
        "config": {
            "features": {
                "red_flags": False,
                "task_management": False,
                "material_tracking": False,
                "progress_photos": False,
                "office_site_sync": True,
                "integrations": True,
            }
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step_num: int, text: str):
    """Print a step indicator"""
    print(f"\n📌 STEP {step_num}: {text}")
    print("-" * 40)


def get_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with optional default"""
    if default:
        display = f"{prompt} [{default}]: "
    else:
        display = f"{prompt}: "
    
    value = input(display).strip()
    
    if not value and default:
        return default
    
    if not value and required:
        print("  ⚠️  This field is required.")
        return get_input(prompt, default, required)
    
    return value


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input"""
    default_str = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not value:
        return default
    
    return value in ['y', 'yes', 'true', '1']


def get_phone(prompt: str) -> str:
    """Get and validate phone number"""
    phone = get_input(prompt)
    
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    # Add country code if missing
    if not phone.startswith("+"):
        if phone.startswith("91"):
            phone = f"+{phone}"
        else:
            phone = f"+91{phone}"
    
    return phone


def select_from_list(prompt: str, options: List[str], allow_multiple: bool = False) -> List[int]:
    """Let user select from a list"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    
    if allow_multiple:
        print("\n  (Enter numbers separated by commas, e.g., 1,3,4)")
    
    selection = input("\nYour choice: ").strip()
    
    if allow_multiple:
        indices = [int(x.strip()) - 1 for x in selection.split(",")]
        return indices
    else:
        return [int(selection) - 1]


# =============================================================================
# MAIN ONBOARDING FLOW
# =============================================================================

def run_onboarding():
    """Main onboarding flow"""
    
    print_header("🏗️  SITEMIND CUSTOMER ONBOARDING")
    print("\nThis wizard will help you set up a new customer.")
    print("Have the customer on call? Great! Let's go.\n")
    
    # -------------------------------------------------------------------------
    # STEP 1: Customer Type
    # -------------------------------------------------------------------------
    print_step(1, "SELECT CUSTOMER TYPE")
    
    template_keys = list(CUSTOMER_TEMPLATES.keys())
    template_names = [f"{CUSTOMER_TEMPLATES[k]['name']} - {CUSTOMER_TEMPLATES[k]['description']}" 
                     for k in template_keys]
    
    selected = select_from_list("What type of customer is this?", template_names)[0]
    customer_type = template_keys[selected]
    template = CUSTOMER_TEMPLATES[customer_type]
    
    print(f"\n  ✅ Selected: {template['name']}")
    
    # -------------------------------------------------------------------------
    # STEP 2: Company Details
    # -------------------------------------------------------------------------
    print_step(2, "COMPANY DETAILS")
    
    company_name = get_input("Company name")
    
    # -------------------------------------------------------------------------
    # STEP 3: Admin User
    # -------------------------------------------------------------------------
    print_step(3, "ADMIN/OWNER DETAILS")
    print("  (This person will have full access)")
    
    admin_name = get_input("Admin name")
    admin_email = get_input("Admin email")
    admin_phone = get_phone("Admin phone")
    
    # -------------------------------------------------------------------------
    # STEP 4: Sites
    # -------------------------------------------------------------------------
    print_step(4, "SITES/PROJECTS")
    
    num_sites = int(get_input("How many sites to set up now?", "1"))
    
    sites = []
    for i in range(num_sites):
        print(f"\n  📍 Site {i+1}:")
        site = {
            "name": get_input("    Site name"),
            "address": get_input("    Address", required=False),
            "city": get_input("    City", required=False),
            "team": []
        }
        
        # Team members for this site
        add_team = get_yes_no("    Add team members now?", True)
        if add_team:
            while True:
                print(f"\n    👤 Team member:")
                member = {
                    "name": get_input("      Name"),
                    "phone": get_phone("      Phone"),
                }
                
                # Role selection
                roles = ["site_engineer", "pm", "consultant", "viewer"]
                role_idx = select_from_list("      Role:", roles)[0]
                member["role"] = roles[role_idx]
                
                site["team"].append(member)
                
                if not get_yes_no("    Add another team member?", False):
                    break
        
        sites.append(site)
    
    # -------------------------------------------------------------------------
    # STEP 5: Customization
    # -------------------------------------------------------------------------
    print_step(5, "CUSTOMIZATION")
    
    # Language
    languages = ["English", "Hindi", "Hinglish (recommended)"]
    lang_codes = ["en", "hi", "hinglish"]
    lang_idx = select_from_list("Preferred language for responses:", languages)[0]
    language = lang_codes[lang_idx]
    
    # Morning brief time
    brief_time = get_input("Morning brief time (24hr format)", "07:00")
    
    # Custom assistant name
    assistant_name = get_input("Assistant name (what should AI call itself?)", "SiteMind")
    
    # -------------------------------------------------------------------------
    # STEP 6: Confirm & Create
    # -------------------------------------------------------------------------
    print_step(6, "CONFIRM & CREATE")
    
    print(f"""
    📋 SUMMARY
    ──────────────────────────────────
    Company:        {company_name}
    Customer Type:  {template['name']}
    Admin:          {admin_name} ({admin_phone})
    Sites:          {len(sites)}
    Language:       {language}
    Morning Brief:  {brief_time}
    Assistant:      {assistant_name}
    """)
    
    for i, site in enumerate(sites, 1):
        print(f"    Site {i}: {site['name']}")
        print(f"            {len(site['team'])} team members")
    
    if not get_yes_no("\n    Proceed with setup?", True):
        print("\n    ❌ Setup cancelled.")
        return
    
    # -------------------------------------------------------------------------
    # EXECUTE SETUP
    # -------------------------------------------------------------------------
    print("\n    ⏳ Creating accounts...")
    
    # Build config
    org_config = {
        **template["config"],
        "language": language,
        "morning_brief_time": brief_time,
        "branding": {
            "assistant_name": assistant_name,
        }
    }
    
    # Create via quick setup
    try:
        result = onboarding_service.quick_setup(
            company_name=company_name,
            admin_name=admin_name,
            admin_email=admin_email,
            admin_phone=admin_phone,
            sites=sites,
            plan="pilot",
        )
        
        # Apply org config
        org_id = result.get("organization", {}).get("id")
        if org_id:
            config_service.set_organization_config(org_id, org_config)
        
        print("\n    ✅ SETUP COMPLETE!")
        print(f"""
    ──────────────────────────────────
    Organization ID:  {result.get('organization', {}).get('id')}
    Projects Created: {result.get('projects_created')}
    Users Added:      {result.get('users_added')}
    ──────────────────────────────────
        """)
        
        # Show welcome messages
        print("\n    📱 WELCOME MESSAGES TO SEND:")
        print("    " + "─" * 40)
        
        for msg in result.get("welcome_messages", []):
            print(f"\n    To: {msg['name']} ({msg['phone']})")
            print("    " + "─" * 30)
            # Show first few lines of message
            lines = msg["message"].split("\n")[:5]
            for line in lines:
                print(f"    {line}")
            print("    ...")
        
        # -------------------------------------------------------------------------
        # POST-SETUP CHECKLIST
        # -------------------------------------------------------------------------
        print_header("📋 POST-SETUP CHECKLIST")
        print("""
    Now do these:
    
    [ ] 1. Send welcome messages via WhatsApp
           (Copy from above or use dashboard)
    
    [ ] 2. Ask customer to share drawings
           - Drive link: You'll sync it
           - Forward on WhatsApp: Works directly
    
    [ ] 3. Demo first query
           "Ask any question about the project!"
           Example: "Beam size B3 floor 2?"
    
    [ ] 4. Schedule Day 3 check-in
           "I'll call in 3 days to see how it's going"
    
    [ ] 5. Add to customer tracker
           Company: {company_name}
           Date: {date}
           Sites: {sites}
           Admin: {admin}
        """.format(
            company_name=company_name,
            date=datetime.now().strftime("%Y-%m-%d"),
            sites=len(sites),
            admin=admin_name
        ))
        
        # Save setup details
        save_details = get_yes_no("\n    Save setup details to file?", True)
        if save_details:
            filename = f"onboarding_{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    "company": company_name,
                    "admin": {"name": admin_name, "email": admin_email, "phone": admin_phone},
                    "sites": sites,
                    "config": org_config,
                    "result": result,
                    "created_at": datetime.now().isoformat(),
                }, f, indent=2)
            print(f"\n    💾 Saved to: {filename}")
        
    except Exception as e:
        print(f"\n    ❌ Error: {e}")
        raise


# =============================================================================
# QUICK ADD FUNCTIONS (For existing customers)
# =============================================================================

def add_site():
    """Add a new site to existing customer"""
    print_header("➕ ADD NEW SITE")
    
    # Would look up org by name/ID
    org_id = get_input("Organization ID (or type company name to search)")
    
    print("\n  📍 New Site Details:")
    site_name = get_input("    Site name")
    site_address = get_input("    Address", required=False)
    site_city = get_input("    City", required=False)
    
    # Create project
    # Would call API here
    
    print(f"\n  ✅ Site '{site_name}' added!")


def add_user():
    """Add a new user to existing project"""
    print_header("➕ ADD NEW USER")
    
    project_id = get_input("Project ID")
    
    print("\n  👤 New User Details:")
    name = get_input("    Name")
    phone = get_phone("    Phone")
    
    roles = ["site_engineer", "pm", "consultant", "viewer"]
    role_idx = select_from_list("    Role:", roles)[0]
    role = roles[role_idx]
    
    # Would call API here
    
    print(f"\n  ✅ User '{name}' added as {role}!")


def modify_permissions():
    """Modify user permissions"""
    print_header("🔐 MODIFY PERMISSIONS")
    
    user_id = get_input("User ID (or phone to search)")
    
    print("\n  Current permissions will be shown here...")
    
    # Would show current and allow modifications


# =============================================================================
# MAIN MENU
# =============================================================================

def main():
    """Main menu"""
    print_header("🏗️  SITEMIND ADMIN TOOLS")
    
    options = [
        "New Customer Onboarding",
        "Add Site to Existing Customer",
        "Add User to Project",
        "Modify User Permissions",
        "View Customer Details",
        "Exit"
    ]
    
    while True:
        print("\n")
        selected = select_from_list("What would you like to do?", options)[0]
        
        if selected == 0:
            run_onboarding()
        elif selected == 1:
            add_site()
        elif selected == 2:
            add_user()
        elif selected == 3:
            modify_permissions()
        elif selected == 4:
            print("\n  Would show customer details...")
        elif selected == 5:
            print("\n  👋 Goodbye!")
            break


if __name__ == "__main__":
    main()

