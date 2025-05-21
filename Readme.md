# Decomposing a Monolith into Microservices (GB1FGO)

This repository contains the final codabase for the microservices.

## Setup

Start the lab enviroment:

- Open the AWS Academy portal and start a learner lab environment.
- Open the AWS console.

Install this CloudFromation stack: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://vitmac12-resources.s3.amazonaws.com/k3s-multinode.template&stackName=k3s-multinode

- Fill in your Neptun ID.
- Select 20 GB for the EC2 instance. (Server: Storage size of the Kubernetes server in GiB)
- Under the "Security group settings" block: Change "Allow cluster ingress from this CIDR block" to "Anywhere-IPv4--0.0.0.0-slash-0".
- Accept the three checkboxes at the bottom.
- Click "Create stack".
- Wait for the stack creation to complete.

Log in to the EC2 intance:

- After the stack is successfully created, go to the "Outputs" tab.
- Click the link next to the "0K3sServerSsh" Key to open the EC2's "Connect to instance" page.
- Click "Connect".

Clone the repository:

```sh
git clone https://github.com/hajduko/cloud-native-lab-hw.git
cd cloud-native-lab-hw
```

Set permission to run script:

```sh
chmod +x run.sh
```

## Usage

Run the application stack:

```sh
./run.sh
```

Export the SSH key to Github (https://github.com/settings/keys) when promted

## Testing

Run the test:

```sh
./test.sh
```

Push the commit to Github to check the result pictures:

```sh
git push
```
