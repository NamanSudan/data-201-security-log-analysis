SELECT
  m.acct,
  h.host_key,
  COUNT(*) AS event_count,
  RANK() OVER (
    PARTITION BY m.acct
    ORDER BY COUNT(*) DESC
  ) AS host_rank_for_acct
FROM audit_event e
JOIN host h
  ON h.host_id = e.host_id
JOIN audit_message m
  ON m.event_id = e.event_id
WHERE m.acct IS NOT NULL
GROUP BY m.acct, h.host_key
ORDER BY m.acct, host_rank_for_acct, h.host_key;
