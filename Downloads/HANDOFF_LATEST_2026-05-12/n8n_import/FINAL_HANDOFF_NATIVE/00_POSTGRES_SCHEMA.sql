create extension if not exists pgcrypto;

create table if not exists lead (
  lead_id text primary key default ('L' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  lead_batch_id text,
  business_name text not null,
  niche text,
  location text,
  website_url text,
  social_links jsonb not null default '[]'::jsonb,
  lead_score numeric,
  score_reason text,
  pain_points jsonb not null default '[]'::jsonb,
  source_urls jsonb not null default '[]'::jsonb,
  sales_stage text not null default 'scraped',
  reply_status text not null default 'none',
  assigned_owner text,
  last_contact_at timestamptz,
  follow_up_count integer not null default 0,
  last_follow_up_at timestamptz,
  next_action text,
  outreach_subject text,
  outreach_body text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists client (
  client_id text primary key default ('C' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  client_name text not null,
  origin_lead_id text references lead(lead_id),
  owner text,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists project (
  project_id text primary key default ('P' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  client_id text not null references client(client_id),
  project_name text not null,
  service_type text,
  business_stage text not null default 'Client Active',
  production_stage text not null default 'Brief Received',
  current_owner text,
  waiting_on text,
  next_action text,
  due_date date,
  brief_summary text,
  selected_direction text,
  drive_folder_url text,
  latest_result_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists content_request (
  request_id text primary key default ('CR' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  project_id text not null references project(project_id),
  goal text,
  brief_text text,
  references jsonb not null default '[]'::jsonb,
  status text not null default 'created',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists approval_item (
  approval_id text primary key default ('A' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  project_id text not null references project(project_id),
  asset_type text,
  approval_status text not null default 'draft',
  reviewer text,
  feedback_text text,
  submitted_at timestamptz,
  decision_at timestamptz
);

create table if not exists revision_item (
  revision_id text primary key default ('R' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  project_id text not null references project(project_id),
  target_asset text,
  instruction_text text,
  revision_status text not null default 'open',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists delivery_record (
  delivery_id text primary key default ('D' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  project_id text not null references project(project_id),
  delivered_asset text,
  drive_folder_url text,
  delivered_to text,
  delivered_at timestamptz
);

create table if not exists invoice_record (
  invoice_id text primary key default ('I' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  project_id text not null references project(project_id),
  client_id text not null references client(client_id),
  invoice_amount numeric,
  invoice_status text not null default 'draft',
  invoice_sent_at timestamptz,
  payment_waiting boolean not null default false,
  paid_at timestamptz
);

create table if not exists workflow_run (
  run_id text primary key default ('RUN' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8))),
  workflow_name text not null,
  related_record_type text,
  related_record_id text,
  run_status text not null,
  trigger_source text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  error_text text
);

create index if not exists idx_lead_stage on lead(sales_stage);
create index if not exists idx_lead_batch on lead(lead_batch_id);
create index if not exists idx_project_client on project(client_id);
create index if not exists idx_project_stages on project(business_stage, production_stage);
create index if not exists idx_project_waiting_on on project(waiting_on);
create index if not exists idx_approval_status on approval_item(approval_status);
create index if not exists idx_revision_status on revision_item(revision_status);
create index if not exists idx_invoice_status on invoice_record(invoice_status, payment_waiting);
