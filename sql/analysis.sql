-- ================================================
-- Web Log Analysis Queries
-- ================================================

-- 1. Overview: Total requests, unique IPs, unique paths
SELECT 
    COUNT(*) as total_requests,
    COUNT(DISTINCT ip) as unique_visitors,
    COUNT(DISTINCT path) as unique_pages
FROM web_logs.access_logs;


-- 2. Requests by HTTP status code
-- 200 = OK, 304 = Not Modified, 404 = Not Found, 500 = Server Error
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM web_logs.access_logs
GROUP BY status
ORDER BY count DESC;


-- 3. Top 10 most visited pages
SELECT 
    path,
    COUNT(*) as visits
FROM web_logs.access_logs
GROUP BY path
ORDER BY visits DESC
LIMIT 10;


-- 4. Top 10 most active IP addresses
-- High request counts from single IP could indicate bots or attacks
SELECT 
    ip,
    COUNT(*) as requests,
    COUNT(DISTINCT path) as unique_pages
FROM web_logs.access_logs
GROUP BY ip
ORDER BY requests DESC
LIMIT 10;


-- 5. HTTP methods breakdown
SELECT 
    method,
    COUNT(*) as count
FROM web_logs.access_logs
GROUP BY method
ORDER BY count DESC;


-- 6. Failed requests (4xx and 5xx status codes)
-- These indicate errors - client errors or server problems
SELECT 
    status,
    path,
    COUNT(*) as count
FROM web_logs.access_logs
WHERE status >= 400
GROUP BY status, path
ORDER BY count DESC
LIMIT 20;


-- 7. Potential security threats: Suspicious paths
-- Looking for common attack patterns
SELECT 
    path,
    COUNT(*) as attempts
FROM web_logs.access_logs
WHERE 
    path LIKE '%..%'           -- Directory traversal
    OR path LIKE '%/etc/%'     -- Linux system files
    OR path LIKE '%passwd%'    -- Password files
    OR path LIKE '%.php%'      -- PHP exploits
    OR path LIKE '%/admin%'    -- Admin pages
    OR path LIKE '%wp-%'       -- WordPress exploits
    OR path LIKE '%<script%'   -- XSS attempts
GROUP BY path
ORDER BY attempts DESC
LIMIT 20;


-- 8. Traffic by hour of day
-- Helps identify peak usage times
SELECT 
    EXTRACT(HOUR FROM PARSE_TIMESTAMP('%d/%b/%Y:%H:%M:%S %z', timestamp)) as hour,
    COUNT(*) as requests
FROM web_logs.access_logs
GROUP BY hour
ORDER BY hour;


-- 9. IPs with high error rates
-- Could indicate attackers probing for vulnerabilities
SELECT 
    ip,
    COUNT(*) as total_requests,
    COUNTIF(status >= 400) as errors,
    ROUND(COUNTIF(status >= 400) * 100.0 / COUNT(*), 2) as error_rate
FROM web_logs.access_logs
GROUP BY ip
HAVING COUNT(*) > 10
ORDER BY error_rate DESC
LIMIT 10;


-- 10. Bandwidth usage by IP
-- Large size values could indicate data exfiltration
SELECT 
    ip,
    COUNT(*) as requests,
    SUM(size) as total_bytes,
    ROUND(SUM(size) / 1024.0 / 1024.0, 2) as total_mb
FROM web_logs.access_logs
GROUP BY ip
ORDER BY total_bytes DESC
LIMIT 10;


-- 11. Investigate suspicious IP with single page requests
SELECT 
    ip,
    path,
    COUNT(*) as hits
FROM web_logs.access_logs
WHERE ip = '46.105.14.53'
GROUP BY ip, path;


-- 12. Find IPs making attack attempts
SELECT 
    ip,
    COUNT(*) as attack_attempts,
    COUNT(DISTINCT path) as paths_tried
FROM web_logs.access_logs
WHERE 
    path LIKE '%wp-%'
    OR path LIKE '%/admin%'
    OR path LIKE '%.php%'
GROUP BY ip
ORDER BY attack_attempts DESC
LIMIT 10;

