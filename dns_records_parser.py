import sys
from datetime import datetime
import requests
import re
import json
import time
import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("-t", "--token", dest="value", help="Authorization header (Bearer eyJ0eXAiOi...)", required=True)
# auth_token = parser.parse_args()
# headers = {"Authorization": auth_token.value}

token = "Bearer eyJ0eXA..."
headers = {"Authorization": token}

# ### extract all subdomains
# def extract_subdomains(dns_records_list):
#     for record in dns_records_list:
#         subdomain = record["properties"]["fqdn"][:-1]
#         subdomains_list.append(subdomain)
#         print(subdomain)
#     print(f"Total of {len(subdomains_list)} subdomains")
#     return

### extract filtered subdomains
def extract_subdomains(dns_records_list):
    bad_domains_regex = re.compile('[@!#$%^&*()<>?/|}{~:]|domainkey|^_|localhost')
    remove_hash_string = re.compile(('^[\w-]{32}\.'))
    for record in dns_records_list:
        if ("CNAMERecord" in record["properties"].keys() or \
                "ARecords" in record["properties"].keys() or \
                "AAAARecords" in record["properties"].keys()):

            subdomain = record["properties"]["fqdn"][:-1]
            if not bad_domains_regex.search(subdomain):
                if "www." in subdomain:
                    subdomain = subdomain.replace("www.", "")
                    subdomains_list.append(subdomain)
                elif remove_hash_string.search(subdomain):
                    subdomain = subdomain.replace(subdomain[:33], "")
                    subdomains_list.append(subdomain)
                else:
                    subdomains_list.append(subdomain)
                print(subdomain)
    return


def extract_dns_records(records_url):
    req_dns_records = requests.get(records_url, headers=headers, verify=True)
    records = json.loads(req_dns_records.text)
    # print(f"\n", f"### Current {len(subdomains_list)} DNS Records:", records)

    dns_records_list = records["value"]
    extract_subdomains(dns_records_list)

    next_page = []
    if "nextLink" in records:
        next_page = records["nextLink"]
    return next_page


### Get Subscriptions ###
get_sub_list = "https://management.azure.com/subscriptions?api-version=2020-01-01"
req = requests.get(get_sub_list, headers=headers, verify=True)
if req.status_code != 200:
    sys.exit("Token not valid")
subs_json = json.loads(req.text)
subs_list_json = subs_json["value"]
subs_list_extracted = []
for sub in subs_list_json:
    subs_list_extracted.append(sub["subscriptionId"])
print(f"Total of {len(subs_list_extracted)} Subscriptions was found!", "\n")
# print(subs_list_extracted, "\n")


### Get DNS zones from each Subscription ###
time.sleep(1)
sub_pattern = "subscriptions/(.*)/resourceGroups"
rg_pattern = "resourceGroups/(.*)/providers"
rg_list = []
sub_list = []
dns_zone_list = []
ctr = 0
for sub in subs_list_extracted:
    get_dns_zones_list = f"https://management.azure.com/subscriptions/{sub}/providers/Microsoft.Network/dnszones?api-version=2018-05-01"
    req = requests.get(get_dns_zones_list, headers=headers, verify=True)
    dns_zones_json = json.loads(req.text)
    ctr += 1
    print(f"Response {ctr}/{len(subs_list_extracted)}: ", dns_zones_json)

    if "value" in req.text:
        dns_zones_list_json = dns_zones_json["value"]
        for zone in dns_zones_list_json:
            dns_zone_list.append(zone["name"])
            rg_list.append(re.search(rg_pattern, zone["id"]).group(1))
            sub_list.append(re.search(sub_pattern, zone["id"]).group(1))
        # print(f"# Listed {len(sub_list)} Subscriptions")
        # print(f"# Listed {len(rg_list)} Resource Groups")
        print(f"# Listed {len(dns_zone_list)} DNS Zones", "\n")

# print(f"\n", f"### Total {len(sub_list)} Subscriptions:", sub_list, "\n")
# print(f"### Total {len(rg_list)} Resource Groups:", rg_list, "\n")
print(f"### Total of {len(dns_zone_list)} DNS Zones was found!", "\n")


### Get DNS Records ###
time.sleep(1)
subdomains_list = []
print(f"### Searching for DNS Records:")
for sub, rg, dns_zone in zip(sub_list, rg_list, dns_zone_list):
    records_endpoint = f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/dnsZones/{dns_zone}/ALL?api-version=2018-05-01"
    nextPage = extract_dns_records(records_endpoint)
    while nextPage:
        print(f"\n", "### Found next page, going inside:", "\n", nextPage, "\n")
        nextPage = extract_dns_records(nextPage)


### Save to file ###
print(f"\n", "\n", "### Total of", len(subdomains_list), "subdomains was found!")
# print(f"# Subdomains:", subdomains_list)
subdomainUniqueList = sorted(set(subdomains_list))  # ordered + unique elements
print(f"### Total of {len(subdomainUniqueList)} after sorted and unique subdomains")
# print(f"# Subdomains:", subdomainUniqueList)

date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
with open(f"result_{date}.txt", 'w') as file:
    file.write('\n'.join(subdomainUniqueList))