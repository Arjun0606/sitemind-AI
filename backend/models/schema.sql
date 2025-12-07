-- SiteMind Production Database Schema
-- Multi-tenant, audit-ready, enterprise-grade

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ORGANIZATIONS (Multi-tenant root)
-- ============================================================================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    
    -- Billing
    plan VARCHAR(50) DEFAULT 'pilot', -- pilot, standard, enterprise
    billing_email VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    subscription_status VARCHAR(50) DEFAULT 'active',
    
    -- Limits
    max_sites INTEGER DEFAULT 3,
    max_users_per_site INTEGER DEFAULT 50,
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- ============================================================================
-- USERS
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    
    -- Identity
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    phone_verified BOOLEAN DEFAULT FALSE,
    name VARCHAR(255) NOT NULL,
    
    -- Role: owner, admin, pm, site_engineer, consultant, viewer
    role VARCHAR(50) DEFAULT 'site_engineer',
    
    -- Auth (managed by Supabase Auth)
    supabase_user_id UUID UNIQUE,
    
    -- Preferences
    language VARCHAR(10) DEFAULT 'en', -- en, hi, hinglish
    notification_preferences JSONB DEFAULT '{"morning_brief": true, "alerts": true}',
    
    -- Activity
    last_active_at TIMESTAMPTZ,
    total_queries INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- ============================================================================
-- PROJECTS (Sites)
-- ============================================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50), -- e.g., "SKY-001"
    description TEXT,
    address TEXT,
    city VARCHAR(100),
    
    -- Project Details
    project_type VARCHAR(50), -- residential, commercial, mixed, infrastructure
    total_area_sqft INTEGER,
    estimated_cost DECIMAL(15, 2),
    start_date DATE,
    expected_completion DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, on_hold, completed, archived
    progress_percent INTEGER DEFAULT 0,
    
    -- SiteMind specific
    sitemind_phone VARCHAR(20), -- Dedicated WhatsApp number for this project
    onboarding_completed BOOLEAN DEFAULT FALSE,
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- ============================================================================
-- PROJECT MEMBERS (User-Project relationship)
-- ============================================================================
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Role in this project
    project_role VARCHAR(50) DEFAULT 'site_engineer', -- pm, site_engineer, consultant, viewer
    
    -- Access
    can_upload_drawings BOOLEAN DEFAULT FALSE,
    can_manage_tasks BOOLEAN DEFAULT FALSE,
    can_view_reports BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    removed_at TIMESTAMPTZ,
    
    UNIQUE(project_id, user_id)
);

-- ============================================================================
-- DOCUMENTS (Drawings, PDFs, etc.)
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- File Info
    name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- drawing, specification, rfi, change_order, photo, other
    mime_type VARCHAR(100),
    file_size INTEGER,
    storage_path VARCHAR(500) NOT NULL, -- Supabase storage path
    
    -- Version Control
    version INTEGER DEFAULT 1,
    revision VARCHAR(20), -- e.g., "Rev 2", "A"
    parent_document_id UUID REFERENCES documents(id), -- Previous version
    is_latest BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    drawing_number VARCHAR(100),
    sheet_name VARCHAR(255),
    discipline VARCHAR(50), -- structural, architectural, mep, electrical, plumbing
    floor VARCHAR(50),
    
    -- AI Processing
    ai_analyzed BOOLEAN DEFAULT FALSE,
    ai_analysis JSONB, -- Extracted specs, dimensions, etc.
    embedding_id VARCHAR(255), -- Supermemory reference
    
    -- Source
    uploaded_by UUID REFERENCES users(id),
    source VARCHAR(50), -- whatsapp, dashboard, drive_sync, email
    source_reference VARCHAR(255), -- Original message ID, email ID, etc.
    
    -- Timestamps
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- ============================================================================
-- MEMORIES (All project knowledge)
-- ============================================================================
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Content
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- query, decision, change_order, rfi, meeting_note, instruction
    
    -- Structured Data
    metadata JSONB DEFAULT '{}',
    -- For decisions: {decision, reason, approved_by, affected_area}
    -- For change_orders: {old_value, new_value, reason, reference}
    -- For queries: {question, answer, confidence}
    
    -- References
    related_document_id UUID REFERENCES documents(id),
    related_memory_ids UUID[], -- Links to related memories
    
    -- Source
    source VARCHAR(50) NOT NULL, -- whatsapp, dashboard, email, meeting
    source_user_id UUID REFERENCES users(id),
    source_reference VARCHAR(255),
    
    -- AI
    embedding_id VARCHAR(255), -- Supermemory reference
    importance_score FLOAT DEFAULT 0.5, -- For prioritizing search results
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CONVERSATIONS (WhatsApp threads)
-- ============================================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- WhatsApp
    whatsapp_phone VARCHAR(20) NOT NULL,
    
    -- Context (for follow-up questions)
    context JSONB DEFAULT '{}',
    last_query TEXT,
    last_response TEXT,
    
    -- Stats
    total_messages INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MESSAGES (Individual messages)
