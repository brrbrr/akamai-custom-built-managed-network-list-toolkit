
<!--- These are examples. See https://shields.io for others or to customize this set of shields. You might want to include dependencies, project status and licence info here --->
![GitHub repo size](https://img.shields.io/github/repo-size/brrbrr/network-list-toolkit)
![GitHub contributors](https://img.shields.io/github/contributors/brrbrr/network-list-toolkit)
![GitHub stars](https://img.shields.io/github/stars/brrbrr/network-list-toolkit?style=social)
![GitHub forks](https://img.shields.io/github/forks/brrbrr/network-list-toolkit?style=social)
# Custom-Built Managed Network List Toolkit

This Custom-Built Managed Network List Toolkit allow you the automation of Akamai network lists.
It perform the following functions:

1. Update existing Network List from source or distant (via URL) CSV file
2. Activate the Network List on either production or staging networks
> Note: This toolkit is based on the [Akamai Network List API](https://techdocs.akamai.com/network-lists/reference/api).
## Introduction
Akamai Network lists are used to manage collections of IP addresses/CIDR blocks (v4 or v6) or geographic locations.
The beauty of Network Lists is that you can edit addresses within a network list at any time, without having to edit and reactivate your security policy configuration.

Akamai​ creates and offers packaged network lists for you to use. These lists feature a wave icon beside their name and are usually collections of IP addresses around a common theme, like cloud service networks you may use. These lists are *read-only*, which means you can't edit them, but you can duplicate and edit your own copy.

You can also create your own custom network lists. For example, say you want to allow all your internal IP addresses and those belonging to your vendors. You'd collect them in a network list and activate it. Then in a security policy, you'd use IP/Geo controls to allow all requests from that list. 

But what if my partner is updating his IP addresses on a regular basis ?
1. You can update manually the network list via the Akamai Control Center
2. You can use this Custom-Built Managed Network List Toolkit

Thus if your partner is providing you locally or remotely (via URL) the list of IP address in a CSV format file, scheduling to run this script on regular basis (via a CRON job, Jenkins, etc.) will allow you to keep your network-list up to date.


> Note: You can include up to 50,000 IP addresses or CIDR blocks per network list and activate up to 32 lists per security configuration. That number includes the following feature-related lists, created automatically: Reputation Allow List, Match Target Bypass List, Rate Controls Bypass List. If you have more than 50,000 IPs, you can split into 2 or more network lists.

## Requirements
Before you begin, ensure you have met the following requirements:

- Python 3.x
- akamai-edgegrid (Python client for Akamai APIs)
- requests
- argparse
- csv
- ipaddress


## Usage
```python
python3 network-list-toolkit.py list-name [--file] [--delimiter] [--url] [--action] [--network] [--email] [--comment] [--config] [--section] [--accountkey]
```

## Arguments

- `list-name`: the name of the network list to modify.
- `--file`: path to CSV file with IPs for the network list. Default is list.csv in current directory.
- `--delimiter`: CSV delimiter used. Default is ,.
- `--url`: URL to CSV file with IPs for the network list.
- `--action`: the action to take on the network list. Supported options are append (default) or overwrite.
- `--network`: activation network: production or staging.
- `--email`: comma-delimited email list for activation email notifications.
- `--comment`: activation comments.
- `--config`: full or relative path to .edgerc file. Default is ~/.edgerc.
- `--section`: the section of the .edgerc file with the proper {OPEN} API credentials. Default is default.
- `--accountkey`: pass an account switch key in a request to manage an account different from the one in which you created your client.

## Authentication
Authentication is handled through Akamai EdgeGrid in the _provider.tf_ file.
Ensure you have your _.edgerc_ file available and that it contains your Akamai EdgeGrid tokens separated in sections.

```bash
[default]
client_secret = xxxx
host = xxxx # unique string followed by `luna.akamaiapis.net`
access_token = xxxx
client_token = xxxx
max-body = xxxx
#account_key = xxxxx # specify the Account Switch Key to handle another another account with your Akamai Internal Credentials
```

For more information on Akamai EdgeGrid, _.edgerc_ file and creating Akamai EdgeGrid tokens, see ['Get started with APIs'](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials).

# Contributing

We're happy to accept help from fellow code-monkeys.
Report issues/questions/feature requests on in the [issues](https://github.com/brrbrr/network-list-toolkit/issues) section.
Refer to the [contribution guidelines](./contributing.md) for information on contributing to this module.

# Authors

- [@Benjamin Brouard](https://www.github.com/brrbrr), Security Professional Services @Akamai.

# License

[Apache License 2](https://choosealicense.com/licenses/apache-2.0/). See [LICENSE](./LICENSE.md) for full details.
