#Fill in info with IPs/DNS and login/api information for use within script
#Anything with [] update to change the value of, and also delete the []
class Secrets:
    phpipam = {'api_url': 'http://[PHPIAM_DNS/IP NAME]/api/[APP_ID]/',
               'basic_auth_value' : '[Basic encoded app code ]', #defined in administration >API
               'dns_domain_name' : '[DNS_SUFFIX]',
               'ipam_section_ipv4' : '[NAME_OF_IPAM_SECTION]',
               'ipam_section_ipv6' : '[NAME_OF_IPAM_SECTION]'}
    proxmox = {'proxmox_ip' : '[PROXMOX_IP/DNS_NAME]',
               'proxmox_user' : '[USERNAME]',
               'proxmox_password' : '[PASSWORD]',
               'proxmox_realm' : '[REALM - IE PAM]'}
    librenms = {'librenms_ip' : '[LIBRENMS IP/DNS_NAME]',
                'auth_tocken' : '[API TOKEN]'} #defined under settings > API > API Settings
    mysql = {'db_ip' : '[MYSQL IP/DNS_NAME]',
             'username': '[DB USERS]',
             'password' : '[DB PASSWORD]',
             'ipv4_table_name' : '[TABLE NAME]',
             'ipv6_table_name' : '[TABLE NAME]',
             'ipv4_db_name' : '[DB NAME]',
             'ipv6_db_name' : '[DB NAME]'}
    