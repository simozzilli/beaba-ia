"""Vetoriza o urso do Beaba (Urso2.png, 500x558) em partes separadas e mede cada contorno no original."""
import json, numpy as np, potrace
from collections import deque
from PIL import Image, ImageFilter

S = 4  # ampliação para traçar com precisão de subpixel
src = Image.open('Urso2.png').convert('RGBA')
W0, H0 = src.size
# premultiplica para o LANCZOS não puxar cor de pixel transparente
arr = np.array(src).astype(float); al = arr[..., 3:4] / 255
pm = Image.fromarray(np.concatenate([arr[..., :3] * al, arr[..., 3:4]], -1).astype(np.uint8), 'RGBA')
up = np.array(pm.resize((W0 * S, H0 * S), Image.LANCZOS)).astype(float)
A = up[..., 3] / 255
RGB = up[..., :3] / np.maximum(A[..., None], 1e-6)
H, W = A.shape

COR = {'marrom': (96, 56, 19), 'amarelo': (248, 195, 17), 'branco': (255, 255, 255), 'verde': (50, 192, 197),
       'azul': (226, 243, 250), 'rosa': (244, 175, 189), 'vermelho': (235, 66, 71)}
hexa = lambda n: '#%02x%02x%02x' % COR[n]

def dist(n):
    return ((RGB - np.array(COR[n], float)) ** 2).sum(-1)

dentro = A >= 0.5
dm = dist('marrom')
claro = np.minimum.reduce([dist(n) for n in ('amarelo', 'branco', 'verde', 'azul', 'vermelho')])
MARROM = dentro & (dm < claro)
NAO_MARROM = dentro & ~MARROM

def inundar(mask, sx, sy):
    """região conexa de mask a partir da semente (coordenadas da imagem original)"""
    sx, sy = int(sx * S), int(sy * S)
    assert mask[sy, sx], (sx / S, sy / S)
    out = np.zeros_like(mask); out[sy, sx] = True; q = deque([(sy, sx)])
    while q:
        y, x = q.popleft()
        for u, v in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= u < H and 0 <= v < W and mask[u, v] and not out[u, v]:
                out[u, v] = True; q.append((u, v))
    return out

def curvas(mask):
    ys, xs = np.nonzero(mask); pad = 8
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    sub = mask[y0:ys.max() + pad, x0:xs.max() + pad]
    res = []
    for c in potrace.Bitmap(~sub).trace(turdsize=20, alphamax=1.1, opttolerance=0.4):
        P = lambda p: ((p.x + x0) / S, (p.y + y0) / S)
        segs = [('M', P(c.start_point))]
        for s in c.segments:
            segs.append(('L', P(s.c), P(s.end_point)) if s.is_corner else ('C', P(s.c1), P(s.c2), P(s.end_point)))
        res.append(segs)
    return res

def area_bbox(segs):
    pts = [p for s in segs for p in s[1:]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))

def d_de(segs):
    f = lambda p: f'{p[0]:.1f} {p[1]:.1f}'
    out = []
    for s in segs:
        if s[0] == 'M': out.append('M' + f(s[1]))
        elif s[0] == 'L': out.append('L' + f(s[1]) + ' ' + f(s[2]))
        else: out.append('C' + ' '.join(f(p) for p in s[1:]))
    return ''.join(out) + 'Z'

def contorno(mask):
    """só a curva de fora (ignora buracos como olhos e pontilhados)"""
    return max(curvas(mask), key=area_bbox)

def amostras(segs, n=6):
    pts = []; cur = segs[0][1]
    for s in segs[1:]:
        if s[0] == 'L':
            for a, b in ((cur, s[1]), (s[1], s[2])):
                for t in np.linspace(0, 1, n, endpoint=False): pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        else:
            p0, p1, p2, p3 = cur, s[1], s[2], s[3]
            for t in np.linspace(0, 1, n, endpoint=False):
                m = 1 - t
                pts.append(tuple(m**3 * p0[i] + 3 * m * m * t * p1[i] + 3 * m * t * t * p2[i] + t**3 * p3[i] for i in (0, 1)))
        cur = s[-1]
    return np.array(pts)

def largura_do_traco(segs, mask):
    """mediana da espessura da faixa marrom, andando para fora a partir da borda do preenchimento"""
    P = amostras(segs); N = len(P); ds = []
    for i in range(0, N, 3):
        t = P[(i + 1) % N] - P[i - 1]; n = np.array([t[1], -t[0]]); L = np.hypot(*n)
        if L < 1e-6: continue
        n /= L
        q = P[i] - n * 1.0
        if not (0 <= int(q[1] * S) < H and 0 <= int(q[0] * S) < W and mask[int(q[1] * S), int(q[0] * S)]): n = -n  # normal para fora
        d = 0.0
        while d < 20:
            x, y = P[i] + n * (d + 0.6)
            xi, yi = int(x * S), int(y * S)
            if not (0 <= yi < H and 0 <= xi < W) or not MARROM[yi, xi]: break
            d += 0.25
        if 2 < d < 19: ds.append(d + 0.35)
    return float(np.median(ds)) if ds else 0.0

