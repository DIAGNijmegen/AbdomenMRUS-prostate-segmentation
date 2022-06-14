#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

./build.sh

VOLUME_SUFFIX=$(dd if=/dev/urandom bs=32 count=1 | md5sum | cut -c 1-10)

DOCKER_FILE_SHARE=picai_prostate_segmentation_processor-output-$VOLUME_SUFFIX
docker volume create $DOCKER_FILE_SHARE
# you can see your output (to debug what's going on) by specifying a path instead:
# DOCKER_FILE_SHARE="/Users/joeranbosma/tmp-docker-volume"

docker run --rm \
        -v $SCRIPTPATH/test/:/input/ \
        -v $DOCKER_FILE_SHARE:/output/ \
        picai_prostate_segmentation_processor

# check prostate segmentation (at /output/images/transverse-whole-prostate-mri/prostate_gland.mha)
docker run --rm \
        -v $DOCKER_FILE_SHARE:/output/ \
        -v $SCRIPTPATH/test/:/input/ \
        insighttoolkit/simpleitk-notebooks:latest python -c "import sys; import numpy as np; import SimpleITK as sitk; f1 = sitk.GetArrayFromImage(sitk.ReadImage('/output/images/transverse-whole-prostate-mri/prostate_gland.mha')); f2 = sitk.GetArrayFromImage(sitk.ReadImage('/input/transverse-whole-prostate-mri/ProstateX-0000_07-07-2011.mha')); print('Pixels different between prediction and reference:', np.abs(f1!=f2).sum()); sys.exit(int(np.abs(f1!=f2).sum() > 10));"

if [ $? -eq 0 ]; then
    echo "Tests successfully passed..."
else
    echo "Expected output was not found..."
fi


docker volume rm $DOCKER_FILE_SHARE