-- ============================================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    
    -- Content
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    message_type VARCHAR(50) NOT NULL, -- text, image, document, audio, location
    content TEXT,
    media_url VARCHAR(500),
    media_analyzed BOOLEAN DEFAULT FALSE,
    
    -- AI Processing
    intent_detected VARCHAR(100), -- query, upload, progress_update, task_update, etc.
    entities_extracted JSONB, -- {location: "B3", floor: "3", element: "beam"}
    response_generated TEXT,
    response_sources JSONB, -- [{document_id, memory_id, confidence}]
    
    -- WhatsApp
    whatsapp_message_id VARCHAR(255),
    whatsapp_status VARCHAR(50), -- sent, delivered, read
    
    -- Processing
    processing_time_ms INTEGER,
    model_used VARCHAR(50),
    tokens_used INTEGER,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- ============================================================================
-- RED FLAGS
-- ============================================================================
CREATE TABLE red_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Flag Details
    category VARCHAR(50) NOT NULL, -- safety, conflict, confusion, timeline, compliance
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    affected_area VARCHAR(255),
    
    -- Evidence
    evidence JSONB DEFAULT '[]', -- [{type, reference, content}]
    related_message_ids UUID[],
    related_document_ids UUID[],
    
    -- Recommended Action
    recommended_action TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, acknowledged, resolved, false_positive
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    -- Timestamps
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- TASKS
-- ============================================================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Task Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    
    -- Assignment
    assigned_to UUID[] NOT NULL, -- Array of user IDs
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Schedule
    due_date DATE,
    due_time TIME,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, blocked, completed, verified
    priority VARCHAR(20) DEFAULT 'normal', -- critical, high, normal, low
    
    -- Progress
    checklist JSONB DEFAULT '[]', -- [{item, completed, completed_by, completed_at}]
    completion_notes TEXT,
    completion_photos UUID[], -- References to documents
    
    -- Blocker
    blocker TEXT,
    blocker_reported_by UUID REFERENCES users(id),
    blocker_reported_at TIMESTAMPTZ,
    
    -- Verification
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MILESTONES (Progress tracking)
-- ============================================================================
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Details
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    stage VARCHAR(50) NOT NULL, -- excavation, foundation, structure, finishing, etc.
    
    -- Schedule
    planned_start DATE,
    planned_end DATE,
    actual_start DATE,
    actual_end DATE,
    
    -- Progress
    progress_percent INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, completed, delayed, verified
    
    -- Photos
    progress_photos JSONB DEFAULT '[]', -- [{document_id, date, notes, ai_analysis}]
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MATERIALS
-- ============================================================================
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Material Info
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- cement, steel, aggregate, etc.
    unit VARCHAR(50) NOT NULL, -- bags, MT, pieces, sqft
    
    -- Stock
    current_stock DECIMAL(10, 2) DEFAULT 0,
    minimum_stock DECIMAL(10, 2) DEFAULT 0,
    
    -- Cost
    rate DECIMAL(10, 2) DEFAULT 0, -- Cost per unit
    
    -- Location
    storage_location VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MATERIAL TRANSACTIONS
-- ============================================================================
CREATE TABLE material_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    material_id UUID NOT NULL REFERENCES materials(id),
    
    -- Transaction
    transaction_type VARCHAR(50) NOT NULL, -- received, consumed, returned, wastage, adjustment
    quantity DECIMAL(10, 2) NOT NULL,
    
    -- Details
    location VARCHAR(255), -- Where used/stored
    reference VARCHAR(255), -- PO number, challan, etc.
    notes TEXT,
    
    -- Source
    recorded_by UUID NOT NULL REFERENCES users(id),
    
    -- Timestamps
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SYNC ITEMS (Office-Site communication)
-- ============================================================================
CREATE TABLE sync_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Content
    item_type VARCHAR(50) NOT NULL, -- drawing, change_order, rfi, decision, instruction
    title VARCHAR(255) NOT NULL,
    content TEXT,
    
    -- Source
    source VARCHAR(20) NOT NULL, -- office, site
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Distribution
    target_recipients UUID[] NOT NULL, -- User IDs
    acknowledgments JSONB DEFAULT '{}', -- {user_id: {status, timestamp}}
    
    -- Attachments
    attachment_ids UUID[], -- Document IDs
    
    -- Priority
    priority VARCHAR(20) DEFAULT 'normal', -- urgent, high, normal
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INTEGRATIONS (External system connections)
-- ============================================================================
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    -- Integration Type
    integration_type VARCHAR(50) NOT NULL, -- google_drive, onedrive, sap, primavera, etc.
    name VARCHAR(255) NOT NULL,
    
    -- Connection
    credentials JSONB, -- Encrypted OAuth tokens, API keys
    settings JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, paused, error
    last_sync_at TIMESTAMPTZ,
    last_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- REPORTS (Generated reports)
