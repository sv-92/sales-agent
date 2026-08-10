-- SalesFlow Agent Demo CRM Data
-- Realistic mock data for sales agent demonstration

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT NOT NULL,
    size TEXT NOT NULL,
    revenue REAL
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    email TEXT NOT NULL,
    account_id INTEGER REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    stage TEXT NOT NULL,
    account_id INTEGER REFERENCES accounts(id),
    close_date TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY,
    quarter TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    industry TEXT,
    size TEXT,
    status TEXT DEFAULT 'new',
    score INTEGER
);

-- Accounts
INSERT INTO accounts (id, name, industry, size, revenue) VALUES
(1, 'TechVault Solutions', 'Technology', 'Enterprise', 85000000),
(2, 'MediBridge Health', 'Healthcare', 'Mid-Market', 42000000),
(3, 'FinanceForward Inc', 'Financial Services', 'Enterprise', 120000000),
(4, 'RetailNova Group', 'Retail', 'Mid-Market', 35000000),
(5, 'CloudManufact Corp', 'Manufacturing', 'Enterprise', 95000000);

-- Contacts
INSERT INTO contacts (id, name, title, email, account_id) VALUES
(1, 'Sarah Chen', 'VP of Engineering', 'sarah.chen@techvault.com', 1),
(2, 'Marcus Johnson', 'CTO', 'mjohnson@techvault.com', 1),
(3, 'Dr. Lisa Park', 'Chief Digital Officer', 'lpark@medibridge.com', 2),
(4, 'David Williams', 'Head of Procurement', 'dwilliams@medibridge.com', 2),
(5, 'Robert Taylor', 'SVP Operations', 'rtaylor@financeforward.com', 3),
(6, 'Amanda Foster', 'Director of Innovation', 'afoster@retailnova.com', 4),
(7, 'James Mitchell', 'VP of IT', 'jmitchell@cloudmanufact.com', 5),
(8, 'Patricia Nguyen', 'Chief Strategy Officer', 'pnguyen@cloudmanufact.com', 5);

-- Deals (varying stages and amounts)
INSERT INTO deals (id, name, amount, stage, account_id, close_date) VALUES
(1, 'TechVault Cloud Migration', 500000, 'Negotiation', 1, '2024-12-15'),
(2, 'MediBridge Platform License', 180000, 'Proposal', 2, '2024-11-30'),
(3, 'FinanceForward AI Suite', 1200000, 'Qualification', 3, '2025-03-01'),
(4, 'RetailNova POS Integration', 75000, 'Prospecting', 4, '2025-01-15'),
(5, 'CloudManufact IoT Platform', 850000, 'Negotiation', 5, '2024-12-30'),
(6, 'TechVault Security Addon', 120000, 'Proposal', 1, '2024-11-15'),
(7, 'MediBridge Analytics Module', 95000, 'Closed Won', 2, '2024-09-30'),
(8, 'FinanceForward Compliance Tool', 340000, 'Prospecting', 3, '2025-06-01'),
(9, 'RetailNova Mobile App', 45000, 'Closed Won', 4, '2024-08-15'),
(10, 'CloudManufact Data Lake', 620000, 'Qualification', 5, '2025-02-28');

-- Forecasts (quarterly)
INSERT INTO forecasts (id, quarter, amount, category, confidence) VALUES
(1, 'Q1', 850000, 'Commit', 0.90),
(2, 'Q1', 400000, 'Best Case', 0.60),
(3, 'Q2', 1100000, 'Commit', 0.85),
(4, 'Q2', 600000, 'Best Case', 0.55),
(5, 'Q3', 1450000, 'Commit', 0.80),
(6, 'Q3', 900000, 'Best Case', 0.50),
(7, 'Q3', 350000, 'Upside', 0.30),
(8, 'Q4', 1800000, 'Commit', 0.75),
(9, 'Q4', 1200000, 'Best Case', 0.45),
(10, 'Q4', 500000, 'Upside', 0.25);

-- Leads
INSERT INTO leads (id, company_name, contact_name, industry, size, status, score) VALUES
(1, 'Acme Corp', 'John Smith', 'Technology', 'Mid-Market', 'new', NULL),
(2, 'Global Dynamics', 'Maria Garcia', 'Manufacturing', 'Enterprise', 'qualified', 82),
(3, 'Horizon Labs', 'Alex Turner', 'Healthcare', 'Startup', 'nurture', 45);
