variable "fip_pool" {
  type = string
  default = "public-cesnet-78-128-250-PERSONAL"
}

variable "name" {
  type = string
  default = "test"
}

variable "total" {
  default = 1
  type = number
}

variable "image_name" {
  default = "debian-11-x86_64"
  type = string
}

variable "flavour_name" {
  default = "csirtmu.small2x4"
  type = string
}

variable "tenant" {
  default = "csirtmdfbdbd"
  type= string
}

variable "network_name" {
  default = "78-128-250-pers-proj-net"
  type = string
}

variable "cloud_name" {
  default = "openstack"
  type = string
}

variable "infrastructure_name" {
  default = "test_infrastructure"
  type = string
}
