IF OBJECT_ID('tempdb..#results', 'U') IS NOT NULL
	DROP TABLE #results
CREATE TABLE #results ( 
	[Report Type] VARCHAR(150),
	[Name] VARCHAR(250),
	[Description] VARCHAR(MAX),
	[Creation Date] DATE,
	[Modified Date] DATE, 
	[Average Execution Time (h:m:s:ms)] VARCHAR(50),
	[Link] VARCHAR(MAX),
	[Template Link] VARCHAR(MAX),
	[Group Contracts] VARCHAR(MAX),
	[Data Constraints] VARCHAR(MAX),
	[Input Fields] VARCHAR(MAX),
	[Original Requester] VARCHAR(MAX),
	[Download Template] VARCHAR(MAX)
)

IF OBJECT_ID('tempdb..#avg_time', 'U') IS NOT NULL
	DROP TABLE #avg_time
SELECT 
	p.id,
	CONVERT(varchar, DATEADD(ms,AVG(DATEDIFF(s, accesstime, completiontime))* 1000, 0), 114) average
INTO #avg_time
FROM REPORT.Dashboard.dbo.progress p
WHERE p.progress = 100
	AND p.completiontime IS NOT NULL
	AND p.accesstime > DATEADD(YEAR, -3, p.accesstime)
GROUP BY p.id

IF OBJECT_ID('tempdb..#report_creation_date') IS NOT NULL
	DROP TABLE #report_creation_date
SELECT 
	p.id,
	MIN(p.accesstime) creation_date
INTO #report_creation_date
FROM REPORT.Dashboard.dbo.progress p
GROUP BY p.id

IF OBJECT_ID('tempdb..#report_original_requester') IS NOT NULL
	DROP TABLE #report_original_requester
SELECT 
	p.id,
	MIN(p.username) original_requester
INTO #report_original_requester
FROM REPORT.Dashboard.dbo.progress p
GROUP BY p.id


INSERT INTO #results
(
    [Report Type],
    Name,
    Description,
    [Creation Date],
    [Modified Date],
    [Average Execution Time (h:m:s:ms)],
	[Link],
	[Template Link],
	[Group Contracts],
	[Original Requester],
	[Download Template]
)
SELECT 
	'UPHP Dashboard' AS FolderPath,
	r.report,
	r.description,
	rcd.creation_date,
	NULL,
	avg_tm.average [Average (h:m:s:ms)],
	'https://dashboard.uphp.local/dashboard/' + r.location,
	'https://dashboard.uphp.local/dashboard/' + REPLACE(REPLACE(location, '.aspx', '.xlsx'), '/', '/templates/'),
	NULL,
	#report_original_requester.original_requester,
	'Download Template'

FROM REPORT.Dashboard.dbo.reports r

LEFT JOIN #avg_time avg_tm
	ON avg_tm.id = r.report_id

LEFT JOIN #report_creation_date rcd
	ON rcd.id = avg_tm.id

LEFT JOIN #report_original_requester
ON #report_original_requester.id = r.report_id

WHERE r.type = 'report'
	AND r.isDeleted = 0

ORDER BY r.report

-----------------------------------------------------------------------------
IF OBJECT_ID('tempdb..#report_run_time', 'U') IS NOT NULL
	DROP TABLE #report_run_time
SELECT 
	c.Name,
	convert(varchar,dateadd(ms,AVG(DATEDIFF(MILLISECOND, l.TimeStart, l.TimeEnd)),0), 114) avg_time
INTO #report_run_time
FROM [SSRSReportServer].[dbo].[ExecutionLog] AS l
INNER JOIN [SSRSReportServer].[dbo].[Catalog] AS c ON l.ReportID = C.ItemID
WHERE c.Type = 2 
GROUP BY c.Name


INSERT INTO #results
(
    [Report Type],
    Name,
    Description,
    [Creation Date],
    [Modified Date],
    [Average Execution Time (h:m:s:ms)],
	[Link],
	[Group Contracts]
)
SELECT 
	SUBSTRING(path,	1+CHARINDEX('/',path),	CASE WHEN CHARINDEX('/',PATH,2) <> 0 THEN CHARINDEX('/',path,2)-2 ELSE LEN(path) END ) AS FolderPath,
	REPLACE(c.Name, '_', ' ') Name,
	c.Description,
	c.CreationDate,
	c.ModifiedDate, -- Is this needed since everytime all the reports get redeployed this value gets reset regardless of it the report had any actual changes.
	rt.avg_time [Average Time (h:m:s:ms)],
	'https://ssrs.uphp.local/reports/report' + c.Path,
	NULL
FROM [SSRSReportServer].[dbo].[Catalog] c

LEFT JOIN #report_run_time rt
	ON rt.Name = c.Name 
	
WHERE c.Type = 2 -- Report

ORDER BY FolderPath, c.Name

SELECT 
	CASE 
		WHEN r.[Report Type] = 'Automated_Reports' THEN 'SSRS Automated Reports'
		WHEN r.[Report Type] = 'Dashboard' THEN 'SSRS Dashboard'
		WHEN r.[Report Type] = 'SSRS_WIDOC_Dashboard' THEN 'SSRS WIDOC Dashboard'
		ELSE r.[Report Type]
	END [Report Type],
    CASE 
		WHEN UPPER(LEFT(r.Name, 1)) <> LEFT(r.Name, 1) COLLATE Latin1_General_CS_AS 
			THEN UPPER(LEFT(r.Name,1))+LOWER(SUBSTRING(r.Name,2,LEN(r.Name))) 
		ELSE r.Name 
	END	Name,
    r.Description,
    r.[Creation Date],
    r.[Modified Date],
    r.[Average Execution Time (h:m:s:ms)],
	r.Link,
	r.[Template Link],
	r.[Group Contracts],
	r.[Original Requester],
	r.[Input Fields],
	r.[Data Constraints],
	r.[Download Template]
FROM #results r
WHERE r.Name <> ''
ORDER BY r.[Report Type], r.Name