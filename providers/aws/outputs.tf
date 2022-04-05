output "hosts" {
  value = aws_instance.instance.*.public_ip
}