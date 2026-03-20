SELECT h.host_key, DATE(e.timestamp) AS event_date, COUNT(*) AS events_that_day,
  RANK() OVER (
    PARTITION BY h.host_key
    ORDER BY COUNT(*) DESC
  ) AS day_rank_for_host
FROM audit_event e
JOIN host h
  ON h.host_id = e.host_id
GROUP BY h.host_key, DATE(e.timestamp)
ORDER BY h.host_key, day_rank_for_host, event_date;
