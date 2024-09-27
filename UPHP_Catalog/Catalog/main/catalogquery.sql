/*This is the query that will update the catalog data table with updated data*/


/*
CHANGE LOG
============================================
08/26/2024 Brad Maison TFS#6680: Removed data constraints column at request of PC
09/27/2024 Brad Maison TFS#9264: Updated average runtime caclculation to work as BIGINT to remove any arithimitc overflow.
============================================
*/
TRUNCATE TABLE [ReportCatalog].[dbo].[catalog_data]

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
	[Input Fields] VARCHAR(MAX)
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
	[Group Contracts]
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
	NULL

FROM REPORT.Dashboard.dbo.reports r

LEFT JOIN #avg_time avg_tm
	ON avg_tm.id = r.report_id

LEFT JOIN #report_creation_date rcd
	ON rcd.id = avg_tm.id

WHERE r.type = 'report'
	AND r.isDeleted = 0

ORDER BY r.report

-----------------------------------------------------------------------------
IF OBJECT_ID('tempdb..#report_run_time', 'U') IS NOT NULL
	DROP TABLE #report_run_time
SELECT 
	c.Name,
    CONVERT(VARCHAR, DATEADD(ms, AVG(CAST(DATEDIFF(MILLISECOND, l.TimeStart, l.TimeEnd) AS BIGINT)), 0), 114) AS avg_time
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
	c.ModifiedDate, -- This is needed since everytime all the reports get redeployed this value gets reset regardless of it the report had any actual changes.
	rt.avg_time [Average Time (h:m:s:ms)],
	'https://ssrs.uphp.local/reports/report' + c.Path,
	NULL
FROM [SSRSReportServer].[dbo].[Catalog] c

LEFT JOIN #report_run_time rt
	ON rt.Name = c.Name 
	
WHERE c.Type = 2 -- Report

ORDER BY FolderPath, c.Name

if object_id('tempdb..#main', 'U') is not null
    drop table #main;
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
	r.[Input Fields]
INTO #main
FROM #results r
WHERE r.Name <> ''
ORDER BY r.[Report Type], r.Name

INSERT INTO ReportCatalog.dbo.catalog_data

SELECT
m.[Report Type],
m.Name,
m.Description,
m.[Creation Date],
m.[Modified Date],
m.[Average Execution Time (h:m:s:ms)],
m.Link,
m.[Template Link],
cmd.[Group Contracts],
cmd.[Input Fields]
FROM #main m

LEFT JOIN ReportCatalog.dbo.catalog_manual_data cmd
ON cmd.Name = m.Name

WHERE [Report Type] <> 'SSRS Dashboard'
ORDER BY [Report Type]