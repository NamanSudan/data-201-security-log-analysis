-- host_fqdn: 1NF child table for host FQDNs (20 rows)
-- 1:N relationship. 7 hosts have 0 FQDNs (no rows).
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE host_fqdn (
    host_id INT NOT NULL REFERENCES host(host_id),
    fqdn    VARCHAR(255) NOT NULL,
    PRIMARY KEY (host_id, fqdn)
);