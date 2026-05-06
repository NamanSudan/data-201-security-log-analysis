SELECT source_host,
       COUNT(*) AS labeled_line_count
FROM labeled_line
GROUP BY source_host
ORDER BY labeled_line_count DESC;