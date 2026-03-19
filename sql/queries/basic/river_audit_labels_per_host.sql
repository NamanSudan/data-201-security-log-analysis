SELECT h.hostname,
       h.host_key,
       COUNT(ae.event_id) AS event_count
FROM host h
INNER JOIN audit_event ae ON ae.host_id = h.host_id
GROUP BY h.host_id, h.hostname