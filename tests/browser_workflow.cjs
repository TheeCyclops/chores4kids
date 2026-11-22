// Actual bundled-card checks with synthetic HA data. No household connection.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const root = path.resolve(__dirname, '..');
const screenshotDir = process.env.SCREENSHOT_DIR || os.tmpdir();
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || path.resolve(root, '../MagicMirror/node_modules/playwright'));

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1500 } });
    const errors = [];
    const consoleErrors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
    await page.route('https://workflow.test/', route => route.fulfill({ contentType: 'text/html',
      body: '<title>Chores4Kids workflow test</title><style>body{font:16px sans-serif;--primary-color:#007ca8;--primary-text-color:#24314a;--divider-color:#d3dce4;--card-background-color:white;--secondary-background-color:#f4f6f8;background:#f4f6f8}</style><script type="module" src="https://workflow.test/card.js"></script>' }));
    await page.route('https://workflow.test/card.js', route => route.fulfill({ contentType: 'text/javascript',
      body: fs.readFileSync(path.join(root, 'custom_components/chores4kids/www/chores4kids-card.js'), 'utf8') }));
    await page.goto('https://workflow.test/');
    await page.waitForFunction(() => customElements.get('chores4kids-card'));
    await page.evaluate(() => {
      const card = document.createElement('chores4kids-card');
      window.card = card;
      window.calls = [];
      card.setConfig({ mode: 'admin' });
      card.hass = { user: { is_admin: true }, language: 'en',
        callService: async (domain, service, data) => {
          window.calls.push({ domain, service, data });
          if (window.failNext) { window.failNext = false; throw new Error('Test save failure'); }
        },
        states: {
          'sensor.points_x': { entity_id: 'sensor.points_x', state: '70', attributes: { child_id: 'x', name: 'Xander', slug: 'x', tasks: [] } },
          'sensor.chores4kids_tasks': { entity_id: 'sensor.chores4kids_tasks', state: '1', attributes: { tasks: [], categories: [], archived_tasks: [{ title: 'Old chore', points: 3, status: 'approved', assigned_to: 'x' }] } },
          'sensor.chores4kids_shop': { entity_id: 'sensor.chores4kids_shop', state: '1', attributes: { items: [{ id: 'r', title: 'Movie night', price: 10, active: true }], purchases: [] } },
          'sensor.workflow': { entity_id: 'sensor.workflow', state: 'active', attributes: {
            schema_version: 2, active: true, definitions: {}, occurrences: {}, runs: {}, routines: {}, eligible: []
          } }
        }
      };
      document.body.append(card);
    });
    await page.getByRole('button', { name: 'Library', exact: true }).click();
    await page.getByRole('button', { name: 'Add chore', exact: true }).click();
    await page.getByLabel('Name', { exact: true }).fill('Change filter');
    await page.getByLabel('First due date').fill('2026-12-01');
    await page.locator('input[name="every"]').fill('3');
    await page.locator('select[name="unit"]').selectOption('months');
    await page.evaluate(() => { window.failNext = true; });
    await page.getByRole('button', { name: 'Save future schedule' }).click();
    await page.getByRole('alert').filter({ hasText: 'Test save failure' }).waitFor();
    await page.getByRole('button', { name: 'Save future schedule' }).click();
    await page.waitForFunction(() => window.calls.length === 2 && !window.card._wfBusy);
    const choreCalls = await page.evaluate(() => window.calls);
    assert.equal(choreCalls[0].data.payload.request_id, choreCalls[1].data.payload.request_id);
    assert.equal(choreCalls[1].data.payload.schedule.every, 3);
    assert.equal(choreCalls[1].data.payload.schedule.unit, 'months');

    await page.getByRole('button', { name: 'Routines', exact: true }).click();
    await page.getByRole('button', { name: 'Add routine', exact: true }).click();
    await page.getByLabel('Name', { exact: true }).fill('Morning');
    await page.locator('input[name="person"]').check();
    await page.getByRole('button', { name: 'Add step', exact: true }).click();
    await page.getByLabel('Step 1', { exact: true }).fill('Get dressed');
    await page.getByRole('button', { name: 'Add step', exact: true }).click();
    await page.getByLabel('Step 2', { exact: true }).fill('Brush teeth');
    await page.getByRole('button', { name: 'Move step up', exact: true }).nth(1).click();
    assert.deepEqual(await page.evaluate(() => window.card._wfRoutine.steps.map(s => s.title)), ['Brush teeth', 'Get dressed']);
    await page.screenshot({ path: path.join(screenshotDir, 'chores4kids-routine-editor.png'), fullPage: true });
    await page.getByRole('button', { name: 'Save routine', exact: true }).click();
    await page.waitForFunction(() => window.calls.length === 3 && !window.card._wfBusy);
    const routineCall = await page.evaluate(() => window.calls[2]);
    assert.equal(routineCall.data.action, 'save_routine');
    assert.deepEqual(routineCall.data.payload.people, ['x']);
    assert.deepEqual(routineCall.data.payload.steps.map(s => s.title), ['Brush teeth', 'Get dressed']);

    await page.getByRole('button', { name: 'Rewards', exact: true }).click();
    assert.equal(await page.getByText('Movie night', { exact: false }).first().isVisible(), true);
    await page.getByRole('button', { name: 'Buy', exact: true }).click();
    await page.waitForFunction(() => window.calls.some(c => c.service === 'buy_shop_item'));
    await page.getByRole('button', { name: 'Archive', exact: true }).click();
    await page.getByText('Old chore', { exact: false }).waitFor();
    await page.evaluate(() => {
      window.card.hass.states['sensor.workflow'].attributes.runs = {
        morning: { id: 'morning', child_id: 'x', title: 'Morning', closed: false,
          starts_at: '2026-11-23T06:30:00-06:00', finish_at: '2026-11-23T07:40:00-06:00',
          steps: [{ id: 'teeth', title: 'Brush teeth', points: 1 }], checked: {}, bonus: 5, bonus_status: 'not_eligible' }
      };
      window.card.requestUpdate();
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole('button', { name: 'Routines', exact: true }).click();
    await page.getByRole('button', { name: 'Check off', exact: true }).click();
    await page.waitForFunction(() => window.calls.some(c => c.data.action === 'check_step'));
    assert.equal(await page.evaluate(() => window.card.hass.states['sensor.points_x'].state), '70');
    await page.screenshot({ path: path.join(screenshotDir, 'chores4kids-workflow-narrow.png'), fullPage: true });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.evaluate(() => { window.card.hass.user.is_admin = false; window.card.requestUpdate(); });
    await page.waitForFunction(() => !Array.from(window.card.shadowRoot.querySelectorAll('nav button')).some(b => b.textContent === 'Library'));
    assert.deepEqual(errors, []);
    assert.deepEqual(consoleErrors, []);
    console.log('PASS: bundled card identity/content, quarterly save/retry, ordered routine save, step submission without optimistic points, reward purchase, archive, admin controls, narrow viewport, no page/console errors.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
