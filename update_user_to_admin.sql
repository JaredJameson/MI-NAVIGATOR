-- Update admin@test.com to have admin role
UPDATE users
SET role = 'admin'
WHERE email = 'admin@test.com';

-- Verify the change
SELECT id, email, name, role, is_active
FROM users
WHERE email = 'admin@test.com';
