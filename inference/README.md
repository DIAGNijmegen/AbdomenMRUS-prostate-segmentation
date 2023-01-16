# Prostate Segmentation in MRI - Inference

Please read the [general description of this algorithm](../) - including its intended use and warnings - first.

This algorithm is hosted on [Grand-Challenge.com](https://grand-challenge.org/algorithms/prostate-segmentation/). Alternatively, [inference can be performed locally](inference/README.md) using Docker. To use Docker for local inference, a working understanding of Docker is assumed.


## Method A: build Docker container and perform inference case-by-case
First, clone the repository:

```bash
git clone https://github.com/DIAGNijmegen/AbdomenMRUS-prostate-segmentation
cd AbdomenMRUS-prostate-segmentation
```

Then, build the Docker container:

```bash
./build.sh
```

This builds the Docker container named `joeranbosma/picai_prostate_segmentation_processor`, which can be used for inference.
To perform inference, prepare the case in the same format as the [test case](../test/):

```bash
test
├── images
│   ├── transverse-adc-prostate-mri
│   │   └── ProstateX-0000_07-07-2011_adc.mha
│   ├── transverse-hbv-prostate-mri
│   │   └── ProstateX-0000_07-07-2011_hbv.mha
│   └── transverse-t2-prostate-mri
│       └── ProstateX-0000_07-07-2011_t2w.mha
```

Then, perform inference by executing the Docker container and pointing to the input data:

```bash
docker run --cpus=8 --memory=12gb --shm-size=12gb --gpus='"device=0"' -it --rm \
    -v /path/to/input/:/input \
    -v /path/to/output/:/output \
    joeranbosma/picai_prostate_segmentation_processor
```

In case you observe one of the following two errors:

```bash
PermissionError: [Errno 13] Permission denied: '/output/images'
FileNotFoundError: [Errno 2] No such file or directory: '/output/images/transverse-whole-prostate-mri'
```

If this happens, create the subfolders `/path/to/output/images/transverse-whole-prostate-mri` already.

After the Docker container finishes, the prostate segmentation will be stored to `/path/to/output/images/transverse-whole-prostate-mri/prostate_gland.mha`.


## Method B: use prebuilt Docker container and perform batch inference
Please follow the steps outlined in [Training > Inference](../training/training-steps.md#nnu-net---inference).
