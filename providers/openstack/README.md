# openstack
Module used to build openstack instances.

## Connection
For Terraform to be able to connect to OpenStack API, you must provide `clouds.yaml`. For more info, see the OpenStack [docs](https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html).


## Arguments
- **fip_pool**: specifies floating IP pool
- **name**: name of the instance
- **total**: number of instances to build
- **image_name**: specifies image to use
- **flavour_name**: specifies instance flavour
- **tenant**: cloud tenant to create instance in
- **network_name**: network to create instance in
- **cloud_name**: specifies which cloud from clouds.yaml to use
- **infrastructure_name**: name of the infrastructure

## Outputs
- **hosts**: list of floating IPs of created instances

