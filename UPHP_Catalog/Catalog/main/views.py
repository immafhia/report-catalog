"""
Routes and views for the flask application.
"""
from multiprocessing import connection
import os
import logging
from plistlib import UID
from main import app
from datetime import datetime
from flask import render_template, request
import pyodbc


# Define the log folder path
log_folder_path = "logs"

# Check if the log folder exists
if not os.path.exists(log_folder_path):
    os.makedirs(log_folder_path)

# Define the error log file path
error_log_file_path = os.path.join(log_folder_path, "error.log")

# Configure logging
logging.basicConfig(
    filename=error_log_file_path,
    level=logging.DEBUG,  # Set the desired logging level
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_error_and_render_generic_error(e):
    # Log the exception
    logging.error("An error occurred: %s", str(e), exc_info=True)



@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@app.route('/ssrs_dashboard_page')
def ssrs_dashboard_page():

    page = request.args.get('page', default=1, type=int)
    items_per_page = 100  # Set the number of items to display per page

    try:
        # Fetch data from the database based on the current page and items per page
        data = ssrs_dashboards(page, items_per_page)

        # Calculate the next page number
        next_page_number = page + 1 if len(data) >= items_per_page else None

        # If there are no more records in the database, set next_page_number to None
        if len(data) < items_per_page:
            next_page_number = None
        previous_page_number = page - 1 if page > 1 else None

        # Pass data, page number, items_per_page, and next_page_number to the template
        return render_template('ssrs_dashboard.html', data=data, title='SSRS Dashboards', page=page,
                               items_per_page=items_per_page, next_page_number=next_page_number,
                               previous_page_number=previous_page_number)

    except Exception as e:
        return log_error_and_render_generic_error(e)

def ssrs_dashboards(page, items_per_page):

    try:
        # Convert `page` to an integer
        page = int(page)

        # Calculate the offset to fetch the correct items based on the page number
        offset = (page - 1) * items_per_page
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
        cursor = conn.cursor()

        # Write your SQL query directly in the Python script
        sql_query = f'''
            SELECT 
            [Name] AS ReportType,
            [Template Link] AS TemplateLink,
            Description AS description,
            [Average Execution Time (h:m:s:ms)] AS averagetime,
            CONVERT(DATE, [Creation Date]) AS Creation_Date,
            [Modified Date] AS modifieddate,
            [Original Requester] As originalrequester,
            [Group Contracts] as gc,
            [Input Fields] as inputfields,
            [Data Constraints] as dataconstraints
            FROM 
            dbo.testpython
            WHERE [Report Type] = 'SSRS Dashboard'
            ORDER BY [Name]
            OFFSET {offset} ROWS
            FETCH NEXT {items_per_page} ROWS ONLY
        '''

        # Execute your SQL query
        cursor.execute(sql_query)

        # Fetch all rows as a list of dictionaries
        data = []
        for row in cursor.fetchall():
            entry = {
                'column1': row.ReportType,
                'column2': row.TemplateLink,
                'column3': row.description,
                'column4': row.averagetime,
                'column5': row.Creation_Date,
                'column6': row.modifieddate,
                'column7': row.originalrequester,
                'column8': row.gc,
                'column9': row.inputfields,
                'column10': row.dataconstraints
                # Add more columns as needed
            }
            data.append(entry)

        # Close the connection
        conn.close()

        return data

    except Exception as e:
        return log_error_and_render_generic_error(e)



@app.route('/ssrs_widoc_page')
def ssrs_widoc_page():

    page = request.args.get('page', default=1, type=int)
    items_per_page = 100  # Set the number of items to display per page

    # Fetch data from the database based on the current page and items per page
    data = ssrs_widoc_dashboards(page, items_per_page)

    # Calculate the next page number
    next_page_number = page + 1 if len(data) >= items_per_page else None

    # If there are no more records in the database, set next_page_number to None
    if len(data) < items_per_page:
        next_page_number = None
    previous_page_number = page - 1 if page > 1 else None

    # Pass data, page number, items_per_page, and next_page_number to the template
    return render_template('ssrs_widoc_dashboards.html', data=data, title='SSRS WIDOC Dashboards', page=page, items_per_page=items_per_page, next_page_number=next_page_number, previous_page_number=previous_page_number)

def ssrs_widoc_dashboards(page, items_per_page):

    # Calculate the offset to fetch the correct items based on the page number
    offset = (page - 1) * items_per_page

    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query directly in the Python script
    sql_query = f'''
    SELECT 
    [Name] AS ReportType,
    [Template Link] AS TemplateLink,
    Description AS description,
    [Average Execution Time (h:m:s:ms)] AS averagetime,
    CONVERT(DATE, [Creation Date]) AS Creation_Date,
    [Modified Date] AS modifieddate,
    [Original Requester] As originalrequester,
    [Group Contracts] as gc,
    [Input Fields] as inputfields,
    [Data Constraints] as dataconstraints
    FROM 
    dbo.testpython
    WHERE [Report Type] = 'SSRS WIDOC Dashboard'
    ORDER BY [Name]
    OFFSET {offset} ROWS
    FETCH NEXT {items_per_page} ROWS ONLY
    '''

    # Execute your SQL query
    cursor.execute(sql_query)

    # Fetch all rows as a list of dictionaries
    data = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints
            # Add more columns as needed
        }
        data.append(entry)

    # Close the connection
    conn.close()

    return data

