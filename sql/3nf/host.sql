-- host: Central host reference entity (22 rows)
-- One row per testbed machine. host_key is the cross-domain integration key.
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE host (
    host_id              SERIAL PRIMARY KEY,
    host_key             VARCHAR(50) NOT NULL UNIQUE,
    hostname             VARCHAR(100) NOT NULL UNIQUE,
    username             VARCHAR(50),
    openvpn_user         VARCHAR(50),
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    timezone             VARCHAR(10) NOT NULL,
    os_release_id        INT NOT NULL REFERENCES os_release(os_release_id)
);