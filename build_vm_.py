from xml.etree.ElementTree import SubElement
from phpipam.phpipam_functions1_4 import Phpipam
from proxmox_api.proxmox_functions import Proxmox
from librenms_api.librenms_functions import Librenms
import argparse
import pymysql.cursors
#Example params
from secrets import Secrets

def get_next_ip(ipam_section,vm_subnet):
    kptipam = Phpipam()
    kptipam.phpipam_login()
    kptipam.get_phpipam_sections(ipam_section)
    kptipam.get_phpipam_subnets()
    #maybe clean this up:
    kptipam.next_ip = kptipam.get_phpipam_nextip(vm_subnet)
    return kptipam

def prep_ipv6_ip(ipv6_subnet):
    kptipam_v6 = Phpipam()
    kptipam_v6.phpipam_login()
    kptipam_v6.get_phpipam_sections('KPTDC IPv6')
    kptipam_v6.get_phpipam_subnets()
    kptipam_v6.get_phpipam_subnet_id(ipv6_subnet)
    return kptipam_v6

def set_ipv6_ip(kptipam_v6,new_vm_name,ipv6_address):
    kptipam_v6.set_phpipam_specific_ip(new_vm_name,ipv6_address)

def parse_ipv6_octet(kptipam_v4):
    #Split the IPv4 IP by 4 ocets, and we will use the last one to define the IPv6 IP.
    ipv4_split = kptipam_v4.phpipam_next_ip.split('.')
    ipv6_last_octet = ipv4_split[3]
    return(ipv6_last_octet)

def clone_vm(proxmox_username,proxmox_password,proxmox_ip,template_id,new_vmid,new_vm_name,subnet_mask,subnet_gateway,kptipam_v4,drive_size,vlan_id,ipv6_address,ipv6_gateway,ipv6_subnetmask):
    print ('Running clone vm')
    proxmox_obj = Proxmox(proxmox_ip,proxmox_username,proxmox_password)
    proxmox_obj.set_proxmox_clone_vm(template_id,new_vmid,new_vm_name)
    proxmox_obj.get_proxmox_vm_lock_status(new_vmid)
    proxmox_obj.set_proxmox_cloud_init(kptipam_v4.phpipam_next_ip+'/'+subnet_mask,subnet_gateway,ipv6_address,ipv6_gateway,ipv6_subnetmask)
    proxmox_obj.set_proxmox_drive_size(drive_size)
    proxmox_obj.get_proxmox_vm_interface_config(new_vmid)
    proxmox_obj.set_proxmox_interface_vlan_id(new_vmid,vlan_id)

def set_new_ip_phpipam(kptipam,new_vm_name):
    kptipam.set_phpipam_ip(new_vm_name)

def add_device_to_monitoring(new_vm_name):
    device = Librenms()
    device.librenms_add_device(new_vm_name,'kptsnmp')
    if device.device_add_response.json()['status'] == 'ok':
        print ('Device added to librenms successfully.')
    else:
        print ('Device failed to add to librenms')

def connect_to_db():
    print (f"Connecting to database {Secrets.mysql['db_ip']}")
    prd_db = pymysql.connect(
        host = Secrets.mysql['db_ip'],
        user = Secrets.mysql['username'],
        password = Secrets.mysql['password']
    )
    return prd_db

def query_vlan_ipv4(prd_db,vlan_id):
    cursor = prd_db.cursor()
    print (f"Running Query on database for vlan {vlan_id}")
    cursor.execute(f'SELECT * FROM {Secrets.mysql["ipv4_db_name"]}.{Secrets.mysql["ipv4_table_name"]} WHERE vlan_id = ' + vlan_id + ';')
    ipv4_db_result =  (cursor.fetchall())
    ipv4_network= {}
    ipv4_network={
        'network' : ipv4_db_result[0][1],
        'gateway' : ipv4_db_result[0][2],
        'subnet_mask' : ipv4_db_result[0][3],
        
    }
    print (f"IPv4 network found:  {ipv4_network}")
    return (ipv4_network)

def query_vlan_ipv6(prd_db,vlan_id):
    cursor = prd_db.cursor()
    cursor.execute(f'SELECT * FROM {Secrets.mysql["ipv6_db_name"]}.{Secrets.mysql["ipv6_table_name"]} WHERE vlan_id = ' + vlan_id + ';')
    ipv6_db_result =  (cursor.fetchall())
    ipv6_network= {}
    ipv6_network={
        'network' : ipv6_db_result[0][1],
        'gateway' : ipv6_db_result[0][2],
        'subnet_mask' : ipv6_db_result[0][3],
        
    }
    print (f"IPv6 network found:  {ipv6_network}")
    return (ipv6_network)

def main(*args):
    parser = argparse.ArgumentParser(description='Program to build new proxmox VM and add to monitoring')
    parser.add_argument('--template_id',action='store', help='proxmox template ID to clone')
    parser.add_argument('--new_vmid', action='store', help='VM ID of new cloned vm')
    parser.add_argument('--new_vm_name', action='store', help='name of new vm')
    parser.add_argument('--ipam_section', action='store',help='kptipam section, enter ipv4 or ipv6')
    parser.add_argument('--disk_size', action='store', help="disk size of disk after clone")
    parser.add_argument('--add_librenms', action='store',help='add device to librenms after vm is booted. new_vm_name to be set')
    parser.add_argument('--vlan_id', action='store',help='vlan ID assignement for VM and DB lookup')
    argsparse = parser.parse_args()
    if argsparse.ipam_section == "ipv4":
        ipam_section = Secrets.phpipam['ipam_section_ipv4']
    if argsparse.ipam_section == "ipv6":
        ipam_section = Secrets.phpipam['ipam_section_ipv6']
    if argsparse.add_librenms:
        add_device_to_monitoring(argsparse.new_vm_name)
    prd_db = connect_to_db()
    ipv4_network = query_vlan_ipv4(prd_db,argsparse.vlan_id)
    ipv6_network = query_vlan_ipv6(prd_db,argsparse.vlan_id)
    
    if argsparse.template_id:
        kptipam_v4 = get_next_ip(ipam_section,ipv4_network['network'])
        print (f"IPv4 IP found: {kptipam_v4.next_ip}")
        ipv6_last_octet = parse_ipv6_octet(kptipam_v4)
        ipv6_address = ipv6_network['network'] + ipv6_last_octet
        kptipam_v6 = prep_ipv6_ip(ipv6_network['network'])
        clone_vm(Secrets.proxmox['proxmox_user'], Secrets.proxmox['proxmox_password'],Secrets.proxmox['proxmox_ip'],argsparse.template_id,argsparse.new_vmid,argsparse.new_vm_name,ipv4_network['subnet_mask'],ipv4_network['gateway'],kptipam_v4,argsparse.disk_size,argsparse.vlan_id,ipv6_address,ipv6_network['gateway'],ipv6_network['subnet_mask'])
        set_new_ip_phpipam(kptipam_v4,argsparse.new_vm_name)
        set_ipv6_ip(kptipam_v6,argsparse.new_vm_name,ipv6_address)
    
    

if __name__ == '__main__':
    main()