"""Build and isolate-install a wheel without changing the Python environment."""
from pathlib import Path
import subprocess,sys,os,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'outputs/release';out.mkdir(parents=True,exist_ok=True)
temp=out/'build-temp';temp.mkdir(exist_ok=True)
env={**os.environ,'TEMP':str(temp),'TMP':str(temp)}
cmd=[sys.executable,'-m','pip','wheel',str(ROOT),'--no-build-isolation','--no-deps','--no-index','--no-cache-dir','--wheel-dir',str(out)]
p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
(out/'build.log').write_text(p.stdout,encoding='utf-8');p.check_returncode()
wheel=max(out.glob('*.whl'),key=lambda x:x.stat().st_mtime)
target=out/'final-validation'
# This is a task-local pip target, never the user's Python environment.
cmd=[sys.executable,'-m','pip','install','--upgrade','--no-deps','--no-index','--no-cache-dir','--target',str(target),str(wheel)]
p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
(out/'install.log').write_text(p.stdout,encoding='utf-8');p.check_returncode()
(out/'wheel.json').write_text(json.dumps({'wheel':str(wheel),'sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'installed':str(target)},indent=2),encoding='utf-8')
print('Built and isolated',wheel,hashlib.sha256(wheel.read_bytes()).hexdigest())
