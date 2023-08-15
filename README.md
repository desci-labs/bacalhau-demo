# Bacalhau demo

## Prerequisites
- Bacalhau client (`curl -sL https://get.bacalhau.org/install.sh | bash`)
- Docker

Optional: [dpid-fetch](https://github.com/desci-labs/dpid-fetch) is required to get the CIDs necessary for running the Bacalhau workload. The inputs are listed in the CLI instructions below though.

## Building the image
Bacalhau only accepts images for the `linux/amd64` platform. This can be achieved on ARM MacOS (e.g. M1 et al) with the following command:
```shell
docker buildx build --platform linux/amd64 -t grid_reso_analysis_desci:latest .
```

On linux, just run:
```shell
docker build -t grid_reso_analysis_desci:latest .
```

Note: for Bacalhau to be able to find this, it needs to be pushed to a repository like [Docker Hub](https://hub.docker.com).

## Running the container
The container scripts expects these files from [node 78](https://beta.dpid.org/78/v1/root/grid_reso_analysis?raw) to be present in the `inputs` directory:
- `chan_l6_4x12x24_4x4x8.h5`
- `chan_l6_4x12x24_6x6x12.h5`
- `chan_l6_4x12x24_8x8x16.h5`

When run, it will produce a graph pdf in the `outputs` directory. Note that the container only knows about the filesystem inside, so we need to tell docker what these two directories are (`inputs` and `outputs`). The way to do this differs locally and on Bacalhau:

### Locally
Done by mounting a volume:
```shell
docker run --rm \
  -v [dir_with_files]:/inputs \
  -v $PWD:/outputs \
  grid_reso_analysis_desci:latest
```

### Bacalhau
Get the CIDs with [dpid-fetch](https://github.com/desci-labs/dpid-fetch) and configure as `inputs`. Note that the image needs to be pushed to a public repository where Bacalhau can access it, this example uses a build from `m0ar`:
```shell
# Run the job
bacalhau docker run \
  --input src=ipfs://bafybeiggs56o2lfnokepfnhllazq4pgohmdnmsdjrjdbxsyntmq2zlktri,dst=/inputs/chan_l6_4x12x24_4x4x8.h5 \
  --input src=ipfs://bafybeibeaampol2yz5xuoxex7dxri6ztqveqrybzfh5obz6jrul5gb4cf4,dst=/inputs/chan_l6_4x12x24_6x6x12.h5 \
  --input src=ipfs://bafybeibvt5s7scy6lvu6v5r3w2oiliti326ddtpx3hhtvphxpxpaeoiy2i,dst=/inputs/chan_l6_4x12x24_8x8x16.h5 \
  m0ar/grid_reso_analysis_desci:1.0.2
```

When this is running it will display the job ID. This can be used to check on progress and metadata using `bacalhau describe [job id]`, or to download the results when the job has terminated with `bacalhau get [job id]`.

After fetching the results, you get a directory called `job-[job id]`. Open this in your file browser, and you can see the generated figure in `outputs/figure_14.pdf`!

## Troubleshooting
### Bacalhau ignoring your image changes
When changing the image, if Bacalhau gives the same error even if you have updated the docker image, you may need to push it with a new tag. It is possible that tag names are cached for a while, so relying on the `latest` tag may not work with frequent updates.

