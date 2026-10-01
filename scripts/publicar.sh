#!/usr/bin/env bash
# Publica o Beaba.ia de teste em beaba.cria.pro (VPS da Hostinger).  Uso: scripts/publicar.sh
# O .env e a pasta dados/ (banco) ficam só no servidor e nunca são sobrescritos.
set -euo pipefail
SERVIDOR=root@179.198.121.91
PASTA=/var/www/beaba
cd "$(dirname "$0")/.."

rsync -az --delete \
  --exclude node_modules --exclude .git --exclude .env --exclude dados --exclude scripts/mascote \
  ./ "$SERVIDOR:$PASTA/"
ssh "$SERVIDOR" "cd $PASTA && npm ci --omit=dev --silent && (pm2 reload beaba --update-env || pm2 start servidor.mjs --name beaba --cwd $PASTA) && pm2 save >/dev/null"
sleep 2
curl -s -o /dev/null -w 'beaba.cria.pro: %{http_code}\n' https://beaba.cria.pro/
