-- ============================================================================
-- SITEMIND DATABASE SCHEMA (Supabase/PostgreSQL)
-- ============================================================================
-- 
-- Run this in your Supabase SQL editor to set up the database
--
-- Tables:
-- - companies: Customer companies
-- - projects: Construction projects
-- - users: Team members
-- - queries: WhatsApp queries (for billing)
-- - documents: Uploaded documents
-- - photos: Uploaded photos
-- - invoices: Billing invoices
-- - usage: Usage tracking for billing
--
-- ============================================================================


-- ============================================================================
-- COMPANIES
-- ============================================================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    gstin TEXT,
    address TEXT,
    
    -- Billing
    plan TEXT DEFAULT 'enterprise',
    flat_fee_usd NUMERIC(10,2) DEFAULT 500.00,
    is_pilot BOOLEAN DEFAULT FALSE,
    is_founding BOOLEAN DEFAULT FALSE,
    billing_email TEXT,
    
    -- Stripe/Razorpay
    stripe_customer_id TEXT,
    razorpay_customer_id TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Settings
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_companies_name ON companies(name);


-- ============================================================================
-- PROJECTS
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    location TEXT,
    project_type TEXT DEFAULT 'residential', -- residential, commercial, mixed, infrastructure
    
    stage TEXT DEFAULT 'active', -- planning, active, finishing, handover, archived
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ,
    
    -- Settings
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_projects_company ON projects(company_id);
CREATE INDEX idx_projects_stage ON projects(stage);


-- ============================================================================
-- USERS
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,  -- WhatsApp number (primary identifier)
    email TEXT,
    
    role TEXT DEFAULT 'site_engineer', -- owner, admin, pm, site_engineer, consultant, viewer
    
    -- Auth (for dashboard)
    password_hash TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,
    
    -- Settings
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_company ON users(company_id);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);


-- ============================================================================
-- PROJECT MEMBERS (many-to-many)
-- ============================================================================

CREATE TABLE project_members (
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member', -- member, lead, viewer
    added_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (project_id, user_id)
);


-- ============================================================================
-- QUERIES (for billing and analytics)
-- ============================================================================

CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Content
    question TEXT NOT NULL,
    answer TEXT,
    
    -- Classification
    query_type TEXT, -- structural, architectural, material, safety, etc.
    
    -- Billing
    billed BOOLEAN DEFAULT FALSE,
    billing_cycle TEXT, -- YYYY-MM
    
    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    response_time_ms INTEGER
);

CREATE INDEX idx_queries_company ON queries(company_id);
CREATE INDEX idx_queries_project ON queries(project_id);
CREATE INDEX idx_queries_billing_cycle ON queries(billing_cycle);
CREATE INDEX idx_queries_billed ON queries(billed);
CREATE INDEX idx_queries_created ON queries(created_at);


-- ============================================================================
-- DOCUMENTS
-- ============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- File info
    name TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Supabase storage path
    file_type TEXT, -- pdf, dwg, image
    file_size_bytes BIGINT,
    
    -- Extracted content
    extracted_text TEXT,
    
    -- Billing
    billed BOOLEAN DEFAULT FALSE,
    billing_cycle TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_company ON documents(company_id);
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_billed ON documents(billed);


-- ============================================================================
-- PHOTOS
-- ============================================================================

CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- File info
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    
    -- Analysis
    caption TEXT,
    analysis TEXT, -- AI analysis result
    photo_type TEXT, -- progress, issue, verification
    location TEXT, -- grid/floor reference
    
    -- Billing
    billed BOOLEAN DEFAULT FALSE,
    billing_cycle TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_photos_company ON photos(company_id);
CREATE INDEX idx_photos_project ON photos(project_id);
CREATE INDEX idx_photos_billed ON photos(billed);


-- ============================================================================
-- USAGE (monthly aggregates for billing)
-- ============================================================================

CREATE TABLE usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Billing period
    billing_cycle TEXT NOT NULL, -- YYYY-MM
    cycle_start DATE NOT NULL,
    cycle_end DATE NOT NULL,
    
    -- Usage counts
    queries_count INTEGER DEFAULT 0,
    documents_count INTEGER DEFAULT 0,
    photos_count INTEGER DEFAULT 0,
    storage_gb NUMERIC(10,2) DEFAULT 0,
    
    -- Included limits (from plan)
    queries_included INTEGER DEFAULT 500,
    documents_included INTEGER DEFAULT 20,
    photos_included INTEGER DEFAULT 100,
    storage_included_gb NUMERIC(10,2) DEFAULT 10,
    
    -- Overages
    queries_overage INTEGER DEFAULT 0,
    documents_overage INTEGER DEFAULT 0,
    photos_overage INTEGER DEFAULT 0,
    storage_overage_gb NUMERIC(10,2) DEFAULT 0,
    
    -- Charges
    flat_fee_usd NUMERIC(10,2) DEFAULT 500,
    usage_charges_usd NUMERIC(10,2) DEFAULT 0,
    total_usd NUMERIC(10,2) DEFAULT 500,
    
    -- Status
    status TEXT DEFAULT 'active', -- active, closed, billed
    billed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, billing_cycle)
);

CREATE INDEX idx_usage_company ON usage(company_id);
CREATE INDEX idx_usage_cycle ON usage(billing_cycle);
CREATE INDEX idx_usage_status ON usage(status);


-- ============================================================================
-- INVOICES
-- ============================================================================

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    usage_id UUID REFERENCES usage(id) ON DELETE SET NULL,
    
    -- Invoice details
    invoice_number TEXT NOT NULL UNIQUE,
    billing_cycle TEXT NOT NULL,
    
    -- Amounts
    flat_fee_usd NUMERIC(10,2),
    usage_charges_usd NUMERIC(10,2),
    discount_usd NUMERIC(10,2) DEFAULT 0,
    total_usd NUMERIC(10,2),
    total_inr NUMERIC(12,2),
    
    -- Status
    status TEXT DEFAULT 'pending', -- pending, paid, overdue, cancelled
    
    -- Payment
    payment_method TEXT,
    payment_id TEXT, -- Stripe/Razorpay payment ID
    paid_at TIMESTAMPTZ,
    
    -- Dates
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    due_at TIMESTAMPTZ,
    
    -- Full breakdown
    breakdown JSONB
);

CREATE INDEX idx_invoices_company ON invoices(company_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_cycle ON invoices(billing_cycle);


-- ============================================================================
-- AUDIT LOG
-- ============================================================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action
    action TEXT NOT NULL, -- decision, change_order, query, upload, etc.
    description TEXT,
    
    -- Data
    old_value JSONB,
    new_value JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT
);

CREATE INDEX idx_audit_company ON audit_log(company_id);
CREATE INDEX idx_audit_project ON audit_log(project_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at);


-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Policies will be added based on auth setup
-- For now, service role has full access


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers
CREATE TRIGGER companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER usage_updated_at
    BEFORE UPDATE ON usage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================================
-- STORAGE BUCKETS (run in Supabase dashboard)
-- ============================================================================

-- Create these buckets in Supabase Storage:
-- 1. documents - for PDFs and drawings
-- 2. photos - for site photos
-- 3. exports - for generated reports


-- ============================================================================
-- SEED DATA (optional)
-- ============================================================================

-- Insert pilot company for testing
-- INSERT INTO companies (name, is_pilot, is_founding)
-- VALUES ('Test Developer', TRUE, TRUE);

