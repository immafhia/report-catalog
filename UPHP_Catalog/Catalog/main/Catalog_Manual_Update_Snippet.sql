/*
This snippet is used to update the group contracts and input fields of the catalog. This is used so we can have a distinct way of tracking group contracts and input fields associated with reports


=====CHANGE LOG======
09/18/2024 Brad Maison TFS#6680: Snippet created
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
'N/A',		--Enter the group contracts used in the report in a comma separated list. Ex. 'UPHP MEDICAID, UPHPMHL', 'UPHP CSHCS'
'N/A'		--Enter the input fields of the report, this includes what values are entered in the report. Ex. 'Procedure Code, Date Range', 'Date Range'	
)