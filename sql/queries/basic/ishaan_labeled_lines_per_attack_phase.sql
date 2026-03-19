SELECT ap.phase_name, COUNT(*) AS labeled_lines
FROM attack_phase ap
JOIN attack_label al 
ON al.phase_id = ap.phase_id
JOIN labeled_line_label lll 
ON lll.label_id = al.label_id
GROUP BY ap.phase_name
ORDER BY labeled_lines DESC;