@app.route('/ssrs_automated_reports')
def ssrs_automated_reports_page():
    page = request.args.get('page', default=1, type=int)
    items_per_page = 100  # Set the number of items to display per page

    # Fetch data from the database based on the current page and items per page
    data = ssrs_report_data(page, items_per_page)

    # Calculate the next page number
    next_page_number = page + 1 if len(data) >= items_per_page else None

    # If there are no more records in the database, set next_page_number to None
    if len(data) < items_per_page:
        next_page_number = None
    previous_page_number = page - 1 if page > 1 else None

    # Pass data, page number, items_per_page, and next_page_number to the template
    return render_template('ssrs_automated_reports.html', data=data, title='SSRS Automated Reports', page=page, items_per_page=items_per_page, next_page_number=next_page_number, previous_page_number=previous_page_number)

def ssrs_report_data(page, items_per_page):

    # Calculate the offset to fetch the correct items based on the page number
    offset = (page - 1) * items_per_page

    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query directly in the Python script
    sql_query = f'''
    SELECT 
    [Name] AS ReportType,
    [Template Link] AS TemplateLink,
    Description AS description,
    [Average Execution Time (h:m:s:ms)] AS averagetime,
    CONVERT(DATE, [Creation Date]) AS Creation_Date,
    [Modified Date] AS modifieddate,
    [Original Requester] As originalrequester,
    [Group Contracts] as gc,
    [Input Fields] as inputfields,
    [Data Constraints] as dataconstraints
    FROM 
    dbo.testpython
    WHERE [Report Type] = 'SSRS Automated Reports'
    ORDER BY [Name]
    OFFSET {offset} ROWS
    FETCH NEXT {items_per_page} ROWS ONLY
    '''

    # Execute your SQL query
    cursor.execute(sql_query)

    # Fetch all rows as a list of dictionaries
    data = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints
            # Add more columns as needed
        }
        data.append(entry)

    # Close the connection
    conn.close()

    return data

def perform_search_uphp_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Original Requester] As originalrequester,
        [Group Contracts] as gc,
        [Input Fields] as inputfields,
        [Data Constraints] as dataconstraints
    FROM 
        dbo.testpython
    WHERE 
        [Name] LIKE ? AND [Report Type] = 'UPHP Dashboard'  -- Use parameterized query to prevent SQL injection
    ORDER BY 
        [Name]
    '''

    # Execute your SQL query with the search term as a parameter
    cursor.execute(sql_query, ('%' + query + '%',))

    # Fetch all rows as a list of dictionaries
    search_results = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints,
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results


def perform_search_ssrs_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Original Requester] As originalrequester,
        [Group Contracts] as gc,
        [Input Fields] as inputfields,
        [Data Constraints] as dataconstraints
    FROM 
        dbo.testpython
    WHERE 
        [Name] LIKE ? AND [Report Type] = 'UPHP Dashboard'  -- Use parameterized query to prevent SQL injection
    ORDER BY 
        [Name]
    '''

    # Execute your SQL query with the search term as a parameter
    cursor.execute(sql_query, ('%' + query + '%',))

    # Fetch all rows as a list of dictionaries
    search_results = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints,
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results

