# aws
Module used to build aws instances.

## Connection
For Terraform to be able to connect to AWS API, you must provide it with credentials. 
The recommended way is by *Shared Credentials file* `$HOME/.aws/credentials`. For more information see the [docs](https://www.terraform.io/docs/providers/aws/index.html#shared-credentials-file).

## Arguments
- **region**: specifies AWS region
- **ami**: image to be used
- **instance_type**: type of the instance
- **name**: name of the instance
- **total**:  number of instances to build

## Outputs
- **hosts**: list of public IPs of created instances

