-- Enable 2FA for test2fa@example.com user
-- Set both totp_secret and two_factor_enabled

UPDATE users
SET
  totp_secret = 'RWLS2I4IEEDKXZ4T3HWZLZ5ZV5ALACK2',
  two_factor_enabled = true,
  updated_at = NOW()
WHERE email = 'test2fa@example.com';

-- Verify the change
SELECT email, two_factor_enabled,
       CASE WHEN totp_secret IS NOT NULL THEN 'SET' ELSE 'NULL' END as totp_secret_status
FROM users
WHERE email = 'test2fa@example.com';
