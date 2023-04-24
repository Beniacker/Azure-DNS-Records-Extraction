# Azure-DNS-Records-Extraction

The purpose of the code is to extract subdomains from Azure DNS zones using the Microsoft Azure Management API.

The code uses several Python libraries such as sys, datetime, requests, re, json, time, and argparse for handling arguments, making API requests, parsing JSON data, regular expressions, and time delays.

The main logic of the code consists of the following steps:

1. It sets up the API authorization token and headers.
2. It extracts a list of Azure subscriptions associated with the provided authorization token.
3. For each subscription, it extracts a list of DNS zones.
4. For each DNS zone, it extracts a list of DNS records and filters out unwanted subdomains using regular expressions.
5. It saves the list of extracted subdomains to a file.

The final output of the code is a list of subdomains that are associated with Azure DNS zones.
