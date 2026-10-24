/**
 * End-to-end smoke test for the QuizGen frontend.
 *
 * Drives the real UI in a headless Chromium browser over the DevTools
 * protocol, so no test framework or browser-download is required.
 *
 * Prerequisites:
 *   - the backend running on http://127.0.0.1:8000
 *   - the dev server running on http://localhost:5173
 *
 * Usage:
 *   npm run e2e
 *
 * Environment overrides:
 *   E2E_APP_URL   default http://localhost:5173
 *   E2E_CDP_PORT  default 9222
 *   E2E_BROWSER   path to the browser executable (auto-detected otherwise)
 */
import { spawn } from 'node:child_process'
import { existsSync, mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const APP = process.env.E2E_APP_URL ?? 'http://localhost:5173'
const CDP_PORT = Number(process.env.E2E_CDP_PORT ?? 9222)

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function findBrowser() {
  if (process.env.E2E_BROWSER) return process.env.E2E_BROWSER

  const candidates =
    process.platform === 'win32'
      ? [
          join(process.env['PROGRAMFILES(X86)'] ?? '', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
          join(process.env['PROGRAMFILES'] ?? '', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
          join(process.env.LOCALAPPDATA ?? '', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
          join(process.env['PROGRAMFILES(X86)'] ?? '', 'Google', 'Chrome', 'Application', 'chrome.exe'),
          join(process.env['PROGRAMFILES'] ?? '', 'Google', 'Chrome', 'Application', 'chrome.exe'),
        ]
      : ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']

  return candidates.find((path) => path && existsSync(path))
}

async function launchBrowser() {
  const executable = findBrowser()
  if (!executable) throw new Error('No Chromium browser found. Set E2E_BROWSER to an executable path.')

  const profile = mkdtempSync(join(tmpdir(), 'quizgen-e2e-'))
  const child = spawn(
    executable,
    [
      '--headless=new',
      '--disable-gpu',
      '--no-sandbox',
      '--no-first-run',
      `--remote-debugging-port=${CDP_PORT}`,
      `--user-data-dir=${profile}`,
      'about:blank',
    ],
    { stdio: 'ignore' },
  )

  for (let attempt = 0; attempt < 40; attempt += 1) {
    await sleep(250)
    try {
      const response = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`)
      if (response.ok) return child
    } catch {
      // browser is still starting
    }
  }

  child.kill()
  throw new Error('Browser did not expose the DevTools port in time.')
}

async function connect() {
  const response = await fetch(`http://127.0.0.1:${CDP_PORT}/json/new?url=about:blank`, { method: 'PUT' })
  const target = await response.json()
  const socket = new WebSocket(target.webSocketDebuggerUrl)
  await new Promise((resolve) => socket.addEventListener('open', resolve, { once: true }))

  let id = 0
  const pending = new Map()
  socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data)
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id)
      pending.delete(message.id)
      if (message.error) reject(new Error(JSON.stringify(message.error)))
      else resolve(message.result)
    }
  })

  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const messageId = ++id
      pending.set(messageId, { resolve, reject })
      socket.send(JSON.stringify({ id: messageId, method, params }))
    })

  const evaluate = async (expression) => {
    const result = await send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
    })
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text)
    return result.result.value
  }

  return { send, evaluate }
}

const checks = []
function check(name, passed, detail = '') {
  checks.push({ name, passed })
  console.log(`${passed ? 'PASS' : 'FAIL'}  ${name}${detail ? ` — ${detail}` : ''}`)
}

/** Sets a React-controlled input value and fires the change event. */
const setValue = (selector, value) => `
  (() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) return false;
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, ${JSON.stringify(value)});
    el.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`

/** Clicks the first element matching the selector whose text contains the text. */
const clickText = (selector, text) => `
  (() => {
    const el = [...document.querySelectorAll(${JSON.stringify(selector)})]
      .find((node) => node.textContent.trim().toLowerCase().includes(${JSON.stringify(text.toLowerCase())}));
    if (!el) return false;
    el.click();
    return true;
  })()`

