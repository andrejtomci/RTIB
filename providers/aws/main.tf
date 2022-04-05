provider "aws" {
  region = var.region
}

resource "aws_instance" "instance" {
  ami = var.ami
  instance_type = var.instance_type
  count = var.total
  key_name = aws_key_pair.keypair.*.key_name[count.index]
  provisioner "local-exec" {
    command = "echo \"${tls_private_key.ssh_key.*.private_key_pem[count.index]}\" > ssh_keys/\"${var.name}_${count.index}\" && chmod 600 ssh_keys/\"${var.name}_${count.index}\""
  }
}
resource "tls_private_key" "ssh_key" {
  count = var.total
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "aws_key_pair" "keypair" {
  count = var.total
  key_name = "${var.name}_${count.index}_key"
  public_key = tls_private_key.ssh_key.*.public_key_openssh[count.index]
}