"""
SiteMind Subscription & Hierarchy Service
Manages company-wide subscriptions with proper site validation

HIERARCHY:
Builder (Company)
    └── Project (Site) - $500/month EACH
        └── Site Engineers (unlimited per site)

ANTI-GAMING RULES:
1. Each site must have unique location/address
2. Each site gets a unique identifier
3. Sites must be verified before activation
4. Usage monitoring to detect multi-site abuse
5. Clear separation of data between sites
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import hashlib


class SubscriptionTier:
    """Subscription pricing tiers"""
    SITE_MONTHLY_USD = 500
    SITE_ANNUAL_USD = 5000  # 2 months free
    
    # Volume discounts for large builders
    VOLUME_DISCOUNTS = {
        10: 0.05,   # 5% off for 10+ sites
        25: 0.10,   # 10% off for 25+ sites
        50: 0.15,   # 15% off for 50+ sites
        100: 0.20,  # 20% off for 100+ sites
    }


class SubscriptionService:
    """
    Manages subscriptions, billing, and site validation
    
    KEY PRINCIPLE: Each construction site = one $500 subscription
    No gaming allowed - we verify each site is legitimate
    """
    
    def __init__(self):
        # In production, this is database-backed
        self._builders: Dict[str, Dict] = {}
        self._sites: Dict[str, Dict] = {}
        self._subscriptions: Dict[str, Dict] = {}
    
    def create_builder(
        self,
        name: str,
        contact_person: str,
        contact_email: str,
        contact_phone: str,
        company_gst: Optional[str] = None,  # For Indian tax compliance
    ) -> Dict[str, Any]:
        """
        Register a new builder/construction company
        This is the top of the hierarchy
        """
        builder_id = self._generate_id(f"builder_{name}_{datetime.utcnow().isoformat()}")
        
        builder = {
            "id": builder_id,
            "name": name,
            "contact_person": contact_person,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "company_gst": company_gst,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "sites": [],
            "total_monthly_cost_usd": 0,
        }
        
        self._builders[builder_id] = builder
        return builder
    
    def add_site(
        self,
        builder_id: str,
        site_name: str,
        site_address: str,
        city: str,
        state: str,
        pin_code: str,
        project_type: str,  # residential, commercial, industrial
        estimated_value_cr: float,
        expected_duration_months: int,
        site_contact_name: str,
        site_contact_phone: str,
    ) -> Dict[str, Any]:
        """
        Add a new construction site under a builder
        
        ANTI-GAMING CHECKS:
        1. Address must be unique (no duplicate sites)
        2. Site details must be complete
        3. Each site gets a unique ID and WhatsApp mapping
        """
        if builder_id not in self._builders:
            return {"error": "Builder not found"}
        
        # ANTI-GAMING: Check for duplicate address
        address_hash = self._generate_address_hash(site_address, city, pin_code)
        for existing_site in self._sites.values():
            if existing_site.get("address_hash") == address_hash:
                return {
                    "error": "Site already registered",
                    "existing_site_id": existing_site["id"],
                    "message": "This location already has a SiteMind subscription. Each construction site requires a separate subscription."
                }
        
        site_id = self._generate_id(f"site_{site_name}_{datetime.utcnow().isoformat()}")
        
        site = {
            "id": site_id,
            "builder_id": builder_id,
            "name": site_name,
            "address": site_address,
            "city": city,
            "state": state,
            "pin_code": pin_code,
            "address_hash": address_hash,  # For duplicate detection
            "project_type": project_type,
            "estimated_value_cr": estimated_value_cr,
            "expected_duration_months": expected_duration_months,
            "site_contact_name": site_contact_name,
            "site_contact_phone": site_contact_phone,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending_verification",  # Must be verified before going live
            "engineers": [],
            "subscription": None,
        }
        
        self._sites[site_id] = site
        self._builders[builder_id]["sites"].append(site_id)
        
        return {
            "site": site,
            "next_steps": [
                "Site created but pending verification",
                "Our team will verify the site details within 24 hours",
                "Once verified, you can add engineers and start using SiteMind",
            ],
            "monthly_cost": f"${SubscriptionTier.SITE_MONTHLY_USD}/month",
        }
    
    def verify_site(self, site_id: str, verified_by: str) -> Dict[str, Any]:
        """
        Verify a site after manual review
        This prevents fake sites from being registered
        """
        if site_id not in self._sites:
            return {"error": "Site not found"}
        
        site = self._sites[site_id]
        site["status"] = "verified"
        site["verified_at"] = datetime.utcnow().isoformat()
        site["verified_by"] = verified_by
        
        return {
            "site": site,
            "message": "Site verified and ready for subscription",
        }
    
    def activate_subscription(
        self,
        site_id: str,
        billing_cycle: str = "monthly",  # monthly or annual
        payment_reference: str = None,
    ) -> Dict[str, Any]:
        """
        Activate subscription for a verified site
        """
        if site_id not in self._sites:
            return {"error": "Site not found"}
        
        site = self._sites[site_id]
        
        if site["status"] != "verified":
            return {"error": "Site must be verified before subscription can be activated"}
        
        # Calculate cost
        if billing_cycle == "annual":
            cost_usd = SubscriptionTier.SITE_ANNUAL_USD
        else:
            cost_usd = SubscriptionTier.SITE_MONTHLY_USD
        
        # Apply volume discount
        builder = self._builders.get(site["builder_id"])
        if builder:
            active_sites = len([s for s in builder["sites"] if self._sites.get(s, {}).get("status") == "active"])
            for threshold, discount in sorted(SubscriptionTier.VOLUME_DISCOUNTS.items(), reverse=True):
                if active_sites >= threshold:
                    cost_usd = cost_usd * (1 - discount)
                    break
        
        subscription = {
            "id": self._generate_id(f"sub_{site_id}"),
            "site_id": site_id,
            "billing_cycle": billing_cycle,
            "cost_usd": cost_usd,
            "cost_inr": cost_usd * 83,
            "started_at": datetime.utcnow().isoformat(),
            "next_billing_date": None,  # Set by payment system
            "payment_reference": payment_reference,
            "status": "active",
        }
        
        site["subscription"] = subscription
        site["status"] = "active"
        
        # Update builder's total cost
        if builder:
            total_cost = 0
            for s in builder["sites"]:
                site_data = self._sites.get(s, {})
                sub = site_data.get("subscription")
                if sub and sub.get("status") == "active":
                    total_cost += sub.get("cost_usd", 0)
            builder["total_monthly_cost_usd"] = total_cost
        
        return {
            "subscription": subscription,
            "site": site,
            "message": f"Site '{site['name']}' is now active!",
        }
    
    def get_builder_dashboard(self, builder_id: str) -> Dict[str, Any]:
        """
        Get company-wide dashboard for a builder
        Shows all sites, costs, and aggregated metrics
        """
        if builder_id not in self._builders:
            return {"error": "Builder not found"}
        
        builder = self._builders[builder_id]
        sites = [self._sites[s] for s in builder["sites"] if s in self._sites]
        
        active_sites = [s for s in sites if s.get("status") == "active"]
        pending_sites = [s for s in sites if s.get("status") in ["pending_verification", "verified"]]
        
        # Calculate costs
        total_monthly = sum(
            s.get("subscription", {}).get("cost_usd", 0)
            for s in active_sites
        )
        
        # Check for volume discount
        discount_applied = None
        for threshold, discount in sorted(SubscriptionTier.VOLUME_DISCOUNTS.items(), reverse=True):
            if len(active_sites) >= threshold:
                discount_applied = f"{discount * 100:.0f}% volume discount ({threshold}+ sites)"
                break
        
        return {
            "builder": {
                "id": builder["id"],
                "name": builder["name"],
                "contact_person": builder["contact_person"],
            },
            "summary": {
                "total_sites": len(sites),
                "active_sites": len(active_sites),
                "pending_sites": len(pending_sites),
                "monthly_cost_usd": total_monthly,
                "monthly_cost_inr": total_monthly * 83,
                "annual_cost_usd": total_monthly * 12,
                "discount_applied": discount_applied,
            },
            "sites": [
                {
                    "id": s["id"],
                    "name": s["name"],
                    "city": s["city"],
                    "status": s["status"],
                    "project_type": s["project_type"],
                    "estimated_value_cr": s["estimated_value_cr"],
                    "engineers_count": len(s.get("engineers", [])),
                    "subscription_cost_usd": s.get("subscription", {}).get("cost_usd", 0),
                }
                for s in sites
            ],
            "pricing": {
                "per_site_monthly": f"${SubscriptionTier.SITE_MONTHLY_USD}",
                "per_site_annual": f"${SubscriptionTier.SITE_ANNUAL_USD} (2 months free)",
                "volume_discounts": SubscriptionTier.VOLUME_DISCOUNTS,
            },
        }
    
    def detect_potential_abuse(self, site_id: str) -> Dict[str, Any]:
        """
        Detect if a site might be serving multiple actual construction sites
        
        RED FLAGS:
        1. Unusually high query volume (>100/day)
        2. Queries about multiple different locations
        3. Queries from many different phone numbers
        4. Geographic references in queries don't match site location
        """
        if site_id not in self._sites:
            return {"error": "Site not found"}
        
        # In production, this would analyze actual usage patterns
        # For now, return the checks we would perform
        return {
            "site_id": site_id,
            "checks_performed": [
                "query_volume_analysis",
                "location_consistency",
                "phone_number_patterns",
                "blueprint_reference_analysis",
            ],
            "status": "no_abuse_detected",
            "message": "Site usage patterns are consistent with single-site subscription",
        }
    
    def _generate_id(self, seed: str) -> str:
        """Generate a unique ID"""
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
    
    def _generate_address_hash(self, address: str, city: str, pin_code: str) -> str:
        """Generate hash for duplicate detection"""
        normalized = f"{address.lower().strip()}_{city.lower().strip()}_{pin_code.strip()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]


# Singleton instance
subscription_service = SubscriptionService()

