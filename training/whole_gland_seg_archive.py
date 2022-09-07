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
from typing import List, Optional

from picai_prep.data_utils import PathLike
from tqdm import tqdm


def generate_prostate158_archive_items(
    in_dir_data: PathLike,
    images_dir: PathLike,
):
    """
    Generate archive items for Prostate158 dataset, with archive of the following structure:
    /path/to/dataset/
    ├── [patient UID]/
        ├── [modality].nii.gz
        ├── t2_anatomy_reader1.nii.gz
        ...
    """
    archive_list = []

    # traverse archive
    archive_dir = os.path.join(in_dir_data, images_dir)
    for study_id in tqdm(sorted(os.listdir(archive_dir))):
        # traverse each study
        study_dir = os.path.join(images_dir, study_id)
        if not os.path.isdir(os.path.join(in_dir_data, study_dir)):
            continue

        # construct scan paths
        scan_paths = [
            os.path.join(study_dir, f"{modality}.nii.gz")
            for modality in ["t2", "adc", "dwi"]
        ]
        all_scans_found = all([
            os.path.exists(os.path.join(in_dir_data, path))
            for path in scan_paths
        ])

        # construct annotation path
        files = [fn for fn in os.listdir(os.path.join(archive_dir, study_id))]
        annotation_paths = sorted([fn for fn in files if fn.startswith("t2_anatomy_reader")])

        # check if annotation exists
        if annotation_paths:
            # grab (first) annotation path
            annotation_path = os.path.join(images_dir, study_id, annotation_paths[0])
        else:
            # could not find annotation, skip case
            continue

        if all_scans_found:
            # store info for complete studies
            archive_list += [{
                "patient_id": study_id,
                "study_id": study_id,
                "scan_paths": scan_paths,
                "annotation_path": annotation_path,
            }]

    if not len(archive_list):
        raise ValueError(f"Did not find any MHA scans in {archive_dir}, aborting.")

    assert len(archive_list) == 139, "Dataset should have 139 training cases"

    return archive_list


def generate_prostatex_archive_items(
    in_dir_data: PathLike,
    images_dir: PathLike,
    annotations_dir: PathLike,
    subject_list: Optional[List[str]] = None
):
    """
    Generate archive items for ProstateX dataset, with archive of the following structure:
    /path/to/dataset/
    ├── [patient UID]/
        ├── [patient UID]_[study UID]_[modality].mha

    The annotations are assumed to be stored as [patient UID]_[study UID].nii.gz
    """
    archive_list = []

    if subject_list is not None:
        print(f"Collecting {len(subject_list)} cases")

    # traverse archive
    archive_dir = os.path.join(in_dir_data, images_dir)
    for patient_id in tqdm(sorted(os.listdir(archive_dir))):
        # traverse each patient
        patient_dir = os.path.join(archive_dir, patient_id)
        if not os.path.isdir(patient_dir):
            continue

        # collect list of available studies
        files = os.listdir(patient_dir)
        files = [fn.replace(".mha", "") for fn in files if ".mha" in fn and "._" not in fn]
        subject_ids = ["_".join(fn.split("_")[0:2]) for fn in files]
        subject_ids = sorted(list(set(subject_ids)))

        # check which studies are complete
        for subject_id in subject_ids:
            if subject_list is not None and subject_id not in subject_list:
                continue

            patient_id, study_id = subject_id.split("_")

            # construct scan paths
            scan_paths = [
                os.path.join(
                    images_dir, patient_id,
                    f"{subject_id}_{modality}.mha"
                )
                for modality in ["t2w", "adc", "hbv"]
            ]
            all_scans_found = all([
                os.path.exists(os.path.join(in_dir_data, path))
                for path in scan_paths
            ])

            # construct annotation path
            annotation_path = os.path.join(annotations_dir, f"{subject_id}.nii.gz")

            # check if annotation exists
            if not os.path.exists(os.path.join(in_dir_data, annotation_path)):
                # could not find annotation, skip case
                print(f"Annotation for {subject_id} not found! At {os.path.join(in_dir_data, annotation_path)}")
                continue

            if all_scans_found:
                # store info for complete studies
                archive_list += [{
                    "patient_id": patient_id,
                    "study_id": study_id,
                    "scan_paths": scan_paths,
                    "annotation_path": annotation_path,
                }]

    if not len(archive_list):
        raise ValueError(f"Did not find any sample in {archive_dir}, aborting.")

    if subject_list is not None:
        assert len(archive_list) == len(subject_list), f"Dataset should have {len(subject_list)} cases"

    return archive_list


