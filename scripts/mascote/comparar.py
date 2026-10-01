import sys
from PIL import Image
import numpy as np
o=Image.open('Urso2.png').convert('RGBA'); s=Image.open(sys.argv[1] if len(sys.argv)>1 else 'svg1.png').convert('RGBA')
def cinza(im):
    bg=Image.new('RGBA',im.size,(200,200,200,255)); bg.alpha_composite(im); return bg.convert('RGB')
O,Sv=cinza(o),cinza(s)
d=np.abs(np.array(O).astype(int)-np.array(Sv).astype(int)).sum(-1)
print('pixels com diferença forte (>150):',(d>150).sum(),'de',d.size,'=',round((d>150).mean()*100,3),'% | média',round(d.mean(),2))
ys,xs=np.nonzero(d>150)
import collections
print('onde:',collections.Counter((int(x)//50*50,int(y)//50*50) for x,y in zip(xs,ys)).most_common(12))
dif=Image.fromarray(np.where(d[...,None]>150,[255,0,0],np.array(O)//3+150).astype(np.uint8))
lado=Image.new('RGB',(1500,558),(255,255,255)); lado.paste(O,(0,0)); lado.paste(Sv,(500,0)); lado.paste(dif,(1000,0)); lado.save('compara.png')
