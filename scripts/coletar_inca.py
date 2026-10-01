#!/usr/bin/env python3
"""Baixa as páginas do INCA para a população e gera api/_inca.js.

Rodar de novo quando o INCA atualizar o conteúdo:  python3 scripts/coletar_inca.py
O texto é guardado sem alteração (licença CC BY-ND 3.0 do portal do INCA).
"""
import html, json, re, sys, time, urllib.request
from pathlib import Path

BASE = "https://www.gov.br/inca/pt-br"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
FAQ = "acesso-a-informacao/perguntas-frequentes"
GERAIS = [
    "cancer/o-que-e-cancer", "cancer/como-surge-o-cancer", "cancer/tratamento",
    "cancer/tratamento/cirurgia", "cancer/tratamento/quimioterapia", "cancer/tratamento/radioterapia",
    "cancer/tratamento/transplante-de-medula-ossea", "cancer/tratamento/cuidados-paliativos",
    "cancer/orientacoes-aos-pacientes-e-familiares",
    f"{FAQ}/cancer", f"{FAQ}/quimioterapia", f"{FAQ}/radioterapia", f"{FAQ}/transplante-de-medula-ossea",
    f"{FAQ}/direitos-sociais-da-pessoa-com-cancer", f"{FAQ}/hpv", f"{FAQ}/estudos-clinicos",
    "causas-e-prevencao-do-cancer/como-prevenir-o-cancer", "causas-e-prevencao-do-cancer/o-que-causa-o-cancer",
    "causas-e-prevencao-do-cancer/alimentacao", "causas-e-prevencao-do-cancer/atividade-fisica",
    "causas-e-prevencao-do-cancer/bebidas-alcoolicas", "causas-e-prevencao-do-cancer/tabagismo",
    "causas-e-prevencao-do-cancer/hereditariedade", "causas-e-prevencao-do-cancer/hpv-e-outras-infeccoes",
    "causas-e-prevencao-do-cancer/exposicao-solar", "causas-e-prevencao-do-cancer/peso-corporal",
    "causas-e-prevencao-do-cancer/mitos-e-verdades",
]
# O Beaba não abre a conversa com número de casos e mortes.
PULAR = re.compile(r"estat[íi]stica", re.I)


def baixar(url):
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if getattr(e, "code", 0) == 404:
                return ""
            time.sleep(2 * (tentativa + 1))
    return ""


def texto(h):
    h = re.sub(r"<(script|style).*?</\1>|<[^>]*$", "", h, flags=re.S)
    h = re.sub(r"</t[dh]>\s*<t[dh][^>]*>", " | ", h)
    h = re.sub(r"<li[^>]*>", "\n- ", h)
    h = re.sub(r"</(p|div|tr|h\d|ul|ol|table)>|<br\s*/?>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "", h)).replace("\xa0", " ")
    linhas = (re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n"))
    return "\n".join(l for l in linhas if l and l != "-")


def miolo(h):
    i, j = h.find('id="content-core"'), h.find('id="viewlet-below-content-body"')
    return h[i:j] if i > 0 else ""


def secoes(h):
    m = miolo(h)
    partes = re.split(r'<a class="toggle[^"]*"[^>]*>(.*?)</a>', m, flags=re.S)
    if len(partes) > 1:
        pares = zip(partes[1::2], partes[2::2])
        return [{"titulo": texto(t), "texto": texto(c)} for t, c in pares]
    return [{"titulo": "", "texto": texto(m[m.find(">") + 1:])}]


def pagina(caminho, sufixo=""):
    url = f"{BASE}/{caminho}"
    h = baixar(url + sufixo) or baixar(url)
    if not h:
        return None
    titulo = texto(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1))
    if sufixo:  # o h1 da aba é "Versão para população"; o nome do câncer está na página mãe
        titulo = texto(re.search(r"<h1[^>]*>(.*?)</h1>", baixar(url), re.S).group(1))
    atual = re.search(r'documentModified.*?class="value">([\d/]+)', h, re.S)
    ss = [s for s in secoes(h) if len(s["texto"]) > 80 and not PULAR.search(s["titulo"])]
    if not ss:
        return None
    return {"id": "inca-" + ("faq-" if FAQ in caminho else "") + caminho.split("/")[-1], "titulo": titulo, "fonte": "INCA", "url": url,
            "atualizado": atual.group(1) if atual else "", "secoes": ss}


def main():
    indice = baixar(f"{BASE}/assuntos/cancer/tipos")
    tipos = sorted(set(re.findall(r'assuntos/(cancer/tipos/[a-z0-9-]+)"', indice)) - {"cancer/tipos/tipos-de-cancer"})
    base = []
    for caminho, sufixo in [("assuntos/" + t, "/versao-para-populacao") for t in tipos] + [(g if g.startswith(FAQ) else "assuntos/" + g, "") for g in GERAIS]:
        v = pagina(caminho, sufixo)
        print(("ok  " if v else "FALHOU ") + caminho, len(json.dumps(v, ensure_ascii=False)) if v else "", file=sys.stderr)
        if v:
            base.append(v)
        time.sleep(0.5)
    saida = Path(__file__).resolve().parent.parent / "api" / "_inca.js"
    saida.write_text("// GERADO por scripts/coletar_inca.py. Não editar à mão.\nexport default "
                     + json.dumps(base, ensure_ascii=False, indent=1) + ";\n")
    print(f"{len(base)} verbetes em {saida}", file=sys.stderr)


if __name__ == "__main__":
    main()
