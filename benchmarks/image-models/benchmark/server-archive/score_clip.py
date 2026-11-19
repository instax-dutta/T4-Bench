import os, glob, json
os.environ['TMPDIR']='/kaggle/working/quadbench/tmp'
os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
p='/kaggle/working/quadbench/models/clip'
model=CLIPModel.from_pretrained(p); proc=CLIPProcessor.from_pretrained(p); model.eval()
prompt="A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"
out={}
for f in sorted(glob.glob('/kaggle/working/quadbench/results/*/*.png')):
    key=f.split('/results/')[1].split('/')[0]
    im=Image.open(f).convert('RGB')
    inp=proc(text=[prompt], images=im, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        e=model(**inp)
        ie=e.image_embeds / e.image_embeds.norm(dim=-1,keepdim=True)
        te=e.text_embeds / e.text_embeds.norm(dim=-1,keepdim=True)
        score=float((ie*te).sum(dim=-1)[0])
    out.setdefault(key,[]).append(round(score,5))
json.dump(out, open('/kaggle/working/quadbench/results/clip_scores.json','w'), indent=2)
for k,v in sorted(out.items()):
    print(f"{k}: cosine={sum(v)/len(v):.4f} n={len(v)}")
