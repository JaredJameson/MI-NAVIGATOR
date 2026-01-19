UPDATE users SET role = 'admin' WHERE email = 'admin210@test.com';
SELECT id, email, role FROM users WHERE email = 'admin210@test.com';
