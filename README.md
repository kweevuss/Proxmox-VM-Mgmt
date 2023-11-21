# Proxmox-VM-Mgmt
Perform functions in Proxmox Hypervisor. There are several main things this project expects:

1. Secrets file is filled out with information. 
2. Mysql database setup with network subnet/vlan info. This seems to be a limit of phpipam to not store some data. Future I plan to have a container ready with this database. For now a quick example of the database table:
vlan_id | subnet | subnet_gateway | subnet_mask
---|---|---|--
2 | 192.168.2.0 | 192.168.2.1 | 24

3. A cloud init working VM template that you would like to clone



## Goal of projects

This is crafted around my personal setup. I have my network vlan information in phpipam, with some other details, such as vlan, in a mysql database. This is utilized to query the subnet, find the next avaiable IP, set it in a cloud init enabled template of a VM on a proxmox hypervisor, clone the VM, and finally set the IP of the dns hostname of the new VM. 


Example run:
 python3 build_vm_.py --template_id 301 --new_vmid 217 --new_vm_name testclone01 --ipam_section ipv4 --disk_size 20G --vlan_id 66
Connecting to database prdkptdb01.internal.keepingpacetech.com
Running Query on database for vlan 66
IPv4 network found:  {'network': '192.168.66.128', 'gateway': '192.168.66.129', 'subnet_mask': '25'}
IPv6 network found:  {'network': 'fd00:0:0:66b::', 'gateway': 'fd00:0:0:66b::1', 'subnet_mask': '64'}
ipv4 IP found: None
Running clone vm
Checking VM status for when clone is done every 5 seconds...
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
VM is still locked
checking vm status 217
vm must be cloned
Was able to write IP to IPAM
{'code': 201, 'success': True, 'message': 'Address created', 'id': '473', 'time': 0.239}

## Running script with parameters

See the help for more information:
usage: build_vm_.py [-h] [--template_id TEMPLATE_ID] [--new_vmid NEW_VMID] [--new_vm_name NEW_VM_NAME] [--ipam_section IPAM_SECTION] [--disk_size DISK_SIZE] [--add_librenms ADD_LIBRENMS]
                    [--vlan_id VLAN_ID]
  -h, --help            show this help message and exit
  --template_id TEMPLATE_ID
                        proxmox template ID to clone
  --new_vmid NEW_VMID   VM ID of new cloned vm
  --new_vm_name NEW_VM_NAME
                        name of new vm
  --ipam_section IPAM_SECTION
                        ipam section, enter ipv4 or ipv6
  --disk_size DISK_SIZE
                        disk size of disk after clone
  --add_librenms ADD_LIBRENMS
                        add device to librenms after vm is booted. new_vm_name to be set
  --vlan_id VLAN_ID     vlan ID assignement for VM and DB lookup

Generally, the script should be ran as: build_vm_.py [--template_id TEMPLATE_ID] [--new_vmid NEW_VMID] [--new_vm_name NEW_VM_NAME] [--ipam_section IPAM_SECTION] [--disk_size DISK_SIZE]. 

Once the VM is up, the device can be added to librenms with: build_vm_.py [--new_vm_name NEW_VM_NAME] [--add_librenms ADD_LIBRENMS]





