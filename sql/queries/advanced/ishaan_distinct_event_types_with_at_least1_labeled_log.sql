SELECT DISTINCT
  e.type
FROM audit_event e
WHERE EXISTS (
  SELECT 1
  FROM host h
  JOIN labeled_line ll
    ON ll.source_host = h.host_key
  WHERE h.host_id = e.host_id
);
