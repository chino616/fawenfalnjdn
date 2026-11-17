#
# Demonstrate that mu2e can be used as a module
#
import pathlib
import yaml
import mu2e_v2 as mu2e

path = 'example.yaml'
with open(path, "r") as f:
    data = yaml.safe_load(f)
    ndata = mu2e.processdata(data)
    # print("ndata = ", ndata)
    print(f"Decay rate = {ndata['DecayRate']}")
    print(f"Branching Ratio = {ndata['BranchingRatio']}")