def desloca(mask, dx, dy, passos=6):
    """une a máscara com cópias deslocadas (esconde a parte de trás de outra peça)"""
    out = mask.copy()
    for k in range(1, passos + 1):
        out |= np.roll(np.roll(mask, int(dy * S * k / passos), 0), int(dx * S * k / passos), 1)
    return out

def dilatar(mask, r):
    """dilatação ~circular (octógono) de r pixels da imagem original"""
    out = mask.copy()
    for k in range(int(round(r * S))):
        viz = [np.roll(out, 1, 0), np.roll(out, -1, 0), np.roll(out, 1, 1), np.roll(out, -1, 1)]
        if k % 2: viz += [np.roll(np.roll(out, a, 0), b, 1) for a in (1, -1) for b in (1, -1)]
        out = out | np.logical_or.reduce(viz)
    return out

def fechar(mask, janela, r):
    """fecha fendas mais finas que 2r dentro da janela (x0, y0, x1, y1)"""
    x0, y0, x1, y1 = [int(v * S) for v in janela]
    sub = np.zeros_like(mask); sub[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    f = ~dilatar(~dilatar(sub, r) , r)
    out = mask.copy(); out[y0 + 8:y1 - 8, x0 + 8:x1 - 8] |= f[y0 + 8:y1 - 8, x0 + 8:x1 - 8]
    return out

def linhas_cheias(mask):
    out = mask.copy()
    for y in np.nonzero(mask.any(1))[0]:
        xs = np.nonzero(mask[y])[0]; out[y, xs.min():xs.max() + 1] = True
    return out

def circulo(mask_borda):
    ys, xs = np.nonzero(mask_borda); x = xs / S; y = ys / S
    M = np.c_[2 * x, 2 * y, np.ones_like(x)]; b = x * x + y * y
    cx, cy, c = np.linalg.lstsq(M, b, rcond=None)[0]
    return cx, cy, np.sqrt(c + cx * cx + cy * cy)

P = {}  # peças

# ── peças com contorno: preenchimento traçado na borda exata + traço medido ──
MASC = {}
SIL_E = ~dilatar(~dentro, 9.7)   # silhueta do urso encolhida de um traço: o que cresce aqui dentro não vaza para fora

def peca(nome, cor, sx, sy, cresce=None, frente=None, tampar=None, fenda=None):
    """cresce = máscara candidata da parte escondida; frente = interior da(s) peça(s) que ficam por cima"""
    m = inundar(NAO_MARROM, sx, sy)
    if tampar:
        x0, y0, x1, y1 = [int(v * S) for v in tampar]; m[y0:y1, x0:x1] = True
    if fenda: m = fechar(m, fenda, 4)
    MASC[nome] = m
    if cresce is not None:
        # dentro da peça da frente pode crescer à vontade (o traço dela cobre); na faixa de contorno entre as duas,
        # só onde não vaza para fora da silhueta
        ponte = dilatar(frente, 10.5) & dilatar(m, 10.5) & SIL_E
        m = m | (cresce(m) & (frente | ponte))
    P[nome] = dict(d=d_de(contorno(m)), fill=hexa(cor), w=9.7)
    print(nome)

def elipse(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx / S - cx) / rx) ** 2 + ((yy / S - cy) / ry) ** 2 <= 1

peca('capuz', 'amarelo', 200, 35)
CABECA = linhas_cheias(MASC['capuz'])
peca('rosto', 'branco', 250, 200)
peca('orelha-e', 'branco', 55, 120, cresce=lambda m: desloca(m, 20, 12) | elipse(76, 112, 42, 46), frente=CABECA)
peca('orelha-d', 'branco', 444, 120, cresce=lambda m: desloca(m, -20, 12) | elipse(424, 112, 42, 46), frente=CABECA)
# roupinha sobe arredondada por trás da cabeça (gola): quando a cabeça inclina, aparece roupa e não um vão
peca('corpo', 'verde', 200, 440, cresce=lambda m: desloca(m, 0, -22) | elipse(250, 408, 99, 62), frente=CABECA,
     tampar=(272, 405, 333, 454), fenda=(322, 414, 356, 450))
CORPO = MASC['corpo']
ATRAS = CORPO | CABECA
peca('braco-e', 'verde', 128, 420, cresce=lambda m: elipse(162, 412, 20, 20), frente=ATRAS)
peca('braco-d', 'verde', 371, 420, cresce=lambda m: elipse(338, 412, 20, 20), frente=ATRAS)
peca('perna-e', 'verde', 188, 510, cresce=lambda m: desloca(m, 0, -18), frente=CORPO)
peca('perna-d', 'verde', 310, 510, cresce=lambda m: desloca(m, 0, -18), frente=CORPO)

