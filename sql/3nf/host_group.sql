-- host_group: 1NF junction table for host group membership (63 rows)
-- M:N bridge, all-key composite PK. 17 distinct groups.
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE host_group (
    host_id    INT NOT NULL REFERENCES host(host_id),
    group_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (host_id, group_name)
);