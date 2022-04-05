variable "region" {
  default = "eu-west-3"
  type = string
}

variable "ami" {
  default = "ami-07bc8d958e772f709"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "name" {
  type = string
}

variable "total" {
  default = 1
}