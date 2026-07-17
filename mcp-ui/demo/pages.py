"""The demo's HTML/JS pages, as Python strings.

Three pages, all vanilla — no framework, no build step:

  HOST_PAGE       the renderer. Calls a tool, reads the UI resource it gets
                  back, and renders it by mimeType. Owns the postMessage
                  conversation with whatever it puts in the iframe.

  JOURNAL_VIEWER  the page `view_journal` points its iframe at. Announces
                  itself (the ready handshake), reports its size, and posts a
                  tool call when you click an entry.

  ENTRY_VIEWER    the page `view_entry` points at. Instead of fetching, it waits
                  for the host to hand it the entry as initial render data.

This is JavaScript, and it has to be: it runs in a browser, inside an iframe.
That's the half of MCP-UI no server language reaches. Read it to see what your
Python-emitted resources are actually driving — and edit it if you're curious;
nothing here is hidden or minified.
"""

# ---------------------------------------------------------------------------
# The host renderer.
# ---------------------------------------------------------------------------

HOST_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>EpicMe UI demo — renderer</title>
<style>
  :root { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { margin: 0; background: #0f1020; color: #e7e7f0; }
  header { padding: 1rem 1.25rem; border-bottom: 1px solid #2a2a45; }
  h1 { font-size: 1.1rem; margin: 0; font-weight: 650; }
  p.sub { margin: .35rem 0 0; color: #a6a6c8; font-size: .85rem; }
  main { display: grid; grid-template-columns: 260px 1fr; gap: 0; min-height: calc(100vh - 66px); }
  nav { padding: 1rem; border-right: 1px solid #2a2a45; display: flex; flex-direction: column; gap: .5rem; }
  button.tool { text-align: left; background: #1b1c33; color: #e7e7f0; border: 1px solid #33345a;
    border-radius: 8px; padding: .6rem .75rem; cursor: pointer; font-size: .9rem; }
  button.tool:hover { background: #232447; }
  button.tool code { color: #8fd0ff; }
  section.stage { padding: 1.25rem; }
  .frame-wrap { border: 1px solid #2a2a45; border-radius: 10px; overflow: hidden; background: #fff; }
  iframe { width: 100%; border: 0; display: block; }
  .card { background: #fff; color: #1a1a2e; border-radius: 10px; padding: 1rem 1.25rem; }
  h2.section { font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; color: #a6a6c8; margin: 1.25rem 0 .5rem; }
  #log { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .78rem;
    background: #08091a; border: 1px solid #2a2a45; border-radius: 8px; padding: .75rem;
    max-height: 220px; overflow: auto; white-space: pre-wrap; }
  #log .ln { color: #b6ffb0; }
  #log .ln.in { color: #ffd479; }
  .pill { display: inline-block; font-size: .7rem; padding: .1rem .45rem; border-radius: 999px;
    background: #33345a; color: #cfd0ff; margin-left: .4rem; }
</style>
</head>
<body>
<header>
  <h1>EpicMe UI renderer <span class="pill">demo host</span></h1>
  <p class="sub">Call a tool on the left. Whatever UI resource it returns gets rendered on the right,
     exactly the way a UI-aware MCP client would render it.</p>
</header>
<main>
  <nav>
    <button class="tool" onclick="callTool('view_tag', {id: 1})">view_tag <code>{id: 1}</code></button>
    <button class="tool" onclick="callTool('view_tag', {id: 999})">view_tag <code>{id: 999}</code></button>
    <button class="tool" onclick="callTool('view_journal', {})">view_journal <code>{}</code></button>
    <button class="tool" onclick="callTool('view_entry', {id: 1})">view_entry <code>{id: 1}</code></button>
    <h2 class="section">Message log</h2>
    <div id="log" role="log">(waiting)</div>
  </nav>
  <section class="stage">
    <h2 class="section">Rendered UI</h2>
    <div id="stage"></div>
  </section>
</main>

<script>
const stage = document.getElementById('stage');
const logEl = document.getElementById('log');

function log(dir, msg) {
  const line = document.createElement('div');
  line.className = 'ln ' + (dir === 'in' ? 'in' : '');
  line.textContent = (dir === 'in' ? '← ' : '→ ') + msg;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

// The initial render data for whatever resource is currently in the iframe.
// The entry-viewer asks for it; we reply from here.
let pendingRenderData = null;

// Call a tool through the in-process bridge, then render its UI resource.
async function callTool(name, args) {
  logEl.textContent = '';
  log('out', `callTool ${name} ${JSON.stringify(args)}`);
  const res = await fetch('/demo/call/' + name, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify(args),
  });
  const data = await res.json();
  const block = data.content[0];
  if (!block || block.type !== 'resource') {
    stage.innerHTML = '<div class="card">Tool returned no UI resource.</div>';
    return;
  }
  renderResource(block.resource);
}

// The heart of a UI host: branch on mimeType.
function renderResource(resource) {
  pendingRenderData = null;
  stage.innerHTML = '';
  const mime = resource.mimeType || '';
  log('in', `resource ${resource.uri}  (${mime})`);

  if (mime === 'text/html') {
    // Raw HTML: drop it straight into an iframe via srcdoc.
    mountIframe({srcdoc: resource.text, meta: resource._meta});
  } else if (mime.startsWith('application/vnd.mcp-ui.remote-dom')) {
    // Remote DOM: run the script against a tiny element vocabulary. A real
    // client (@mcp-ui/client) runs it in the client's own design system; this
    // is a faithful stand-in that maps ui-stack/ui-text onto plain divs.
    mountIframe({srcdoc: remoteDomHost(resource.text), meta: resource._meta});
  } else if (mime === 'text/uri-list') {
    // External URL: point the iframe at the page the server hosts. If the
    // resource carried initial render data, stash it for the page to ask for.
    const meta = resource._meta || {};
    pendingRenderData = meta['mcpui.dev/ui-initial-render-data'] || null;
    mountIframe({src: resource.text, meta: resource._meta});
  } else {
    stage.innerHTML = '<div class="card">Unknown mimeType: ' + mime + '</div>';
  }
}

// Create the iframe, applying a preferred-frame-size hint if present.
function mountIframe({src, srcdoc, meta}) {
  const wrap = document.createElement('div');
  wrap.className = 'frame-wrap';
  const iframe = document.createElement('iframe');
  iframe.style.height = '420px';

  const size = meta && meta['mcpui.dev/ui-preferred-frame-size'];
  if (size) {
    log('in', `preferred-frame-size ${JSON.stringify(size)}`);
    if (size[1]) iframe.style.height = size[1];
    if (size[0]) wrap.style.maxWidth = size[0];
  }
  if (src) iframe.src = src;
  if (srcdoc) iframe.srcdoc = srcdoc;
  wrap.appendChild(iframe);
  stage.appendChild(wrap);
  window.__frame = iframe;
}

// Wrap a remote-dom script in a minimal page that gives it `root` and a
// `document.createElement` that only knows ui-stack and ui-text.
function remoteDomHost(script) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;font-family:-apple-system,sans-serif;padding:1.5rem;color:#1a1a2e}
    .ui-stack{display:flex;flex-direction:column;align-items:center;gap:12px}
    .ui-text{font-size:1rem} .ui-text:first-child{font-size:1.5rem;font-weight:700}
  </style></head><body><div id="root"></div><script>
    const root = document.getElementById('root');
    const realCreate = document.createElement.bind(document);
    document.createElement = (tag) => {
      if (tag === 'ui-stack' || tag === 'ui-text') {
        const el = realCreate('div'); el.className = tag;
        const realSet = el.setAttribute.bind(el);
        el.setAttribute = (k, v) => { if (k === 'content') el.textContent = v; else realSet('data-' + k, v); };
        return el;
      }
      return realCreate(tag);
    };
    try { ${script} } catch (e) { root.textContent = 'script error: ' + e.message; }
  <\/script></body></html>`;
}

// The other side of the conversation: messages the iframe posts up to us.
window.addEventListener('message', async (event) => {
  const data = event.data || {};
  if (!data.type) return;

  if (data.type === 'ui-lifecycle-iframe-ready') {
    log('in', 'ui-lifecycle-iframe-ready');
    // If this resource had render data, the page is ready to receive it.
    if (pendingRenderData) {
      window.__frame.contentWindow.postMessage(
        {type: 'ui-lifecycle-iframe-render-data', payload: {renderData: pendingRenderData}}, '*');
      log('out', 'render-data → iframe');
    }
    return;
  }

  if (data.type === 'ui-size-change') {
    const {height} = data.payload || {};
    if (height && window.__frame) window.__frame.style.height = height + 'px';
    log('in', `ui-size-change height=${height}`);
    return;
  }

  // A UI action: the iframe wants the host to DO something (call a tool, open a
  // link, run a prompt). We act, then post the result back keyed by messageId.
  if (['tool', 'link', 'prompt'].includes(data.type)) {
    log('in', `${data.type} ${JSON.stringify(data.payload)}`);
    let response = null, error = null;
    try {
      if (data.type === 'tool') {
        const r = await fetch('/demo/call/' + data.payload.toolName, {
          method: 'POST', headers: {'content-type': 'application/json'},
          body: JSON.stringify(data.payload.params || {}),
        });
        response = await r.json();
      } else if (data.type === 'link') {
        window.open(data.payload.url, '_blank');
        response = {opened: data.payload.url};
      } else if (data.type === 'prompt') {
        response = {note: 'a real client would run this prompt: ' + data.payload.prompt};
      }
    } catch (e) { error = String(e); }

    if (data.messageId && window.__frame) {
      window.__frame.contentWindow.postMessage(
        {type: 'ui-message-response', messageId: data.messageId, payload: {response, error}}, '*');
      log('out', `ui-message-response → ${data.messageId.slice(0, 8)}`);
    }
  }
});
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Shared iframe-side helper, inlined into both iframe pages.
# ---------------------------------------------------------------------------

_MCP_UI_CLIENT_JS = r"""
// The iframe side of the MCP-UI conversation. Every page loaded into a host
// frame speaks this little protocol over window.parent.postMessage.

// Announce readiness, then report our size once so the host can fit us.
function mcpUiInit() {
  window.parent.postMessage({type: 'ui-lifecycle-iframe-ready'}, '*');
  reportSize();
  // Dynamic sizing: if our content grows or shrinks, tell the host again.
  const ro = new ResizeObserver(reportSize);
  ro.observe(document.documentElement);
}

function reportSize() {
  const height = document.documentElement.scrollHeight;
  window.parent.postMessage({type: 'ui-size-change', payload: {height}}, '*');
}

// Send an action to the host and (optionally) await its response. Each message
// carries a unique id so the reply can be matched to this exact request.
function sendMcpMessage(type, payload) {
  const messageId = (crypto.randomUUID && crypto.randomUUID()) ||
    String(Date.now()) + Math.random();
  return new Promise((resolve, reject) => {
    if (!window.parent || window.parent === window) {
      console.log('[MCP-UI] no host frame; would have sent', {type, payload});
      reject(new Error('no host frame')); return;
    }
    function onMessage(event) {
      const d = event.data || {};
      if (d.type !== 'ui-message-response' || d.messageId !== messageId) return;
      window.removeEventListener('message', onMessage);
      if (d.payload && d.payload.error) reject(d.payload.error);
      else resolve(d.payload ? d.payload.response : undefined);
    }
    window.addEventListener('message', onMessage);
    window.parent.postMessage({type, messageId, payload}, '*');
  });
}

// Wait for the host to hand us our initial render data (view_entry uses this).
function waitForRenderData() {
  return new Promise((resolve) => {
    function onMessage(event) {
      const d = event.data || {};
      if (d.type !== 'ui-lifecycle-iframe-render-data') return;
      window.removeEventListener('message', onMessage);
      resolve(d.payload ? d.payload.renderData : null);
    }
    window.addEventListener('message', onMessage);
    // Also announce readiness — the host sends render data once it hears this.
    window.parent.postMessage({type: 'ui-lifecycle-iframe-ready'}, '*');
  });
}
"""


# ---------------------------------------------------------------------------
# The journal-viewer iframe page.
# ---------------------------------------------------------------------------

JOURNAL_VIEWER = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Your journal</title>
<style>
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1a1a2e; background: #f7f6fb; padding: 1.25rem; }
  h1 { font-size: 1.5rem; margin: 0 0 .25rem; }
  p.count { color: #6b6b8a; margin: 0 0 1rem; }
  .entry { background: #fff; border: 1px solid #e5e3f0; border-radius: 10px; padding: 1rem;
    margin-bottom: .75rem; }
  .entry h2 { font-size: 1.05rem; margin: 0 0 .35rem; }
  .entry p { margin: 0 0 .6rem; color: #43435e; }
  button { background: #4f46e5; color: #fff; border: 0; border-radius: 7px; padding: .45rem .8rem;
    cursor: pointer; font-size: .85rem; }
  button:hover { background: #4038c7; }
</style>
</head>
<body>
<div id="root">
  <h1>Your journal</h1>
  <p class="count" id="count"></p>
  <div id="entries"></div>
</div>
<script>
__MCP_UI_CLIENT__

const entries = __ENTRIES__;
document.getElementById('count').textContent =
  entries.length + (entries.length === 1 ? ' entry' : ' entries');

const list = document.getElementById('entries');
for (const entry of entries) {
  const card = document.createElement('div');
  card.className = 'entry';
  const h = document.createElement('h2'); h.textContent = entry.title;
  const p = document.createElement('p'); p.textContent = entry.content;
  const btn = document.createElement('button'); btn.textContent = 'View entry';
  // Clicking asks the HOST to call the view_entry tool for us — an iframe can't
  // reach the server itself, so it posts the request up and the host acts.
  btn.onclick = () => sendMcpMessage('tool', {toolName: 'view_entry', params: {id: entry.id}})
    .catch((e) => console.log('tool call rejected', e));
  card.append(h, p, btn);
  list.appendChild(card);
}

mcpUiInit();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# The entry-viewer iframe page — driven entirely by render data.
# ---------------------------------------------------------------------------

ENTRY_VIEWER = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Entry</title>
<style>
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1a1a2e; background: #f7f6fb; padding: 1.5rem; }
  h1 { font-size: 1.5rem; margin: 0 0 .5rem; }
  .meta { color: #6b6b8a; font-size: .85rem; margin: 0 0 1rem; }
  .body { background: #fff; border: 1px solid #e5e3f0; border-radius: 10px; padding: 1rem; line-height: 1.55; }
</style>
</head>
<body>
<div id="root">Loading…</div>
<script>
__MCP_UI_CLIENT__

// No fetch, no id in the URL: the host handed us the entry as render data.
waitForRenderData().then((data) => {
  const root = document.getElementById('root');
  const entry = data && data.entry;
  if (!entry) { root.textContent = 'No render data received.'; return; }
  root.innerHTML = '';
  const h = document.createElement('h1'); h.textContent = entry.title;
  const meta = document.createElement('p'); meta.className = 'meta';
  meta.textContent = [entry.mood, entry.location, entry.weather].filter(Boolean).join(' · ');
  const body = document.createElement('div'); body.className = 'body';
  body.textContent = entry.content;
  root.append(h, meta, body);
  reportSize();
});
</script>
</body>
</html>
"""

# Inline the shared client helper into both iframe pages.
JOURNAL_VIEWER = JOURNAL_VIEWER.replace("__MCP_UI_CLIENT__", _MCP_UI_CLIENT_JS)
ENTRY_VIEWER = ENTRY_VIEWER.replace("__MCP_UI_CLIENT__", _MCP_UI_CLIENT_JS)
