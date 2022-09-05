#!/usr/bin/env bash

./build.sh

docker save joeranbosma/picai_prostate_segmentation_processor:latest | gzip -c > picai_prostate_segmentation_processor-v2.1.tar.gz

