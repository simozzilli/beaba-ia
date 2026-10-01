// Servidor do Beaba.ia fora da Vercel (VPS ou computador):  node servidor.mjs
// Lê as variáveis do arquivo .env, se existir. Serve o chat, o admin e a página de aprovação das reações.
import http from 'node:http';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { timingSafeEqual } from 'node:crypto';

if (existsSync(new URL('.env', import.meta.url))) process.loadEnvFile(new URL('.env', import.meta.url));
const { default: chat } = await import('./api/chat.js');
const banco = await import('./api/_banco.js');

const PORTA = process.env.PORT || 3040;
const SENHA = process.env.BEABA_ADMIN_SENHA || '';

// Só estes arquivos saem para a internet. O resto da pasta (código, .env, banco) não é servido.
const PAGINAS = {
  '/': ['index.html', 'text/html; charset=utf-8'],
  '/reacoes': ['reacoes.html', 'text/html; charset=utf-8'],
  '/mascote.html': ['reacoes.html', 'text/html; charset=utf-8'],
  '/mascote.svg': ['mascote.svg', 'image/svg+xml'],
  '/mascote.js': ['mascote.js', 'text/javascript; charset=utf-8'],
  '/Logo.svg': ['Logo.svg', 'image/svg+xml'],
  '/robots.txt': [null, 'text/plain'],
};

const json = (res, codigo, obj) => { res.writeHead(codigo, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); };

async function corpo(req) {
  let texto = '';
  for await (const pedaco of req) { texto += pedaco; if (texto.length > 100_000) break; }
  try { return JSON.parse(texto || '{}'); } catch { return {}; }
}

function autorizado(req) {
  const [, b64] = (req.headers.authorization || '').split(' ');
  const senha = Buffer.from(b64 || '', 'base64').toString().split(':').slice(1).join(':');
  const a = Buffer.from(senha), b = Buffer.from(SENHA);
  return SENHA && a.length === b.length && timingSafeEqual(a, b);
}

const texto = (v, max) => String(v ?? '').slice(0, max);

http.createServer(async (req, res) => {
  const caminho = req.url.split('?')[0];
  try {
    if (caminho === '/api/chat') {
      req.body = await corpo(req);
      res.status = (codigo) => { res.statusCode = codigo; return res; };
      res.json = (obj) => json(res, res.statusCode, obj);
      return await chat(req, res);
    }
    if (caminho === '/api/feedback' && req.method === 'POST') {
      const b = await corpo(req);
      const voto = ['up', 'down'].includes(b.voto) ? b.voto : '';
      return json(res, 200, { ok: banco.gravarFeedback({ id: Number(b.id), voto, comentario: texto(b.comentario, 2000) }) });
    }
    if (caminho === '/api/reacoes') {
      if (req.method === 'GET') return json(res, 200, banco.listarReacoes());
      const b = await corpo(req);
      const status = ['aprovada', 'ajustar'].includes(b.status) ? b.status : '';
      return json(res, 200, { ok: banco.gravarReacao({ nome: texto(b.nome, 40), status, nota: texto(b.nota, 1000) }) });
    }
    if (caminho === '/admin' || caminho === '/api/admin/dados') {
      if (!autorizado(req)) {
        res.writeHead(401, { 'WWW-Authenticate': 'Basic realm="Beaba.ia admin", charset="UTF-8"' });
        return res.end('Acesso restrito');
      }
      if (caminho === '/api/admin/dados') return json(res, 200, banco.tudoParaAdmin());
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      return res.end(await readFile(new URL('admin.html', import.meta.url)));
    }
    const pagina = PAGINAS[caminho];
    if (!pagina) { res.writeHead(404); return res.end('não encontrado'); }
    res.writeHead(200, { 'Content-Type': pagina[1], 'X-Robots-Tag': 'noindex, nofollow' });
    res.end(pagina[0] ? await readFile(new URL(pagina[0], import.meta.url)) : 'User-agent: *\nDisallow: /\n');
  } catch (err) {
    console.error('[servidor]', caminho, err.message);
    if (!res.headersSent) res.writeHead(500);
    res.end();
  }
}).listen(PORTA, process.env.HOST || '0.0.0.0', () => console.log(`Beaba.ia em http://localhost:${PORTA}` + (banco.temBanco() ? '' : ' (sem banco: defina BEABA_DB)')));