async function main() {
  const browser = await launchBrowser()

  try {
    const { send, evaluate } = await connect()
    await send('Page.enable')
    await send('Runtime.enable')

    const goto = async (url) => {
      await send('Page.navigate', { url })
      await sleep(1500)
    }

    await goto(`${APP}/login`)
    await evaluate('localStorage.clear()')
    await sleep(300)

    // --- register -------------------------------------------------------
    await goto(`${APP}/register`)
    const username = `e2e${Date.now().toString().slice(-7)}`
    await evaluate(setValue('#email', `${username}@example.com`))
    await evaluate(setValue('#username', username))
    await evaluate(setValue('#password', 'secret123'))
    await evaluate(setValue('#confirm-password', 'secret123'))
    await sleep(200)
    await evaluate(clickText('button', 'Create account'))
    await sleep(2500)

    let state = await evaluate('({ url: location.pathname, text: document.body.innerText })')
    check('register redirects to the dashboard', state.url === '/', `path=${state.url}`)
    check('dashboard greets the new user', state.text.includes(username))

    // --- generate -------------------------------------------------------
    await goto(`${APP}/generate`)
    await evaluate(setValue('#topic', 'Quantum Computing'))
    await evaluate(clickText('button', 'Generate quiz'))
    await sleep(200)
    check(
      'quiz type must be selected',
      await evaluate("document.body.innerText.includes('Please choose General or Niche.')"),
    )
    await evaluate("document.querySelector('input[name=\"quiz-type\"][value=\"general\"]').click()")
    await sleep(200)
    await evaluate(clickText('button', 'Generate quiz'))
    for (let attempt = 0; attempt < 90; attempt += 1) {
      state = await evaluate(
        '({ url: location.pathname, text: document.body.innerText, hasAlert: Boolean(document.querySelector(\'[role="alert"]\')) })',
      )
      if (/^\/quiz\/\d+$/.test(state.url) || state.hasAlert) break
      await sleep(1000)
    }

    check('generate opens the quiz', /^\/quiz\/\d+$/.test(state.url), `path=${state.url}`)
    check('quiz shows its topic', state.text.includes('Quantum Computing'))
    check('quiz displays the General type', state.text.includes('General'))
    check('quiz starts at question 1 of 8', state.text.includes('Question 1 of 8'))
    check('answers stay hidden before submitting', !state.text.includes('Correct answer:'))

    // --- take the quiz --------------------------------------------------
    await evaluate(clickText('button', 'A'))
    await sleep(250)
    check(
      'picking an option marks it answered',
      await evaluate("document.body.innerText.includes('1/8 answered')"),
    )

    for (let question = 0; question < 7; question += 1) {
      await evaluate(clickText('button', 'Next'))
      await sleep(400)
      await evaluate(clickText('button', 'B'))
      await sleep(200)
    }

    check(
      'navigating reaches the last question',
      await evaluate("document.body.innerText.includes('Question 8 of 8')"),
    )

    await evaluate(clickText('button', 'Submit answers'))
    await sleep(2500)

    state = await evaluate('({ url: location.pathname, text: document.body.innerText })')
    check('results screen renders', /your score/i.test(state.text))
    check('score percentage is shown', /\d+%/.test(state.text))
    check('review section is shown', state.text.includes('Review'))
    check('correct answers are revealed after submitting', state.text.includes('Correct answer:'))

    // --- library --------------------------------------------------------
    await goto(`${APP}/`)
    for (let attempt = 0; attempt < 15; attempt += 1) {
      state = await evaluate('({ url: location.pathname, text: document.body.innerText })')
      if (state.text.includes('Quantum Computing')) break
      await sleep(1000)
    }
    check(
      'quiz appears in the library',
      state.text.includes('Quantum Computing'),
    )

    await evaluate(clickText('button', 'Share publicly'))
    for (let attempt = 0; attempt < 10; attempt += 1) {
      if (await evaluate("document.body.innerText.includes('Make private')")) break
      await sleep(300)
    }
    check('owner can publish their quiz', await evaluate("document.body.innerText.includes('Make private')"))

    await evaluate(clickText('a', 'Community'))
    await sleep(1000)
    check('public quiz appears in the community directory', await evaluate("document.body.innerText.includes('Quantum Computing')"))
    await evaluate(clickText('button', 'Take quiz'))
    await sleep(1000)
    state = await evaluate('({ url: location.pathname, text: document.body.innerText })')
    check('share link opens the shared quiz page', /^\/shared\/\d+$/.test(state.url), `path=${state.url}`)
    check('shared quiz page does not reveal answers early', !state.text.includes('Correct answer:'))
    check(
      'public quiz API omits correct answers before submission',
      await evaluate(
        "fetch(`/api/quizzes/shared/${location.pathname.split('/').pop()}`).then(r => r.json()).then(q => q.questions.every(question => !('correct_option' in question)))",
      ),
    )

    // --- sign out -------------------------------------------------------
    await evaluate(clickText('button', 'Log out'))
    for (let attempt = 0; attempt < 10; attempt += 1) {
      state = await evaluate('location.pathname')
      if (state === '/login') break
      await sleep(500)
    }
    check('logout returns to the login page', state === '/login', `path=${state}`)

    await goto(`${APP}/community`)
    check('community directory is public while signed out', await evaluate("document.body.innerText.includes('Quantum Computing')"))

    await goto(`${APP}/`)
    state = await evaluate('location.pathname')
    check('protected routes redirect when signed out', state === '/login', `path=${state}`)
  } finally {
    browser.kill()
  }

  const failed = checks.filter((c) => !c.passed).length
  console.log(`\n${checks.length - failed}/${checks.length} checks passed`)
  process.exit(failed === 0 ? 0 : 1)
}

main().catch((error) => {
  console.error('E2E run failed:', error)
  process.exit(1)
})