-- ============================================================================
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    organization_id UUID REFERENCES organizations(id),
    
    -- Report Details
    report_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, custom
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL, -- Markdown or HTML
    
    -- Data
    data JSONB, -- Structured data used in report
    
    -- Distribution
    sent_to UUID[], -- User IDs
    sent_via VARCHAR(20)[], -- whatsapp, email, dashboard
    
    -- Timestamps
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ
);

-- ============================================================================
-- AUDIT LOG (Everything that happens)
-- ============================================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What
    action VARCHAR(100) NOT NULL, -- document.uploaded, decision.made, task.completed, etc.
    entity_type VARCHAR(50) NOT NULL, -- document, memory, task, etc.
    entity_id UUID NOT NULL,
    
    -- Context
    organization_id UUID REFERENCES organizations(id),
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    
    -- Details
    old_value JSONB,
    new_value JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- Source
    source VARCHAR(50), -- whatsapp, dashboard, api, system
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- BILLING (Usage tracking for invoicing)
-- ============================================================================
CREATE TABLE billing_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    project_id UUID REFERENCES projects(id),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Usage
    queries_count INTEGER DEFAULT 0,
    documents_uploaded INTEGER DEFAULT 0,
    storage_bytes BIGINT DEFAULT 0,
    ai_tokens_used INTEGER DEFAULT 0,
    
    -- Value
    issues_caught INTEGER DEFAULT 0,
    estimated_value_saved DECIMAL(15, 2) DEFAULT 0,
    
    -- Timestamps
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Organizations
CREATE INDEX idx_organizations_slug ON organizations(slug);

-- Users
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);

-- Projects
CREATE INDEX idx_projects_org ON projects(organization_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Project Members
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);

-- Documents
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_documents_type ON documents(file_type);
CREATE INDEX idx_documents_discipline ON documents(discipline);

-- Memories
CREATE INDEX idx_memories_project ON memories(project_id);
CREATE INDEX idx_memories_type ON memories(content_type);
CREATE INDEX idx_memories_created ON memories(created_at DESC);

-- Conversations
CREATE INDEX idx_conversations_project ON conversations(project_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_phone ON conversations(whatsapp_phone);

-- Messages
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_project ON messages(project_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);

-- Red Flags
CREATE INDEX idx_red_flags_project ON red_flags(project_id);
CREATE INDEX idx_red_flags_status ON red_flags(status);
CREATE INDEX idx_red_flags_severity ON red_flags(severity);

-- Tasks
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due ON tasks(due_date);

-- Milestones
CREATE INDEX idx_milestones_project ON milestones(project_id);
CREATE INDEX idx_milestones_status ON milestones(status);

-- Materials
CREATE INDEX idx_materials_project ON materials(project_id);

-- Audit Log
CREATE INDEX idx_audit_log_org ON audit_log(organization_id);
CREATE INDEX idx_audit_log_project ON audit_log(project_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);

-- ============================================================================
-- TRIGGERS (Auto-update timestamps)
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_red_flags_updated_at BEFORE UPDATE ON red_flags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_milestones_updated_at BEFORE UPDATE ON milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- ROW LEVEL SECURITY (Multi-tenant isolation)
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE red_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_usage ENABLE ROW LEVEL SECURITY;

-- Policies will be created based on Supabase Auth JWT claims
-- Example policy structure (implement after Supabase setup):

-- CREATE POLICY "Users can view own organization" ON organizations
--     FOR SELECT USING (id = auth.jwt() -> 'user_metadata' ->> 'organization_id');

-- CREATE POLICY "Users can view projects in their organization" ON projects
--     FOR SELECT USING (organization_id = auth.jwt() -> 'user_metadata' ->> 'organization_id');

