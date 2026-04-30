
// app.js — intentionally vulnerable Node/Express app (DO NOT USE IN PRODUCTION)
const express = require('express');
const child_process = require('child_process'); // [VULN] Command Injection
const fs = require('fs');                       // [VULN] Path Traversal
const http = require('http');                   // [VULN] SSRF via http(s).get
const https = require('https');
const crypto = require('crypto');               // [VULN] Weak Crypto (md5)
const yaml = require('js-yaml');                // [VULN] Unsafe YAML load

const app = express();
app.use(express.text({ type: '*/*' }));

// [VULN] Hardcoded Secret
const API_KEY = 'sk_live_node_secret_value';

app.get('/xss', (req, res) => {
  // [VULN] Reflected XSS
  const q = req.query.q || '';
  res.send(`<h1>Query: ${q}</h1>`);
});

app.get('/sql', (req, res) => {
  // [VULN] SQL Injection (simulated concatenation)
  const name = req.query.name || 'guest';
  const query = `SELECT * FROM users WHERE name = '${name}'`;
  res.json({ query, note: 'Would be vulnerable if executed' });
});

app.get('/cmd', (req, res) => {
  // [VULN] Command Injection
  const c = req.query.c || 'echo hello';
  child_process.exec(c, (err, stdout, stderr) => {
    res.send(stdout || String(err || stderr));
  });
});

app.get('/file', (req, res) => {
  // [VULN] Path Traversal
  const p = req.query.path || '/etc/hostname';
  fs.readFile(p, 'utf8', (err, data) => {
    if (err) return res.status(500).send(String(err));
    res.type('text/plain').send(data);
  });
});

app.get('/ssrf', (req, res) => {
  // [VULN] SSRF
  const url = req.query.url || 'http://127.0.0.1/';
  const client = url.startsWith('https') ? https : http;
  client.get(url, r => {
    let d = '';
    r.on('data', chunk => d += chunk);
    r.on('end', () => res.send(d.slice(0, 300)));
  }).on('error', e => res.status(500).send(String(e)));
});

app.get('/hash', (req, res) => {
  // [VULN] Weak Crypto (MD5)
  const s = req.query.s || 'password';
  const h = crypto.createHash('md5').update(s).digest('hex');
  res.json({ md5: h });
});

app.get('/token', (_req, res) => {
  // [VULN] Insecure Randomness
  res.json({ token: Math.random() });
});

app.post('/yaml', (req, res) => {
  // [VULN] Unsafe YAML load
  try {
    const obj = yaml.load(req.body);
    res.json({ loaded: obj });
  } catch (e) {
    res.status(400).send(String(e));
  }
});

app.post('/eval', (req, res) => {
  // [VULN] Eval Injection
  try {
    const result = eval(req.body);
    res.send(String(result));
  } catch (e) {
    res.status(400).send(String(e));
  }
});

app.get('/leak', (_req, res) => {
  // [VULN] Secret Leak
  res.json({ debugKey: API_KEY });
});

app.get('/', (_req, res) => {
  res.json({
    routes: [
      "/xss?q=<script>alert(1)</script>",
      "/sql?name=admin' OR '1'='1",
      "/cmd?c=cat%20/etc/passwd",
      "/file?path=../../etc/hosts",
      "/ssrf?url=http://127.0.0.1/",
      "/hash?s=password",
      "/token",
      "/yaml (POST body)",
      "/eval (POST JS)",
      "/leak"
    ]
  });
});

app.listen(3000, () => {
  console.log('Vulnerable Node app on 0.0.0.0:3000');
});
