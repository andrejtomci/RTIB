# network

Setup iptables firewall.

Already present iptables are flushed. Localhost, ssh from attacker and connections from expected addresses are allowed. 
Then, the rest of the connections are restricted and persistency is achieved via *iptables-persistent*.

# Arguments
- **accept_from**: list of addresses to allow connection from (can also be a name of an another infrastructure component)
- **attacker**: address of the attacker