


def storage_audit(root='public/uploads'):
    total = 0; files=[]
    for dirpath,_,fnames in os.walk(root):
        for f in fnames:
            p=os.path.join(dirpath,f); s=os.path.getsize(p); total+=s; files.append((p,s))
    return {'total_bytes': total, 'largest': sorted(files, key=lambda x:x[1], reverse=True)[:10]}
