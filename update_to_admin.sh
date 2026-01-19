#!/bin/bash
sqlite3 mi_navigator.db << 'EOFSQL'
UPDATE users SET role = 'admin' WHERE email = 'admin210@test.com';
SELECT 'User updated to admin:';
SELECT id, email, role FROM users WHERE email = 'admin210@test.com';
EOFSQL
