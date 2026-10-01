// Servidor local para testar sem a Vercel:  ANTHROPIC_API_KEY=... npm run dev  → http://localhost:3040
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import handler from '../api/chat.js';

const TIPOS = { html: 'text/html; charset=utf-8', js: 'text/javascript', svg: 'image/svg+xml', png: 'image/png', css: 'text/css' };

http.createServer(async (req, res) => {
  if (req.url === '/api/chat') {
    let corpo = '';
    for await (const pedaco of req) corpo += pedaco;
    try { req.body = JSON.parse(corpo || '{}'); } catch { req.body = {}; }
    res.status = (codigo) => { res.statusCode = codigo; return res; };
    res.json = (obj) => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(obj)); };
    return handler(req, res);
  }
  const caminho = req.url.split('?')[0].replace(/\.\./g, '');
  try {
    const arquivo = await readFile(new URL('..' + (caminho === '/' ? '/index.html' : caminho), import.meta.url));
    res.writeHead(200, { 'Content-Type': TIPOS[caminho.split('.').pop()] || TIPOS.html });
    res.end(arquivo);
  } catch {
    res.writeHead(404).end('não encontrado');
  }
}).listen(process.env.PORT || 3040, () => console.log('Beaba em http://localhost:' + (process.env.PORT || 3040)));
