import os, glob, json
os.environ['TMPDIR']='/kaggle/working/quadbench/tmp'
os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
p='/kaggle/working/quadbench/models/clip'
model=CLIPModel.from_pretrained(p); proc=CLIPProcessor.from_pretrained(p); model.eval()
out={}
for d in sorted(glob.glob('/kaggle/working/quadbench/results/*')):
    pf=d+'/prompt.txt'
    if not os.path.exists(pf): continue
    prompt=open(pf).read().strip()
    for f in sorted(glob.glob(d+'/*.png')):
        key=os.path.basename(d)
        im=Image.open(f).convert('RGB')
        inp=proc(text=[prompt], images=im, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            e=model(**inp)
            ie=e.image_embeds/e.image_embeds.norm(dim=-1,keepdim=True)
            te=e.text_embeds/e.text_embeds.norm(dim=-1,keepdim=True)
            s=float((ie*te).sum(dim=-1)[0])
        out.setdefault(key,[]).append(round(s,5))
json.dump(out, open('/kaggle/working/quadbench/results/clip_by_prompt.json','w'), indent=2)
agg={}
for k,v in sorted(out.items()):
    pfx=k.split('_')[0]
    agg.setdefault(pfx,[]).extend(v)
    print(f"{k}: {sum(v)/len(v):.4f} n={len(v)}")
print("===== AGGREGATE =====")
for pfx,v in sorted(agg.items()):
    print(f"{pfx}: n={len(v)} mean={sum(v)/len(v):.4f} min={min(v):.4f} max={max(v):.4f}")
