SELECT ap.phase_name,
       COUNT(al.label_id) AS label_count
FROM attack_phase ap
FULL OUTER JOIN attack_label al ON al.phase_id = ap.phase_id
GROUP BY ap.phase_id, ap.phase_name
ORDER BY label_count DESC;