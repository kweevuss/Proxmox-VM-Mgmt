import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPBasicAuth
import json
import sys
sys.path.append("..")
from secrets import Secrets


class Phpipam():
    def __init__(self):
        self.phpipam_url_base = Secrets.phpipam['api_url']
        self.header = {"Authorization": Secrets.phpipam['basic_auth_value']}

    def phpipam_login(self):
        reponse = requests.post(self.phpipam_url_base + "user/", headers=self.header)
        self.phpipam_token = reponse.json()['data']['token']
        self.header_token = {"token": self.phpipam_token}

    def get_phpipam_sections(self,phpipam_section_name):
        self.phpipam_section_name = phpipam_section_name
        response_section = requests.get(self.phpipam_url_base + "sections/", headers=self.header_token)
        for section in response_section.json()['data']:  # This loops through the json response, and get's the data dict, which includes all the sections
            if section['name'] == self.phpipam_section_name:  # filter by the name of the section that we are looking for
                self.phpipam_section_id = section['id'] # Once we filter on what we want, return the ID value which will be used for other queries

    def get_phpipam_subnets(self):
        response = requests.get(self.phpipam_url_base + "sections/" + str(self.phpipam_section_id) + "/subnets/",
                                headers=self.header_token)  # get all sections ie customers
        self.subnetinfo = {}  # empty dict for holding the subnet and ID info
        for section in response.json()['data']:  # loop through all the subnets within the data portion of json
            self.subnetinfo[section['subnet']] = section['id']  # write to dictonary with key of subnet in network and then the ID as value
            # Ex: {'192.168.9.0': '8', '192.168.10.0': '7'}

    def get_phpipam_nextip(self,phpipam_subnet_query):
        self.phpipam_subnet_query = phpipam_subnet_query
        response = requests.get(self.phpipam_url_base + "subnets/" + str(self.subnetinfo[self.phpipam_subnet_query]) + "/first_free/", headers=self.header_token)
        self.phpipam_next_ip = response.json()['data']
    
    def get_phpipam_subnet_id(self,phpipam_subnet_query):
        #this is similar to get next ip, but because for ipv6 we do not need next IP, need to break out getting that next IP. probably should change ipv4 to use this one
        self.phpipam_subnet_query = phpipam_subnet_query #this is just used later in set phpipam_ip 

    def set_phpipam_ip(self,new_vm_name):
        subnet_id = self.subnetinfo[self.phpipam_subnet_query]
        self.new_vm_name = new_vm_name
        self.post_header = {"token": self.phpipam_token}
        self.patch_data = {"hostname": self.new_vm_name+Secrets.phpipam['dns_domain_name']}
        response = requests.post(self.phpipam_url_base + "addresses/first_free/"+str(subnet_id)+"/", headers=self.post_header)
        response_patch = requests.patch(self.phpipam_url_base + "addresses/" + str(response.json()['id']), headers=self.post_header, data=self.patch_data )
        if response_patch.json()['code'] == 200:
            print ('Was able to write IP to IPAM')
        else:
            print ('something went wrong with creating IPAM IP:')
            print (response_patch.json())
    def set_phpipam_specific_ip(self,new_vm_name,ip):
        subnet_id = self.subnetinfo[self.phpipam_subnet_query]
        self.new_vm_name = new_vm_name
        self.new_ip = ip
        self.post_header = {"token": self.phpipam_token}
        self.patch_data = {"hostname": self.new_vm_name+Secrets.phpipam['dns_domain_name'], "ip" : self.new_ip, "subnetId" : subnet_id}
        response = requests.post(self.phpipam_url_base + "addresses/", headers=self.post_header, data=self.patch_data)
        print (response.json())
    