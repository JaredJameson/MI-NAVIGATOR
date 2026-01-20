#!/usr/bin/env python3
"""Create a large test file for Feature #202 testing - Session 355."""

import os

# Create a 50MB test PDF file
file_size = 50 * 1024 * 1024  # 50 MB
output_path = "/tmp/test_50mb_session355.pdf"

print(f"Creating {file_size / 1024 / 1024}MB test file for Session 355...")

with open(output_path, 'wb') as f:
    # Write in chunks to avoid memory issues
    chunk_size = 1024 * 1024  # 1MB chunks
    chunks_written = 0
    while chunks_written < file_size:
        remaining = file_size - chunks_written
        write_size = min(chunk_size, remaining)
        f.write(b'0' * write_size)
        chunks_written += write_size

print(f"✅ Created: {output_path}")
print(f"   Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
