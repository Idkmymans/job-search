/*
  # Create Tenders Management Schema

  1. New Tables
    - `tenders`
      - `id` (uuid, primary key)
      - `ifb_no` (text, unique) - Tender invitation for bid number
      - `title` (text) - Tender title
      - `organization` (text) - Organization announcing tender
      - `deadline` (timestamptz) - Application deadline
      - `procurement_type` (text) - Type (works ncb, goods ncb, etc)
      - `notice_date` (timestamptz) - When notice was published
      - `province` (text) - Province location
      - `source` (text) - Source (Bolpatra, Manual)
      - `days_left` (integer) - Days until deadline
      - `scraped_date` (date) - Date when data was scraped
      - `marked_relevant` (boolean) - User relevance marker
      - `created_at` (timestamptz) - Record creation time
      - `updated_at` (timestamptz) - Last update time

    - `tender_filters`
      - `id` (uuid, primary key)
      - `name` (text) - Filter preset name
      - `filter_config` (jsonb) - Filter criteria
      - `created_at` (timestamptz)

    - `audit_log`
      - `id` (uuid, primary key)
      - `action_type` (text) - Action name (export, delete, mark_relevant)
      - `details` (jsonb) - Action details
      - `created_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Add policies for unauthenticated access (demo mode)

  3. Indexes
    - Index on ifb_no, organization, deadline, days_left
*/

CREATE TABLE IF NOT EXISTS tenders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ifb_no text UNIQUE NOT NULL,
  title text NOT NULL,
  organization text NOT NULL,
  deadline timestamptz NOT NULL,
  procurement_type text NOT NULL,
  notice_date timestamptz NOT NULL,
  province text,
  source text NOT NULL DEFAULT 'Manual',
  days_left integer,
  scraped_date date DEFAULT CURRENT_DATE,
  marked_relevant boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tender_filters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  filter_config jsonb NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  action_type text NOT NULL,
  details jsonb NOT NULL,
  tender_count integer,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tenders_ifb_no ON tenders(ifb_no);
CREATE INDEX IF NOT EXISTS idx_tenders_organization ON tenders(organization);
CREATE INDEX IF NOT EXISTS idx_tenders_deadline ON tenders(deadline);
CREATE INDEX IF NOT EXISTS idx_tenders_days_left ON tenders(days_left);
CREATE INDEX IF NOT EXISTS idx_tenders_marked_relevant ON tenders(marked_relevant);
CREATE INDEX IF NOT EXISTS idx_tenders_scraped_date ON tenders(scraped_date);

ALTER TABLE tenders ENABLE ROW LEVEL SECURITY;
ALTER TABLE tender_filters ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenders_select_all"
  ON tenders FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "tenders_insert_all"
  ON tenders FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "tenders_update_all"
  ON tenders FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "tenders_delete_all"
  ON tenders FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "tender_filters_select_all"
  ON tender_filters FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "tender_filters_insert_all"
  ON tender_filters FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "tender_filters_delete_all"
  ON tender_filters FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "audit_log_select_all"
  ON audit_log FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "audit_log_insert_all"
  ON audit_log FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);
