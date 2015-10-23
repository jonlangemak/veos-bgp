
from jsonrpclib import Server
import ssl
import dns
import json
from prettytable import PrettyTable
import datetime
import time

from dns import resolver
from dns import reversename

res = dns.resolver.Resolver()
res.nameservers = ['10.20.30.13']


# Deal with self signed certificate
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:

    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

switch = Server("https://vagrant:vagrant@localhost:8443/command-api")
response = switch.runCmds(1, ["show ip bgp summary"])

# print json.dumps(response, indent=4, sort_keys=True)


table = PrettyTable(["Peer", "DNS Name", "ASN", "State", "Up Down Time"])

for peers in response[0]['vrfs']['default']['peers']:
    try:
        addr = reversename.from_address(peers)
        resolved = res.query(addr, "PTR")[0]
    except dns.resolver.NXDOMAIN:
        resolved = "No DNS record"

    asn = response[0]['vrfs']['default']['peers'][peers]['asn']

    epoch = response[0]['vrfs']['default']['peers'][peers]['upDownTime']

    state = response[0]['vrfs']['default']['peers'][peers]['peerState']

    udtime = time.time() - epoch
    udtime = datetime.timedelta(seconds=udtime)
    udtime = str(udtime).split(".")[0]

    table.add_row([peers, resolved, asn, state, udtime])

print table
