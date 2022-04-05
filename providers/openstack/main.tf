terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "1.47.0"
    }
  }
}


provider "openstack" {
  cloud = var.cloud_name
  tenant_name = var.tenant
}


resource "openstack_compute_instance_v2" "openstack_instance" {
  name = "${var.name}_${count.index}"
  image_name = var.image_name
  flavor_name = var.flavour_name
  key_pair = openstack_compute_keypair_v2.keypair.*.name[count.index]
  count = var.total
  security_groups = ["default"]
  network {
    name = var.network_name
  }
  provisioner "local-exec" {
    command = "echo \"${openstack_compute_keypair_v2.keypair.*.private_key[count.index]}\" > ssh_keys/\"${var.name}_${count.index}\" && chmod 600 ssh_keys/\"${var.name}_${count.index}\""
  }
}

resource "openstack_compute_keypair_v2" "keypair" {
  count = var.total
  name = "${var.name}_${count.index}_key"

}

resource "openstack_networking_floatingip_v2" "fip" {
  pool = var.fip_pool
  count = var.total
}

resource "openstack_compute_floatingip_associate_v2" "fip" {
  floating_ip = openstack_networking_floatingip_v2.fip.*.address[count.index]
  instance_id = openstack_compute_instance_v2.openstack_instance.*.id[count.index]
  count = var.total
}

