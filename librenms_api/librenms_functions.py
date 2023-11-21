import requests
import time
import sys
sys.path.append("..")
from secrets import Secrets
class Librenms():
    def __init__(self):
        self.librenms_base_url = f"http://{Secrets.librenms['librenms_ip']}/api/v0"
        self.librenms_header = {'X-Auth-Token' : Secrets.librenms['auth_tocken']}

    def librenms_get_device_status(self,device_name):
        self.librenms_device_name = device_name
        self.device_status_response = requests.get(self.librenms_base_url, "/devices/" + self.librenms_device_name + "/", headers=self.librenms_header)

    def librenms_add_device(self,device_name,snmp_community):
        self.librenms_device_name = device_name
        self.librenms_snmp_community = snmp_community
        device_data = {"hostname":self.librenms_device_name, "community" : self.librenms_snmp_community}
        self.device_add_response = requests.post(self.librenms_base_url + "/devices", headers=self.librenms_header, json=device_data)
        
    def librenms_delete_device(self,device_name):
        self.librenms_device_name = device_name
        self.device_delete_response = requests.delete(self.librenms_base_url + "/devices/" + self.librenms_device_name, headers=self.librenms_header)
        