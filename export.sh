#!/usr/bin/env bash

./build.sh

docker save picai_prostate_segmentation_processor | gzip -c > picai_prostate_segmentation_processor-1.0.1.tar.gz
