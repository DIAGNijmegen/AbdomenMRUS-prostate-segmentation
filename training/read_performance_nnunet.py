#  Copyright 2022 Diagnostic Image Analysis Group, Radboudumc, Nijmegen, The Netherlands
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# environment settings
if 'workdir' in os.environ:
    workdir = Path(os.environ['workdir'])
else:
    workdir = Path("/media/pelvis/projects/joeran/picai/workdir")

task_results = os.path.join(workdir, "results/nnUNet/3d_fullres/Task2202_prostate_segmentation")
trainer_results = os.path.join(task_results, "nnUNetTrainerV2_Loss_FL_and_CE_checkpoints__nnUNetPlansv2.1")


res = []
for fold in range(5):
    # determine validation performance
    path = os.path.join(trainer_results, f"fold_{fold}/validation_raw_postprocessed/summary.json")
    with open(path) as fp:
        metrics = json.load(fp)

    # calculate DSC mean ± std.
    for metric in ["Dice", "Jaccard"]:
        results = metrics['results']['all']
        results = [case['1'][metric] for case in results]
        res += [{
            "metric": metric,
            "fold": fold,
            "mean": np.mean(results),
            "std": np.std(results),
        }]


# determine overall validation performance
path = os.path.join(trainer_results, f"cv_niftis_postprocessed/summary.json")
with open(path) as fp:
    metrics = json.load(fp)

# calculate DSC mean ± std.
for metric in ["Dice", "Jaccard"]:
    results = metrics['results']['all']
    results = [case['1'][metric] for case in results]
    res += [{
        "metric": metric,
        "fold": "cv",
        "mean": np.mean(results),
        "std": np.std(results),
    }]

res = pd.DataFrame(res)
res.to_csv("metrics.csv", index=False)
