-- os_release: 3NF lookup table for OS releases (2 rows)
-- Resolves transitive dependency: distribution_release -> distribution, distribution_version
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE os_release (
    os_release_id        SERIAL PRIMARY KEY,
    distribution_release VARCHAR(20) NOT NULL UNIQUE,
    distribution         VARCHAR(50) NOT NULL,
    distribution_version VARCHAR(20) NOT NULL
);