# coração: as duas metades vermelhas são separadas pelo cateter; junta e tampa o miolo
m = inundar(NAO_MARROM, 290, 432) | inundar(NAO_MARROM, 314, 419)
segs_h = contorno(m)
wh = 6.0
mh = m.copy()
for x0, y0, x1, y1 in ((296, 424, 312, 441), (308, 424.5, 320, 432.5)):  # tampa o miolo e a fenda do cateter
    mh[int(y0 * S):int(y1 * S), int(x0 * S):int(x1 * S)] = True
mh = fechar(mh, (312, 418, 334, 440), 3.3)
mh = fechar(mh, (288, 410, 316, 430), 3)
P['coracao'] = dict(d=d_de(contorno(mh)), fill=hexa('vermelho'), w=5.2); print(f'coracao    traço {wh:.2f}px')

# ── detalhes marrons sem contorno: traçados como forma cheia ──
comps = json.load(open('comps.json'))
for i, c in enumerate(comps): c['i'] = i
LAB = np.load('lab.npy')
def marrons(nome, filtro):
    ds = []
    for c in comps:
        if c['c'] == 'marrom' and c['n'] < 2000 and filtro(c):
            ys, xs = np.nonzero(LAB == c['i'])
            sub = inundar(MARROM, xs[0] + 0.5, ys[0] + 0.5)
            cs = curvas(sub)
            if len(cs) != 1 and c['n'] < 200: print('  curvas', len(cs), [round(area_bbox(x), 1) for x in cs], c)
            ds += [d_de(s) for s in cs]
    P[nome] = dict(d=' '.join(ds), fill=hexa('marrom')); print(nome, len(ds), 'formas')
cx_ = lambda c: (c['x0'] + c['x1']) / 2; cy_ = lambda c: (c['y0'] + c['y1']) / 2
marrons('pontos-capuz', lambda c: 80 <= c['n'] <= 110 and cy_(c) < 320)
anel = inundar(MARROM, 250, 115.5)
sobra = anel & ~dilatar(MASC['rosto'], 9.7 - 1.5) & (np.mgrid[0:H, 0:W][0] > 150 * S)
extras = [d_de(c) for c in curvas(sobra) if area_bbox(c) > 30]
P['pontos-capuz']['d'] += ' ' + ' '.join(extras); print('pontos encostados no rosto:', len(extras))
marrons('pontos-corpo', lambda c: 80 <= c['n'] <= 110 and cy_(c) > 400)
marrons('arco-orelha-e', lambda c: c['n'] == 538 and cx_(c) < 250)
marrons('arco-orelha-d', lambda c: c['n'] == 538 and cx_(c) > 250)
marrons('nariz-boca', lambda c: 480 <= c['n'] <= 490)

# ── formas simples, pelas medidas ──
def bbox(i):
    c = comps[i]; return (c['x0'] + c['x1'] + 1) / 2, (c['y0'] + c['y1'] + 1) / 2, (c['x1'] - c['x0'] + 1) / 2, (c['y1'] - c['y0'] + 1) / 2
P['medidas'] = {k: [round(v, 2) for v in bbox(i)] for k, i in dict(anel_e=697, anel_d=701, branco_e=737, branco_d=745, pupila_e=824, pupila_d=833,
               bochecha_e=954, bochecha_d=956, focinho=980, miolo=1556).items()}
print(P['medidas'])

a1 = np.array(src).astype(float)
br = (np.abs(a1[..., :3] - np.array(COR['marrom'])).sum(-1) < 90) & (a1[..., 3] > 128)
pts = []
for x in range(312, 345, 3):   # trecho sobre o corpo: faixa marrom entre o coração e a borda
    col = br[415:447, x]; ys = np.nonzero(col)[0]
    # pega o grupo de pixels marrons mais fino (o cateter), não o contorno do coração
    grupos = np.split(ys, np.nonzero(np.diff(ys) > 1)[0] + 1)
    g = min((g for g in grupos if 4 <= len(g) <= 9), key=len, default=None)
    if g is not None: pts.append((x + 0.5, 415 + g.mean() + 0.5))
for y in range(452, 477, 3):   # ponta solta, fora do corpo: último trecho opaco da linha
    row = a1[y, :, 3] > 128; xs = np.nonzero(row)[0]
    grupos = np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1)
    g = grupos[-1]
    if len(g) <= 12: pts.append((g.mean() + 0.5, y + 0.5))
print('cateter', [(round(x, 1), round(y, 1)) for x, y in pts])
P['cateter'] = [(round(x, 1), round(y, 1)) for x, y in pts]
json.dump(P, open('pecas.json', 'w'), indent=1)
