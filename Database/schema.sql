-- ==========================================
-- AITasker Database Schema
-- PostgreSQL 17
-- ==========================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- USERS
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    phone VARCHAR(20),
    avatar_url TEXT,

    role VARCHAR(20) NOT NULL
    CHECK (role IN ('ADMIN', 'ENTERPRISE', 'EXPERT')),

    status VARCHAR(20) DEFAULT 'ACTIVE'
    CHECK (status IN ('ACTIVE', 'INACTIVE', 'BANNED')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- ENTERPRISES
-- ==========================================

CREATE TABLE enterprises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID UNIQUE NOT NULL,

    company_name VARCHAR(255) NOT NULL,
    address TEXT,
    website VARCHAR(255),
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_enterprise_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- ==========================================
-- EXPERTS
-- ==========================================

CREATE TABLE experts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID UNIQUE NOT NULL,

    title VARCHAR(255),
    bio TEXT,

    experience_years INT DEFAULT 0,

    hourly_rate DECIMAL(12,2) DEFAULT 0,

    rating DECIMAL(3,2) DEFAULT 0,

    completed_projects INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_expert_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- ==========================================
-- SKILLS
-- ==========================================

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    skill_name VARCHAR(100) UNIQUE NOT NULL
);

-- ==========================================
-- EXPERT SKILLS
-- ==========================================

