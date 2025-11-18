/*
  # Add Automatic Daily Days Left Decrement

  1. Purpose
     - Automatically recalculate days_left column daily for all active tenders
     - Keeps the days_left field synchronized with the deadline date
     - Runs automatically at midnight every day via pg_cron scheduled job

  2. New Functions
     - `decrement_days_left()` - Recalculates days_left for all tenders based on deadline minus current date
       - Sets days_left to 0 if deadline has passed
       - Handles null deadlines gracefully
       - Updates the updated_at timestamp when changes occur

  3. Scheduled Jobs
     - pg_cron job scheduled to run daily at midnight UTC
     - Job executes the decrement_days_left function
     - Ensures accurate days_left values across the system

  4. Edge Cases Handled
     - Null deadline values are skipped
     - Past deadlines are set to 0 (not negative)
     - Current date calculations use CURRENT_DATE in UTC
     - Updated_at timestamp is set to now() for modified records

  5. Important Notes
     - pg_cron extension must be enabled in Supabase project
     - All times are in UTC
     - This is non-destructive and can be run multiple times safely
*/

-- Enable pg_cron extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Create function to decrement days_left
CREATE OR REPLACE FUNCTION decrement_days_left()
RETURNS integer AS $$
DECLARE
  v_count integer;
BEGIN
  UPDATE tenders
  SET 
    days_left = GREATEST(0, (deadline::date - CURRENT_DATE)::integer),
    updated_at = now()
  WHERE deadline IS NOT NULL
    AND GREATEST(0, (deadline::date - CURRENT_DATE)::integer) != days_left;
  
  GET DIAGNOSTICS v_count = ROW_COUNT;
  
  RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule daily execution at midnight UTC
-- Note: Adjust the schedule if needed - '0 0 * * *' means every day at 00:00 UTC
SELECT cron.schedule(
  'decrement-days-left-daily',
  '0 0 * * *',
  'SELECT decrement_days_left()'
);

-- Initial run to update all records immediately
SELECT decrement_days_left();
