CREATE TABLE jobs (
    job_id UUID PRIMARY KEY,
    previous_version_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'active',
    job_title TEXT NOT NULL,
    job_description TEXT NOT NULL,
    budget_min INTEGER,
    budget_max INTEGER,
    budget_currency TEXT,
    location TEXT,
    company_name TEXT,
    employment_type TEXT,
    required_skills TEXT NOT NULL,
    is_bachelor BOOLEAN DEFAULT FALSE,
    is_master BOOLEAN DEFAULT FALSE,
    tenure INTEGER,
    job_embedding vector(32)
);
CREATE INDEX ON jobs USING ivfflat (job_embedding vector_cosine_ops) WITH (lists = 100);


CREATE TABLE candidates (
    candidate_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_name TEXT NOT NULL,
    last_name TEXT,
    birthdate DATE,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    skills TEXT NOT NULL,
    
    -- Current Experience
    current_company TEXT,
    current_job_role TEXT,
    current_start_date DATE,
    current_end_date DATE,
    
    -- Previous Experience
    previous_company TEXT,
    previous_job_role TEXT,
    previous_start_date DATE,
    previous_end_date DATE,
    
    -- Education
    bachelor_institution TEXT,
    bachelor_degree TEXT,
    bachelor_graduation_year INTEGER,
    has_bachelor BOOLEAN DEFAULT FALSE,
    
    master_institution TEXT,
    master_degree TEXT,
    master_graduation_year INTEGER,
    has_master BOOLEAN DEFAULT FALSE,
    
    candidate_tenure INTEGER,
    candidate_embedding vector(32)
);

CREATE INDEX ON jobs USING ivfflat (candidate_embedding vector_cosine_ops) WITH (lists = 100);