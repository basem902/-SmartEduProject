-- Add telegram_id and telegram_username columns if not exist
ALTER TABLE teachers ADD COLUMN IF NOT EXISTS telegram_id BIGINT UNIQUE;
ALTER TABLE teachers ADD COLUMN IF NOT EXISTS telegram_username VARCHAR(100);

-- Update teacher with telegram_id
UPDATE teachers SET telegram_id = 5844908352 WHERE id = 1;

-- Verify
SELECT id, full_name, email, telegram_id FROM teachers;
