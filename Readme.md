# Decomposing a Monolith into Microservices (GB1FGO)

This repository contains the final codabase for the microservices.

## Setup

Install this CloudFromation stack: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://vitmac12-resources.s3.amazonaws.com/k3s-multinode.template&stackName=k3s-multinode

Select 20 GB for the EC2 instance. (Server: Storage size of the Kubernetes server in GiB)

Clone the repository:

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
