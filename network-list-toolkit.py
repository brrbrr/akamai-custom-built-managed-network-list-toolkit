import logging
import argparse
import os
import sys
import requests
import urllib.request
import csv
import ipaddress
from time import sleep
from akamai.edgegrid import EdgeGridAuth, EdgeRc

# Setup logging
logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger()

# Argparse will help manage command line arguments
parser = argparse.ArgumentParser(description='Custom-Built Managed Network List Toolkit',
                                 epilog='Built for automation of network list - bbrouard 2023',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# Let's add a positional argument
parser.add_argument('name', metavar='list-name', type=str, help='The name of our network list.')

# Let's add optional arguments
parser.add_argument('--file', action="store", default=os.getcwd() + "/list.csv", help="Path to CSV file with IPs for the network list.")
parser.add_argument('--delimiter', action="store", default=',', help="CSV delimiter used. Default=\',\'")
parser.add_argument('--url', action="store", help="URL to CSV file with IPs for the network list.")
parser.add_argument('--action', action="store", default='append', help="The action to take on the network list. Supported options are: append or overwrite.")
parser.add_argument('--network', action="store", help="Activation network: production or staging")
parser.add_argument('--email', action="store", default='noreply@example.com', help="Comma delimited e-mail list, for activation e-mail notifications.")
parser.add_argument('--comment', action="store", default="None.", help="Activation comments.")

# Let's add edgerc options for flexibility
parser.add_argument('--config', action="store", default=os.environ['HOME'] + "/.edgerc", help="Full or relative path to .edgerc file")
parser.add_argument('--section', action="store", default="default", help="The section of the edgerc file with the proper {OPEN} API credentials.")
parser.add_argument('--accountkey', action="store", help="Pass an account switch key in a request to manage an account different from the one in which you created your client.")

args = parser.parse_args()

""" 
##########################################
Edgegrid auth
##########################################
"""
try:
    edgerc = EdgeRc(args.config)
    baseurl = 'https://%s' % edgerc.get(args.section, 'host')
    if args.accountkey:
        ask = 'accountSwitchKey=' + args.accountkey
    else: 
        try:
            ask = 'accountSwitchKey=%s' % edgerc.get(args.section, 'account_key')  
        except Exception:
            ask = ''
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, args.section)
    log.debug('API Base URL: ' + baseurl)

except Exception as e:
    log.error('Error authenticating Akamai {OPEN} API client.')
    log.error(e)

""" 
##########################################
START OF THE SRIPT
##########################################
"""
log.info('Updating network list \'' + args.name + '\'. Action: ' + args.action)

# Find our list, using the 'name' argument and obtain the Network List ID
endpoint = baseurl + '/network-list/v2/network-lists?' + ask + '&search=' + args.name
result = session.get(endpoint).json()

# Check that the list exists, and there is no ambiguity (more than 1 list)
if len(result['networkLists']) != 1:
    log.error('Network list \'' + args.name + '\' not found. Please verify the name. Exiting.')
    parser.print_help()
    sys.exit(1)

# Initialize the listID as a variable
listId = result['networkLists'][0]['uniqueId']

# Get the list details
endpoint = baseurl + '/network-list/v2/network-lists/' + listId + '?' + ask
result = session.get(endpoint).json()


# Fetch the list based on the supplied action (url or file)
if args.url:
    #Dowload list of IP from the URL provided and placing into list.csv file
    urllib.request.urlretrieve(args.url, args.file)  
    log.info('Downloading CSV file at URL: ' + args.url)

# Ensure that the file exists
if not os.path.isfile(args.file):
    log.error('No input file was found or provided. Exiting.')
    parser.print_help()
    sys.exit(1)

# Open the file
try:
    with open(args.file, 'r') as csvfile:
        # Read in file contents as a list
        csvreader = csv.reader(csvfile, delimiter=args.delimiter, dialect="excel")
        log.info('Reading input file: ' + args.file + '. Size (bytes): ' + str(os.stat(args.file).st_size))
        # We'll use this list to hold our IPs
        sanitizedIps = []
        # Open the CSV file and read each row
        for row in csvreader:
            # Loop over each column in the row
            for value in row:
                try:
                    ipaddress.ip_address(value)
                    sanitizedIps.append(value)
                except ValueError:
                    continue
        log.info('Found ' + str(len(sanitizedIps)) + ' IP addresses in the list. Network List \'' + args.name + '\' previously had ' + str(result['elementCount']) + ' items.')       
except Exception as e:
    log.error('Error encountered opening CSV file: ' + args.file)
    log.error(e)


# Generating payload using python Dict operations
log.info('Generating JSON payload for Network Lists API...')
result['list'] = sanitizedIps

log.info('Updating network list: ' + args.name)
endpoint = baseurl + '/network-list/v2/network-lists/' + listId

# Update the list based on the supplied action (overwrite or append)
if args.action == 'append':
    endpoint = endpoint  + '/append' + '?' + ask
    # Append requires simplified payload
    result = {"list": sanitizedIps}
    # Append requires POST method
    method = 'POST'
else:
    # Overwrite (update) requires PUT method
    endpoint = endpoint  + '?' + ask
    method = 'PUT'

result = session.request(method, endpoint, json=result, headers={'Content-Type': 'application/json'})

# check status code and log result if not 202
if result.status_code != 202:
    log.error('Update failed. Status Code: ' + str(result.status_code) + '. Result: ' + result.text)
    sys.exit(1)
else:
    log.info('Update complete. Status Code: ' + str(result.status_code))

    ################################### ACTIVATION
    if args.network:
        log.info('Activating network list \'' + args.name + '\' on ' + args.network.upper() + ' network.')

        def checkStatus(listId, network):
            endpoint = baseurl + '/network-list/v2/network-lists/' + listId + '/environments/' + network.upper() + '/status' + '?' + ask
            result = session.get(endpoint).json()
            return result

        result = checkStatus(listId, args.network)
        if result['activationStatus'] == 'ACTIVE':
            log.error('Network List \'' + args.name + '\' is already active. Exiting.')
            log.info(result)
            sys.exit(1)

        log.info('Creating activation payload.')
        emailList = args.email.split(",")
        endpoint = baseurl + '/network-list/v2/network-lists/' + listId + '/environments/' + args.network.upper() + '/activate' + '?' + ask
        payload = { "comments": args.comment, "notificationRecipients": emailList}
        result = session.post(endpoint, json=payload, headers={'Content-Type': 'application/json'}).json()

        if not result['activationId']:
            log.error('Error requesting activation. Exiting.')
            sys.exit(1)

        log.info('Activation request on network: ' + args.network + ' complete. Activation Id: ' + str(result['activationId']))
        result = checkStatus(listId, args.network)

        while result['activationStatus'] != 'ACTIVE':
            log.info('Activation status on ' + args.network.upper() + ': ' + result['activationStatus'])
            result = checkStatus(listId, args.network)
            sleep(10)

        log.info('Activation complete in network: ' + args.network + '. Status: ' + result['activationStatus'])