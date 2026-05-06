-- host_ipv4: 1NF child table for host IPv4 addresses (24 rows)
-- 1:N relationship. 21 hosts x 1 + inet-firewall x 3.
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE host_ipv4 (
    host_id      INT NOT NULL REFERENCES host(host_id),
    ipv4_address VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv4_address)
);