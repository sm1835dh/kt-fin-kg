#!/bin/bash
pkill -f "ssh.*{port_number}"
ssh -i ~/.ssh/{pem_file_name}.pem -L {port_number}:{postgresql_domain}:5432 azureuser@{postgresql_public_ip} -N -f
echo "SSH tunnel started on port {port_number}"