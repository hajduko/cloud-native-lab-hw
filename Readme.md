# Decomposing a Monolith into Microservices (GB1FGO)

This repository contains the final codabase for the microservices.

## Setup

Install this CloudFromation stack: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://vitmac12-resources.s3.amazonaws.com/k3s-multinode.template&stackName=k3s-multinode

Select 20 GB for the4 EC2 instance.

Clone the repository and install dependencies:

```sh
git clone https://github.com/hajduko/cloud-native-lab-hw.git
cd cloud-native-lab-hw
chmod +x run.sh
```

## Usage

Run the main application:

```sh
./run.sh
```

## Testing

Run the test:

```sh
./test.sh
git push
```
