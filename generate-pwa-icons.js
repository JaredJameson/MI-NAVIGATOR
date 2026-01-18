/**
 * Generate PWA icons using Canvas (node-canvas)
 * Creates 192x192 and 512x512 PNG icons with app branding
 */

const fs = require('fs');
const path = require('path');

// Try to use canvas if available
let Canvas;
try {
  Canvas = require('canvas');
} catch (e) {
  console.log('⚠️  node-canvas not installed');
  console.log('📦 Install with: npm install canvas');
  console.log('');
  console.log('Alternative: Use online tool to create icons:');
  console.log('1. Go to https://www.pwabuilder.com/imageGenerator');
  console.log('2. Upload a logo or use placeholder');
  console.log('3. Download generated icons');
  console.log('4. Place in frontend/public/ directory');
  console.log('');
  console.log('Required icons:');
  console.log('- icon-192x192.png');
  console.log('- icon-512x512.png');
  process.exit(1);
}

const { createCanvas } = Canvas;

const sizes = [192, 512];
const outputDir = path.join(__dirname, 'frontend', 'public');

// Brand colors
const brandColor = '#3b82f6'; // Blue
const textColor = '#ffffff';   // White

sizes.forEach(size => {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Background
  ctx.fillStyle = brandColor;
  ctx.fillRect(0, 0, size, size);

  // Add "MI" text
  ctx.fillStyle = textColor;
  ctx.font = `bold ${size * 0.4}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('MI', size / 2, size / 2);

  // Save
  const filename = `icon-${size}x${size}.png`;
  const filepath = path.join(outputDir, filename);
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(filepath, buffer);
  console.log(`✅ Created ${filename}`);
});

console.log('');
console.log('✅ PWA icons generated successfully!');
console.log('📝 Update manifest.json with:');
console.log(JSON.stringify({
  icons: [
    {
      src: '/icon-192x192.png',
      sizes: '192x192',
      type: 'image/png',
      purpose: 'any maskable'
    },
    {
      src: '/icon-512x512.png',
      sizes: '512x512',
      type: 'image/png',
      purpose: 'any maskable'
    }
  ]
}, null, 2));
