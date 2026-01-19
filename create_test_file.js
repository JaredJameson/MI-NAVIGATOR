// Create a 50MB test file
const fs = require('fs');

const filePath = '/tmp/test_50mb.pdf';
const sizeInMB = 50;
const sizeInBytes = sizeInMB * 1024 * 1024;

console.log(`Creating ${sizeInMB}MB test file...`);

// Create a buffer with repeated data
const chunkSize = 1024 * 1024; // 1MB
const chunk = Buffer.alloc(chunkSize, '0');

const stream = fs.createWriteStream(filePath);

let written = 0;
while (written < sizeInBytes) {
    const remaining = sizeInBytes - written;
    const writeSize = Math.min(chunkSize, remaining);
    stream.write(chunk.slice(0, writeSize));
    written += writeSize;
}

stream.end(() => {
    const stats = fs.statSync(filePath);
    console.log(`✅ Created: ${filePath}`);
    console.log(`   Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
});
