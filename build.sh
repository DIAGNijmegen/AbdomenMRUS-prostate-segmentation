#!/usr/bin/env bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

docker build "$SCRIPTPATH" \
    -t joeranbosma/picai_prostate_segmentation_processor:latest \
    -t joeranbosma/picai_prostate_segmentation_processor:v2.1