def generate_rumc_archive_items(
    in_dir_data: PathLike,
    images_dir: PathLike,
    annotations_dir: PathLike,
    subject_list: Optional[List[str]] = None
):
    """
    Generate archive items for RUMC dataset, with archive of the following structure:
    /path/to/dataset/
    ├── [patient UID]/
        ├── [patient UID]_[study UID]_[modality].mha

    The annotations are assumed to be stored as [patient UID]_[study UID].nii.gz
    """
    archive_list = []

    if subject_list is not None:
        print(f"Collecting {len(subject_list)} cases")

    # traverse archive
    archive_dir = os.path.join(in_dir_data, images_dir)
    for patient_id in tqdm(sorted(os.listdir(archive_dir))):
        # traverse each patient

        # collect list of available studies
        patient_dir = os.path.join(archive_dir, patient_id)
        if not os.path.isdir(patient_dir):
            continue
        files = os.listdir(patient_dir)
        files = [fn.replace(".mha", "") for fn in files if ".mha" in fn and "._" not in fn]
        subject_ids = ["_".join(fn.split("_")[0:2]) for fn in files]
        subject_ids = sorted(list(set(subject_ids)))

        # check which studies are complete
        for subject_id in subject_ids:
            if subject_list is not None and subject_id not in subject_list:
                continue

            patient_id, study_id = subject_id.split("_")

            # construct scan paths
            scan_paths = [
                os.path.join(
                    images_dir, patient_id,
                    f"{subject_id}_{modality}.mha"
                )
                for modality in ["t2w", "adc", "hbv"]
            ]
            all_scans_found = all([
                os.path.exists(os.path.join(in_dir_data, path))
                for path in scan_paths
            ])

            # construct annotation path
            annotation_path = os.path.join(annotations_dir, f"{subject_id}.nii.gz")

            # check if annotation exists
            if not os.path.exists(os.path.join(in_dir_data, annotation_path)):
                # could not find annotation, skip case
                print(f"Annotation for {subject_id} not found! At {os.path.join(in_dir_data, annotation_path)}")
                continue

            if all_scans_found:
                # store info for complete studies
                archive_list += [{
                    "patient_id": patient_id,
                    "study_id": study_id,
                    "scan_paths": scan_paths,
                    "annotation_path": annotation_path,
                }]

    if not len(archive_list):
        raise ValueError(f"Did not find any sample in {archive_dir}, aborting.")

    if subject_list is not None:
        assert len(archive_list) == len(subject_list), f"Dataset should have {len(subject_list)} cases"

    return archive_list


def generate_mha2nnunet_settings(
    archive_item_collectors,
    output_path: PathLike,
):
    """
    Create mha2nnunet_settings (with annotations) for whole-gland prostate segmentation.

    Parameters:
    - archive_item_collectors: [
        (archive_item_function, archive_item_function_arguments)
    ],
        where `archive_item_function` takes the arguments `archive_item_function_arguments`,
        and returns an `archive_list`.
    - output_path: path to store mha2nnunet settings JSON to
    """

    # collect archive items from each dataset
    archive_list = []
    for func, kwargs in archive_item_collectors:
        archive_list += func(**kwargs)

    mha2nnunet_settings = {
        "dataset_json": {
            "task": "Task2202_prostate_segmentation",
            "description": "bpMRI scans with whole-gland prostate segmentations.",
            "tensorImageSize": "4D",
            "reference": "",
            "licence": "",
            "release": "1.0",
            "modality": {
                "0": "T2W",
                "1": "CT",
                "2": "HBV"
            },
            "labels": {
                "0": "background",
                "1": "prostate_gland"
            }
        },
        "preprocessing": {
            # optionally, resample and perform centre crop:
            # "matrix_size": [
            #     20,
            #     320,
            #     320
            # ],
            # "spacing": [
            #     3.0,
            #     0.5,
            #     0.5
            # ],
        },
        "archive": archive_list
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as fp:
        json.dump(mha2nnunet_settings, fp, indent=4)

    print(f""""
    Saved mha2nnunet_settings to {output_path}, with {len(archive_list)} cases.
    """)


if __name__ == "__main__":
    # set up paths
    project_root = Path("/media/pelvis/projects/")
    workdir = project_root / "joeran/picai/workdir/"
    in_dir_data = "/media/pelvis/data/prostate-MRI/"
    output_path = workdir / "mha2nnunet_settings" / "Task2202_prostate_segmentation.json"

    # read subject list of cases without patient overlap with PI-CAI test/validation sets
    with open(project_root / "joeran/Data/ds-config/V2_ZonalSegmentation299/ds-config-all.json") as fp:
        subject_list = json.load(fp)['subject_list']

    # collect arguments for Prostate158 dataset
    prostate158_kwargs = {
        "in_dir_data": in_dir_data,
        "images_dir": "public-datasets/prostate158/prostate158_train/train/"
    }

    # collect arguments for ProstateX dataset
    prostatex_kwargs = {
        "in_dir_data": in_dir_data,
        "images_dir":  "public-datasets/prostateX/images/",
        "annotations_dir": "public-datasets/prostateX/annotations/granular-delineations-TZPZ/",
        "subject_list": [s for s in subject_list if "ProstateX" in s]
    }

    # RUMC dataset
    rumc_kwargs = {
        "in_dir_data": in_dir_data,
        "images_dir":  "rumc/images",
        "annotations_dir":  "rumc/annotations/zonal-segmentations/granular-delineations-TZPZ",
        "subject_list": [s for s in subject_list if "ProstateX" not in s]
    }

    generate_mha2nnunet_settings(
        archive_item_collectors=[
            (generate_prostate158_archive_items, prostate158_kwargs),
            (generate_prostatex_archive_items, prostatex_kwargs),
            (generate_rumc_archive_items, rumc_kwargs),
        ],
        output_path=output_path,
    )
