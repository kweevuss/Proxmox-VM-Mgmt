#api tree https://pve.proxmox.com/pve-docs/api-viewer/index.html
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
import sys
sys.path.append("..")
from secrets import Secrets

class Proxmox():
    def __init__ (self,url,username,password):
        #When running proxmox class, it will get the params, login and get needed auth items, and set the node name variable for future calls
        self.url= "https://" + Secrets.proxmox['proxmox_ip'] + ":8006/api2/json/"
        self.username = Secrets.proxmox['proxmox_user']
        self.password = Secrets.proxmox['proxmox_password']
        self.proxmox_login()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


    def proxmox_login(self):
        payload = {"username": self.username + f"@{Secrets.proxmox['proxmox_realm']}", "password": self.password}
        self.proxmox_login_reponse = requests.post(self.url + "access/ticket", data=payload, verify=False)
        self.proxmox_prevention_token = self.proxmox_login_reponse.json()['data']['CSRFPreventionToken']
        self.proxmox_header = {'CSRFPreventionToken': self.proxmox_prevention_token}
        self.proxmox_ticket = self.proxmox_login_reponse.json()['data']['ticket']
        self.proxmox_cookie = {"PVEAuthCookie": self.proxmox_ticket}
        self.get_proxmox_node_name()

    def get_proxmox_node_name(self):
        node = requests.get(self.url + "nodes/", cookies=self.proxmox_cookie, verify=False)
        self.node_name = node.json()['data'][0]['node']


    def get_proxmox_vm_status(self,proxmox_vm_id):
        self.proxmox_vm_id = proxmox_vm_id
        print ("checking vm status " + proxmox_vm_id)
        self.proxmox_vm_status = requests.get(self.url + "nodes/" + self.node_name + "/qemu/" + self.proxmox_vm_id + "/status/current", cookies=self.proxmox_cookie,
                                 verify=False)

    def set_proxmox_clone_vm(self,vm_id_of_template,new_vm_id,new_vm_name):
        self.vm_id_of_template = vm_id_of_template
        self.new_vm_id = new_vm_id
        self.new_vm_name = new_vm_name
        payload = {"newid": self.new_vm_id, "vmid": self.vm_id_of_template, "target": self.node_name, "full": "1", "name": self.new_vm_name}
        clone_vm = requests.post(self.url + "nodes/" + self.node_name + "/qemu/" + self.vm_id_of_template + "/clone", headers=self.proxmox_header,
                                 cookies=self.proxmox_cookie,
                                 verify=False, data=payload)
        self.proxmox_vm_lock = True


    def get_proxmox_vm_lock_status(self,vm_id_lock_check):
        print ('Checking VM status for when clone is done every 5 seconds...')
        time.sleep(5)
        self.vm_id_lock_check = vm_id_lock_check
        self.get_proxmox_vm_status(self.vm_id_lock_check)
        try:
            while self.proxmox_vm_status.json()['data']['lock']:
                print("VM is still locked")
                self.get_proxmox_vm_status(self.vm_id_lock_check)
                time.sleep(10)
        except:
            print ("vm must be cloned")
            self.proxmox_vm_lock = False


    def set_proxmox_cloud_init(self,subnet_cidr,gateway,ipv6_address,ipv6_gateway,ipv6_subnetmask):
        self.subnet_cidr = subnet_cidr
        self.gateway = gateway
        self.ipv6_address = ipv6_address
        self.ipv6_gateway = ipv6_gateway
        payload = {"ipconfig0": "ip=" + self.subnet_cidr + "," "gw=" + self.gateway + "," "ip6=" + self.ipv6_address + '/' + ipv6_subnetmask + "," + "gw6=" + self.ipv6_gateway}
        ip_set = requests.post(self.url + "nodes/" + self.node_name + "/qemu/" + self.proxmox_vm_id + "/config", headers=self.proxmox_header,
                               cookies=self.proxmox_cookie,
                               verify=False, data=payload)
        if 'errors' in ip_set.json():
            print ('There is an error with cloud init, check output:')
            print (ip_set.json())
    def set_proxmox_delete_vm(self,vm_id_to_delete):
        self.vm_id_to_delete = vm_id_to_delete
        payload = {"purge": "1", "destroy-unreferenced-disks" : "1"}
        vm_delete = requests.delete(self.url + "nodes/", self.node_name + "/qemu/" + self.vm_id_to_delete + "/purge", headers=self.proxmox_header,
                                  cookies=self.proxmox_cookie,verify=False,data=payload)

    def set_proxmox_drive_size(self,drive_size):
        self.drive_size = drive_size
        payload = {"disk": "scsi0", "size": "+" + self.drive_size}
        resize_disk = requests.put(self.url + "nodes/" + self.node_name + "/qemu/" + self.new_vm_id + "/resize",headers=self.proxmox_header,
                                 cookies=self.proxmox_cookie,
                                 verify=False, data=payload)
    def set_proxmox_interface_vlan_id(self,new_vmid,vlan_id):
        self.vlan_id = vlan_id
        self.new_vm_id = new_vmid
        new_vm_int = self.proxmox_vm_int_config.replace('tag=10','tag='+self.vlan_id)
        #this is how you have to pass this data in
        #payload = {"net0": 'virtio=56:3E:8A:93:B3:AF,bridge=vmbr4,tag='+self.vlan_id}
        payload = {"net0": new_vm_int }
        interface_vlan = requests.post(self.url + "nodes/" + self.node_name + "/qemu/" + self.new_vm_id + "/config",headers=self.proxmox_header,
                                 cookies=self.proxmox_cookie,
                                 verify=False, data=payload)
    def get_proxmox_vm_interface_config(self,proxmox_vm_id):
        self.proxmox_vm_interface = requests.get(self.url + "nodes/" + self.node_name + "/qemu/" + self.proxmox_vm_id + "/config", cookies=self.proxmox_cookie,
                                 verify=False)
        self.proxmox_vm_int_config = self.proxmox_vm_interface.json()['data']['net0']



