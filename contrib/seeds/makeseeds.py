#!/usr/bin/env python
#
# Generate seeds.txt from Pieter's DNS seeder
#

NSEEDS=512

MAX_SEEDS_PER_ASN=2

MIN_BLOCKS = 200000

# These are hosts that have been observed to be behaving strangely (e.g.
# aggressively connecting to every node).
SUSPICIOUS_HOSTS = set([
    "18.218.20.171", "18.191.141.168", "10.211.55.7",
    "127.0.0.1"
])

import re
import sys
import dns.resolver

PATTERN_IPV4 = re.compile(r"^((\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})):1993$")
PATTERN_AGENT = re.compile(r"^(\/Satoshi:0.8.6\/|\/Satoshi:0.9.(2|3)\/|\/Core:0.1(0|1|2).\d{1,2}.\d{1,2}\/)$")

def parseline(line):
    sline = line.split()
    if len(sline) < 11:
       return None
    # Match only IPv4
    m = PATTERN_IPV4.match(sline[0])
    if m is None:
        return None
    # Do IPv4 sanity check
    ip = 0
    for i in range(0,4):
        if int(m.group(i+2)) < 0 or int(m.group(i+2)) > 255:
            return None
        ip = ip + (int(m.group(i+2)) << (8*(3-i)))
    if ip == 0:
        return None
    # Skip bad results.
    if sline[1] == 0:
        return None
    # Extract uptime %.
    uptime30 = float(sline[7][:-1])
    # Extract Unix timestamp of last success.
    lastsuccess = int(sline[2])
    # Extract protocol version.
    version = int(sline[10])
    # Extract user agent.
    agent = sline[11][1:-1]
    # Extract service flags.
    service = int(sline[9], 16)
    # Extract blocks.
    blocks = int(sline[8])
    # Construct result.
    return {
        'ip': m.group(1),
        'ipnum': ip,
        'uptime': uptime30,
        'lastsuccess': lastsuccess,
        'version': version,
        'agent': agent,
        'service': service,
        'blocks': blocks,
    }

# Based on Greg Maxwell's seed_filter.py
def filterbyasn(ips, max_per_asn, max_total):
    result = []
    asn_count = {}
    for ip in ips:
        if len(result) == max_total:
            break
        try:
            asn = int([x.to_text() for x in dns.resolver.query('.'.join(reversed(ip['ip'].split('.'))) + '.origin.asn.cymru.com', 'TXT').response.answer][0].split('\"')[1].split(' ')[0])
            if asn not in asn_count:
                asn_count[asn] = 0
            if asn_count[asn] == max_per_asn:
                continue
            asn_count[asn] += 1
            result.append(ip)
        except:
            sys.stderr.write('ERR: Could not resolve ASN for "' + ip['ip'] + '"\n')
    return result

def main():
    lines = sys.stdin.readlines()
    ips = [parseline(line) for line in lines]

    # Skip entries with valid IPv4 address.
    ips = [ip for ip in ips if ip is not None]
    # Skip entries from suspicious hosts.
    ips = [ip for ip in ips if ip['ip'] not in SUSPICIOUS_HOSTS]
    # Enforce minimal number of blocks.
    ips = [ip for ip in ips if ip['blocks'] >= MIN_BLOCKS]
    # Require service bit 1.
    ips = [ip for ip in ips if (ip['service'] & 1) == 1]
    # Require at least 50% 30-day uptime.
    ips = [ip for ip in ips if ip['uptime'] > 50]
    # Require a known and recent user agent.
    ips = [ip for ip in ips if PATTERN_AGENT.match(ip['agent'])]
    # Sort by availability (and use last success as tie breaker)
    ips.sort(key=lambda x: (x['uptime'], x['lastsuccess'], x['ip']), reverse=True)
    # Look up ASNs and limit results, both per ASN and globally.
    ips = filterbyasn(ips, MAX_SEEDS_PER_ASN, NSEEDS)
    # Sort the results by IP address (for deterministic output).
    ips.sort(key=lambda x: (x['ipnum']))

    for ip in ips:
        print ip['ip']

if __name__ == '__main__':
    main()