CREATE TABLE expert_skills (
    expert_id UUID NOT NULL,
    skill_id UUID NOT NULL,

    PRIMARY KEY (expert_id, skill_id),

    CONSTRAINT fk_expert_skill_expert
    FOREIGN KEY (expert_id)
    REFERENCES experts(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_expert_skill_skill
    FOREIGN KEY (skill_id)
    REFERENCES skills(id)
    ON DELETE CASCADE
);

-- ==========================================
-- CATEGORIES
-- ==========================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- ==========================================
-- PROJECTS
-- ==========================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    enterprise_id UUID NOT NULL,

    category_id UUID,

    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    budget DECIMAL(12,2),

    deadline DATE,

    status VARCHAR(30) DEFAULT 'OPEN'
    CHECK (
        status IN (
            'OPEN',
            'IN_PROGRESS',
            'COMPLETED',
            'CANCELLED'
        )
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_project_enterprise
    FOREIGN KEY (enterprise_id)
    REFERENCES enterprises(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_project_category
    FOREIGN KEY (category_id)
    REFERENCES categories(id)
    ON DELETE SET NULL
);

-- ==========================================
-- PROJECT FILES
-- ==========================================

CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    project_id UUID NOT NULL,

    file_name VARCHAR(255) NOT NULL,

    file_url TEXT NOT NULL,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_project_file
    FOREIGN KEY (project_id)
    REFERENCES projects(id)
    ON DELETE CASCADE
);

-- ==========================================
-- PROPOSALS
-- ==========================================

CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    project_id UUID NOT NULL,

    expert_id UUID NOT NULL,

    price DECIMAL(12,2) NOT NULL,

    duration_days INT,

    cover_letter TEXT,

    status VARCHAR(30) DEFAULT 'PENDING'
    CHECK (
        status IN (
            'PENDING',
            'ACCEPTED',
            'REJECTED',
            'WITHDRAWN'
        )
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_proposal_project
    FOREIGN KEY (project_id)
    REFERENCES projects(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_proposal_expert
    FOREIGN KEY (expert_id)
    REFERENCES experts(id)
    ON DELETE CASCADE
);

-- ==========================================
-- CONTRACTS
-- ==========================================

CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    project_id UUID UNIQUE NOT NULL,

    enterprise_id UUID NOT NULL,

    expert_id UUID NOT NULL,

    start_date DATE,

    end_date DATE,

    contract_value DECIMAL(12,2),

    status VARCHAR(30) DEFAULT 'ACTIVE'
    CHECK (
        status IN (
            'ACTIVE',
            'COMPLETED',
            'TERMINATED'
        )
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_contract_project
    FOREIGN KEY (project_id)
    REFERENCES projects(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_contract_enterprise
    FOREIGN KEY (enterprise_id)
    REFERENCES enterprises(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_contract_expert
    FOREIGN KEY (expert_id)
    REFERENCES experts(id)
    ON DELETE CASCADE
);

-- ==========================================
-- MILESTONES
-- ==========================================

CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    contract_id UUID NOT NULL,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    amount DECIMAL(12,2),

    due_date DATE,

    status VARCHAR(30) DEFAULT 'PENDING'
    CHECK (
        status IN (
            'PENDING',
            'IN_PROGRESS',
            'DONE'
        )
    ),

    CONSTRAINT fk_milestone_contract
    FOREIGN KEY (contract_id)
    REFERENCES contracts(id)
    ON DELETE CASCADE
);

-- ==========================================
-- PAYMENTS
-- ==========================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    contract_id UUID NOT NULL,

    amount DECIMAL(12,2) NOT NULL,

    payment_method VARCHAR(100),

    transaction_code VARCHAR(255),

    payment_date TIMESTAMP,

    status VARCHAR(30) DEFAULT 'PENDING'
    CHECK (
        status IN (
            'PENDING',
            'PAID',
            'FAILED',
            'REFUNDED'
        )
    ),

    CONSTRAINT fk_payment_contract
    FOREIGN KEY (contract_id)
    REFERENCES contracts(id)
    ON DELETE CASCADE
);

-- ==========================================
-- CONVERSATIONS
-- ==========================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    contract_id UUID UNIQUE NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_conversation_contract
    FOREIGN KEY (contract_id)
    REFERENCES contracts(id)
    ON DELETE CASCADE
);

-- ==========================================
-- MESSAGES
-- ==========================================

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    conversation_id UUID NOT NULL,

    sender_id UUID NOT NULL,

    receiver_id UUID NOT NULL,

    content TEXT NOT NULL,

    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_conversation
    FOREIGN KEY (conversation_id)
    REFERENCES conversations(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_message_sender
    FOREIGN KEY (sender_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_message_receiver
    FOREIGN KEY (receiver_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- ==========================================
-- REVIEWS
-- ==========================================

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    contract_id UUID NOT NULL,

    reviewer_id UUID NOT NULL,

    reviewee_id UUID NOT NULL,

    rating INT NOT NULL
    CHECK (rating BETWEEN 1 AND 5),

    comment TEXT,

    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_contract
    FOREIGN KEY (contract_id)
    REFERENCES contracts(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_review_reviewer
    FOREIGN KEY (reviewer_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_review_reviewee
    FOREIGN KEY (reviewee_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- ==========================================
-- NOTIFICATIONS
-- ==========================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL,

    title VARCHAR(255),

    content TEXT,

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

-- ==========================================
-- INDEXES
-- ==========================================

CREATE INDEX idx_users_email
ON users(email);

CREATE INDEX idx_projects_enterprise
ON projects(enterprise_id);

CREATE INDEX idx_projects_category
ON projects(category_id);

CREATE INDEX idx_proposals_project
ON proposals(project_id);

CREATE INDEX idx_proposals_expert
ON proposals(expert_id);

CREATE INDEX idx_contracts_project
ON contracts(project_id);

CREATE INDEX idx_contracts_expert
ON contracts(expert_id);

CREATE INDEX idx_milestones_contract
ON milestones(contract_id);

CREATE INDEX idx_payments_contract
ON payments(contract_id);

CREATE INDEX idx_messages_sender
ON messages(sender_id);

CREATE INDEX idx_messages_receiver
ON messages(receiver_id);

CREATE INDEX idx_reviews_reviewee
ON reviews(reviewee_id);

CREATE INDEX idx_notifications_user
ON notifications(user_id);