// Banco de dados do Beaba.ia: um arquivo SQLite no próprio servidor (variável BEABA_DB).
// Sem BEABA_DB (na Vercel, por exemplo) nada é gravado aqui e as funções devolvem vazio.
// ponytail: SQLite num arquivo só. Aguenta com folga a rodada de testes; trocar por Postgres se houver
// mais de um servidor escrevendo ou se o admin ficar lento com dezenas de milhares de respostas.
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

let db = null;
if (process.env.BEABA_DB) {
  const { default: Database } = await import('better-sqlite3');
  mkdirSync(dirname(process.env.BEABA_DB), { recursive: true });
  db = new Database(process.env.BEABA_DB);
  db.pragma('journal_mode = WAL');
  db.exec(`
    create table if not exists respostas (
      id integer primary key,
      sessao text not null,
      criada_em text not null default (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
      pergunta text not null,
      resposta text not null,
      fontes text not null default '[]',
      cartoes text not null default '',
      tipo_cancer text not null default '',
      tipo_duvida text not null default '',
      quem text not null default '',
      sentimento text not null default '',
      reacao text not null default '',
      modelo text not null default '',
      tokens_entrada integer not null default 0,
      tokens_cache_lido integer not null default 0,
      tokens_cache_escrito integer not null default 0,
      tokens_saida integer not null default 0,
      buscas_web integer not null default 0,
      tokens_jev integer not null default 0,
      custo_usd real not null default 0,
      ms integer not null default 0
    );
    create index if not exists respostas_sessao on respostas (sessao, id);
    create table if not exists feedback (
      id integer primary key,
      resposta_id integer not null references respostas (id),
      criado_em text not null default (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
      voto text not null default '',
      comentario text not null default ''
    );
    create table if not exists reacoes (
      nome text primary key,
      status text not null default '',
      nota text not null default '',
      atualizado_em text not null default (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
    );
  `);
}

export const temBanco = () => Boolean(db);

const CAMPOS = ['sessao', 'pergunta', 'resposta', 'fontes', 'cartoes', 'tipo_cancer', 'tipo_duvida', 'quem', 'sentimento', 'reacao',
  'modelo', 'tokens_entrada', 'tokens_cache_lido', 'tokens_cache_escrito', 'tokens_saida', 'buscas_web', 'tokens_jev', 'custo_usd', 'ms'];

export function gravarResposta(r) {
  if (!db) return null;
  const info = db.prepare(`insert into respostas (${CAMPOS.join(', ')}) values (${CAMPOS.map((c) => '@' + c).join(', ')})`).run(r);
  return Number(info.lastInsertRowid);
}

// Um registro por resposta: o voto e o comentário chegam em momentos diferentes e se completam.
export function gravarFeedback({ id, voto, comentario }) {
  if (!db || !db.prepare('select 1 from respostas where id = ?').get(id)) return false;
  const atual = db.prepare('select id from feedback where resposta_id = ?').get(id);
  if (atual) {
    db.prepare("update feedback set voto = coalesce(nullif(?, ''), voto), comentario = coalesce(nullif(?, ''), comentario) where id = ?").run(voto, comentario, atual.id);
  } else {
    db.prepare('insert into feedback (resposta_id, voto, comentario) values (?, ?, ?)').run(id, voto, comentario);
  }
  return true;
}

export function tudoParaAdmin() {
  if (!db) return { respostas: [], reacoes: [] };
  // ponytail: manda as 5.000 respostas mais recentes e o admin filtra no navegador. Paginar no servidor quando passar disso.
  const respostas = db.prepare(`
    select r.*, coalesce(f.voto, '') as voto, coalesce(f.comentario, '') as comentario
    from respostas r left join feedback f on f.resposta_id = r.id
    order by r.id desc limit 5000`).all();
  return { respostas, reacoes: listarReacoes() };
}

export const listarReacoes = () => (db ? db.prepare('select * from reacoes').all() : []);

export function gravarReacao({ nome, status, nota }) {
  if (!db) return false;
  db.prepare(`insert into reacoes (nome, status, nota) values (?, ?, ?)
    on conflict (nome) do update set status = excluded.status, nota = excluded.nota, atualizado_em = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')`).run(nome, status, nota);
  return true;
}
