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

import SimpleITK as sitk
from picai_prep import MHA2nnUNetConverter

"""
Script to prepare data into the nnUNet raw data format
For documentation, please see:
https://github.com/DIAGNijmegen/picai_prep
"""

# environment settings
if 'inputdir' in os.environ:
    inputdir = Path(os.environ['inputdir'])
else:
    inputdir = Path("/media/pelvis/data/prostate-MRI/")
if 'workdir' in os.environ:
    workdir = Path(os.environ['workdir'])
else:
    workdir = Path("/media/pelvis/projects/joeran/picai/workdir")

# settings
task = "Task2202_prostate_segmentation"
trainer = "nnUNetTrainerV2_Loss_FL_and_CE_checkpoints"

# paths
mha2nnunet_settings_path = workdir / "mha2nnunet_settings" / "Task2202_prostate_segmentation.json"
nnUNet_raw_data_path = workdir / "nnUNet_raw_data"
nnUNet_task_dir = nnUNet_raw_data_path / task
nnUNet_dataset_json_path = nnUNet_task_dir / "dataset.json"


def preprocess_annotation(lbl: sitk.Image) -> sitk.Image:
    """Convert the zonal segmentations into whole-gland segmentations"""
    lbl_arr = sitk.GetArrayFromImage(lbl)

    # convert granular PI-CAI csPCa annotation to binary csPCa annotation
    lbl_arr = (lbl_arr >= 1).astype('uint8')

    # convert label back to SimpleITK
    lbl_new: sitk.Image = sitk.GetImageFromArray(lbl_arr)
    lbl_new.CopyInformation(lbl)
    return lbl_new


if nnUNet_dataset_json_path.exists():
    print(f"Found dataset.json at {nnUNet_dataset_json_path}, skipping..")
else:
    # read preprocessing settings and set the annotation preprocessing function
    with open(mha2nnunet_settings_path) as fp:
        mha2nnunet_settings = json.load(fp)

    if not "options" in mha2nnunet_settings:
        mha2nnunet_settings["options"] = {}
    mha2nnunet_settings["options"]["annotation_preprocess_func"] = preprocess_annotation

    # prepare dataset in nnUNet format
    archive = MHA2nnUNetConverter(
        output_dir=nnUNet_raw_data_path,
        scans_dir=inputdir,
        annotations_dir=inputdir,
        mha2nnunet_settings=mha2nnunet_settings,
    )
    archive.convert()
    archive.create_dataset_json()

print("Finished.")
