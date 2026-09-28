const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const artifactDir = '/config/.gemini/antigravity/brain/2a8c129c-0dd3-4bfc-b04b-94307a0b57aa';
  
  console.log('Launching Chrome browser for video recording...');
  const browser = await chromium.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: {
      dir: artifactDir,
      size: { width: 1280, height: 800 }
    }
  });

  const page = await context.newPage();
  console.log('Navigating to http://localhost:8080...');
  await page.goto('http://localhost:8080', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 1. First prompt: Core app feature (3-day tropical trip)
  console.log('Submitting Prompt 1...');
  await page.fill('#input', 'Recommend a 3-day tropical trip to Bali with hotel options');
  await page.click('button.send-btn');
  
  // Wait for response bubble to receive text/content
  console.log('Waiting for response to Prompt 1...');
  await page.waitForFunction(() => {
    const bubbles = document.querySelectorAll('.msg.agent .bubble');
    if (bubbles.length === 0) return false;
    const last = bubbles[bubbles.length - 1];
    return last.textContent && !last.textContent.includes('…');
  }, { timeout: 30000 });

  await page.waitForTimeout(4000);

  // 2. Toggle Dark Mode to showcase theme switcher
  console.log('Toggling Dark Mode...');
  await page.click('#theme-toggle');
  await page.waitForTimeout(2000);

  // 3. Second prompt: Tool call, currency conversion & generated image
  console.log('Submitting Prompt 2...');
  await page.fill('#input', 'Generate a scenic travel photograph of a tropical beach sunset in Bali and convert $2000 to EUR');
  await page.click('button.send-btn');

  console.log('Waiting for response to Prompt 2...');
  await page.waitForFunction(() => {
    const bubbles = document.querySelectorAll('.msg.agent .bubble');
    if (bubbles.length < 2) return false;
    const last = bubbles[bubbles.length - 1];
    return last.textContent && !last.textContent.includes('…');
  }, { timeout: 45000 });

  await page.waitForTimeout(5000);

  const videoPage = page.video();
  const videoPath = await videoPage.path();
  console.log('Raw video recorded to:', videoPath);

  await context.close();
  await browser.close();

  // Rename video file to demo_recording.webm in artifact directory
  const targetPath = path.join(artifactDir, 'demo_recording.webm');
  fs.copyFileSync(videoPath, targetPath);
  console.log('Successfully saved demo video to:', targetPath);
})();
