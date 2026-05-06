SELECT h.host_key,
       h.hostname,
       (SELECT COUNT(*) FROM labeled_line ll WHERE ll.source_host = h.host_key) AS labeled_lines
FROM host h
WHERE EXISTS (
    SELECT 1
    FROM labeled_line ll
    WHERE ll.source_host = h.host_key
)
  AND NOT EXISTS (
    SELECT 1
    FROM audit_event ae
    WHERE ae.host_id = h.host_id
)
ORDER BY labeled_lines DESC;
