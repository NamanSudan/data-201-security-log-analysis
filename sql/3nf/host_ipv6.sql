-- host_ipv6: 1NF child table for host IPv6 addresses (24 rows)
-- 1:N relationship. Same cardinality pattern as host_ipv4.
-- Reference snapshot -- canonical schema is in src/models/final/host.py

CREATE TABLE host_ipv6 (
    host_id      INT NOT NULL REFERENCES host(host_id),
    ipv6_address VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv6_address)
);
