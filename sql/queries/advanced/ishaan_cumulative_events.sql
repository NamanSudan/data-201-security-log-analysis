SELECT date, day_events,
       SUM(day_events) OVER (ORDER BY date) AS cumulative_events
FROM (
  SELECT DATE(timestamp) AS date, COUNT(*) AS day_events
  FROM audit_event
  GROUP BY DATE(timestamp)
) 
ORDER BY date;
