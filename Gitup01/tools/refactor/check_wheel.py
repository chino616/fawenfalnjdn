"""Offline build-artifact smoke test; does not install or update environment packages."""
from pathlib import Path
import json
import subprocess
import sys
import zipfile

PROJECT = Path(__file__).resolve().parents[2]


def main():
    wheel = next((PROJECT/"outputs/refactor_r4/dist").glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert not any(name.startswith("workflows/") for name in names)
        metadata = archive.read(next(name for name in names if name.endswith(".dist-info/METADATA"))).decode()
        assert "Requires-Dist: numpy>=2.0" in metadata
    script = r'''
from pathlib import Path
import json, sys
sys.path.insert(0, sys.argv[1])
import numpy as np
import cevns_pyeft
assert '.whl' in cevns_pyeft.__file__
from cevns_pyeft.contracts import IntegrationSettings
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.core.predict import predict
from cevns_pyeft.kernels import compile_fast, save_compiled_kernel, load_compiled_kernel
from cevns_pyeft.core import engine
model = make_csi2021_model(sys.argv[2])
numerics = IntegrationSettings(n_er=3,n_enu=6)
kernel = compile_fast(model,numerics=numerics,basis_keys=[(6,1,'u'),(6,1,'d'),(6,2,'u'),(6,2,'d')])
slow = predict(model,numerics=numerics)
fast = kernel.predict()
np.testing.assert_allclose(fast.counts,slow.counts,rtol=1e-10,atol=1e-12)
out = Path(sys.argv[3]); save_compiled_kernel(out/'wheel_kernel.npz',kernel)
loaded = load_compiled_kernel(out/'wheel_kernel.npz',model=model)
np.testing.assert_array_equal(loaded.predict().counts,fast.counts)
# The content key must also work across source checkout and wheel imports.
portable = load_compiled_kernel(out/'kernels/small.npz',model=model)
portable_result = portable.predict()
np.testing.assert_allclose(portable_result.counts,predict(model,numerics=portable.numerics).counts,rtol=1e-10,atol=1e-12)
assert callable(engine.slow_counts_csi2021)
record = {'status':'PASS','imported_from':cevns_pyeft.__file__,'cwd':str(Path.cwd()),
          'external_resource_path':sys.argv[2],'slow_fast_max_absolute':float(abs(fast.counts-slow.counts).max()),
          'source_to_wheel_cache_portability':'PASS','installed_environment_packages':False}
(out/'wheel_smoke.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
'''
    result = subprocess.run([sys.executable,"-I","-c",script,str(wheel),
        str(PROJECT/"data/responses/responses_all.json"),str(PROJECT/"outputs/refactor_r4")],
        cwd=PROJECT.parent,text=True,capture_output=True)
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)


if __name__=="__main__":
    main()
