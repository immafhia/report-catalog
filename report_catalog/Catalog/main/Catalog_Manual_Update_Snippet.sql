/*
This snippet is used to update the group contracts and input fields of the catalog. This is used so we can have a distinct way of tracking group contracts and input fields associated with reports


=====CHANGE LOG======
Initial manual row template for enrichment join.
=====================
*/

INSERT INTO ReportCatalog.dbo.catalog_manual_data
(
    Name,
    [Group Contracts],
    [Input Fields]
)
VALUES
( 
'N/A',		--Enter the name of ther report
'N/A',		--Enter the group contracts used in the report in a comma separated list. Example: 'Medicaid Product A', 'Product B Specialty'
'N/A'		--Enter the input fields of the report, this includes what values are entered in the report. Ex. 'Procedure Code, Date Range', 'Date Range'	
)