def perform_search_ssrs_automated_reports(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Original Requester] As originalrequester,
        [Group Contracts] as gc,
        [Input Fields] as inputfields,
        [Data Constraints] as dataconstraints
    FROM 
        dbo.testpython
    WHERE 
        [Name] LIKE ? AND [Report Type] = 'SSRS Automated Reports'  -- Use parameterized query to prevent SQL injection
    ORDER BY 
        [Name]
    '''

    # Execute your SQL query with the search term as a parameter
    cursor.execute(sql_query, ('%' + query + '%',))

    # Fetch all rows as a list of dictionaries
    search_results = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints,
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results

def perform_search_ssrs_widoc_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Original Requester] As originalrequester,
        [Group Contracts] as gc,
        [Input Fields] as inputfields,
        [Data Constraints] as dataconstraints
    FROM 
        dbo.testpython
    WHERE 
        [Name] LIKE ? AND [Report Type] = 'SSRS WIDOC Dashboard'  -- Use parameterized query to prevent SQL injection
    ORDER BY 
        [Name]
    '''

    # Execute your SQL query with the search term as a parameter
    cursor.execute(sql_query, ('%' + query + '%',))

    # Fetch all rows as a list of dictionaries
    search_results = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints,
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results

@app.route('/search')
def search():
    query = request.args.get('query', default='', type=str)

    # Initialize search result variables as None
    ssrs_automated_reports_results = None
    uphp_dashboard_results = None
    ssrs_dashboard_results = None
    ssrs_widoc_dashboard_results = None

    # Check if a search query has been submitted
    if query:
        # Call your functions to fetch search results based on the query for different categories
        ssrs_automated_reports_results = perform_search_ssrs_automated_reports(query)
        uphp_dashboard_results = perform_search_uphp_dashboards(query)
        ssrs_dashboard_results = perform_search_ssrs_dashboards(query)
        ssrs_widoc_dashboard_results = perform_search_ssrs_widoc_dashboards(query)

    # Render the search results template with the search results
    return render_template('search.html', title='Search Reports',
                           ssrs_automated_reports_results=ssrs_automated_reports_results,
                           uphp_dashboard_results=uphp_dashboard_results,
                           ssrs_dashboard_results=ssrs_dashboard_results,
                           ssrs_widoc_dashboard_results=ssrs_widoc_dashboard_results)





@app.route('/uphp_dashboard_page')
def uphp_dashboard_page():
    page = request.args.get('page', default=1, type=int)
    items_per_page = 100  # Set the number of items to display per page

    # Fetch data from the database based on the current page and items per page
    data = fetch_data_from_database(page, items_per_page)

    # Calculate the next page number
    next_page_number = page + 1 if len(data) >= items_per_page else None

    # If there are no more records in the database, set next_page_number to None
    if len(data) < items_per_page:
        next_page_number = None
    previous_page_number = page - 1 if page > 1 else None

    # Pass data, page number, items_per_page, and next_page_number to the template
    return render_template('uphp_dashboard_page.html', data=data, title='UPHP Dashboards', page=page, items_per_page=items_per_page, next_page_number=next_page_number, previous_page_number=previous_page_number)


def fetch_data_from_database(page, items_per_page):

    # Manual mapping of dashboard names to document paths
    dashboard_to_document_mapping = {
        'Agent Charge Backs': '/dashboard_pseudocode/odag_table_1_pseudocode.docx',
        # Add more mappings as needed
    }

    # Calculate the offset to fetch the correct items based on the page number
    offset = (page - 1) * items_per_page

    # Establish a connection to the SQL Server database using Windows Authentication
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=REPORT;DATABASE=UPHP_Prod_Replica;Trusted_Connection=Yes;')
    cursor = conn.cursor()

    # Write your SQL query directly in the Python script
    sql_query = f'''
    SELECT 
    [Name] AS ReportType,
    [Template Link] AS TemplateLink,
    Description AS description,
    [Average Execution Time (h:m:s:ms)] AS averagetime,
    CONVERT(DATE, [Creation Date]) AS Creation_Date,
    [Modified Date] AS modifieddate,
    [Original Requester] As originalrequester,
    [Group Contracts] as gc,
    [Input Fields] as inputfields,
    [Data Constraints] as dataconstraints
    FROM 
    dbo.testpython
    WHERE [Report Type] = 'UPHP Dashboard'
    ORDER BY [Name]
    OFFSET {offset} ROWS
    FETCH NEXT {items_per_page} ROWS ONLY
    '''

    # Execute your SQL query
    cursor.execute(sql_query)

    # Fetch all rows as a list of dictionaries
    data = []
    for row in cursor.fetchall():
        entry = {
            'column1': row.ReportType,
            'column2': row.TemplateLink,
            'column3': row.description,
            'column4': row.averagetime,
            'column5': row.Creation_Date,
            'column6': row.modifieddate,
            'column7': row.originalrequester,
            'column8': row.gc,
            'column9': row.inputfields,
            'column10': row.dataconstraints,
            'document_link': dashboard_to_document_mapping.get(row.ReportType)  # Get document link from manual mapping
            # Add more columns as needed
        }
        data.append(entry)

    # Close the connection
    conn.close()

    return data
