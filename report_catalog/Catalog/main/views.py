"""
Routes and views for the flask application.
"""
from multiprocessing import connection
import os
import logging
from plistlib import UID
from main import app
from datetime import datetime
from flask import render_template, request, redirect, url_for
import pyodbc

# dbo.catalog_data [Report Type] for web/dashboard platform rows (matches catalog load).
WEB_PLATFORM_DASHBOARD_REPORT_TYPE = os.environ.get(
    'CATALOG_WEB_PLATFORM_DASHBOARD_TYPE',
    'Web Dashboard',
)

# dbo.catalog_data [Report Type] for SSRS-hosted “program dashboard” subtree (neutral label; matches catalog ETL CASE).
SSRS_PROGRAM_DASHBOARD_REPORT_TYPE = os.environ.get(
    'CATALOG_SSRS_PROGRAM_DASHBOARD_TYPE',
    'SSRS Program Dashboards',
)


def catalog_db_connection():
    """
    Open ODBC connection to the report catalog SQL Server database.
    Set CATALOG_SQL_SERVER, CATALOG_SQL_DATABASE, CATALOG_ODBC_DRIVER in the environment,
    or CATALOG_SQL_USER / CATALOG_SQL_PASSWORD for SQL auth instead of Trusted_Connection.
    """
    driver = os.environ.get('CATALOG_ODBC_DRIVER', '{ODBC Driver 17 for SQL Server}')
    server = os.environ.get('CATALOG_SQL_SERVER', 'localhost')
    database = os.environ.get('CATALOG_SQL_DATABASE', 'ReportCatalog')
    user = os.environ.get('CATALOG_SQL_USER', '').strip()
    password = os.environ.get('CATALOG_SQL_PASSWORD', '').strip()
    if user:
        conn_str = (
            f'DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password};'
        )
    else:
        conn_str = (
            f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        )
    return pyodbc.connect(conn_str)


#COMMENT THIS PORTION OF CODE OUT FOR LOCAL TESTING#
################################################################
#Define the log folder path
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
###################################################################


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/desired_page')
def desired_page():
    # Always redirect to the search.html page
    return redirect(url_for('search'))

@app.route('/ssrs_program_dashboards')
def ssrs_program_dashboards_page():

    page = request.args.get('page', default=1, type=int)
    items_per_page = 100  # Set the number of items to display per page

    # Fetch data from the database based on the current page and items per page
    data = ssrs_program_dashboards(page, items_per_page)

    # Calculate the next page number
    next_page_number = page + 1 if len(data) >= items_per_page else None

    # If there are no more records in the database, set next_page_number to None
    if len(data) < items_per_page:
        next_page_number = None
    previous_page_number = page - 1 if page > 1 else None

    # Pass data, page number, items_per_page, and next_page_number to the template
    return render_template('ssrs_program_dashboards.html', data=data, title='SSRS program dashboards', page=page, items_per_page=items_per_page, next_page_number=next_page_number, previous_page_number=previous_page_number)

def ssrs_program_dashboards(page, items_per_page):

    # Calculate the offset to fetch the correct items based on the page number
    offset = (page - 1) * items_per_page
    _rt = SSRS_PROGRAM_DASHBOARD_REPORT_TYPE.replace("'", "''")

    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
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
    [Group Contracts] as gc,
    [Input Fields] as inputfields  
    FROM 
    dbo.catalog_data
    WHERE [Report Type] = '{_rt}'
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
            'column8': row.gc,
            'column9': row.inputfields,
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
    conn = catalog_db_connection()
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
    [Group Contracts] as gc,
    [Input Fields] as inputfields
    FROM 
    dbo.catalog_data
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
            'column8': row.gc,
            'column9': row.inputfields           
            # Add more columns as needed
        }
        data.append(entry)

    # Close the connection
    conn.close()

    return data

def perform_search_web_platform_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
    cursor = conn.cursor()

    _rt = WEB_PLATFORM_DASHBOARD_REPORT_TYPE.replace("'", "''")

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Group Contracts] as gc,
        [Input Fields] as inputfields     
    FROM 
        dbo.catalog_data
    WHERE 
        [Name] LIKE ? AND [Report Type] = '{_rt}'
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
            'column8': row.gc,
            'column9': row.inputfields
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results


def perform_search_ssrs_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
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
        [Group Contracts] as gc,
        [Input Fields] as inputfields
        
    FROM 
        dbo.catalog_data
    WHERE 
        [Name] LIKE ? AND [Report Type] = 'SSRS Dashboard'
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
            'column8': row.gc,
            'column9': row.inputfields
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results

def perform_search_ssrs_automated_reports(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
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
        [Group Contracts] as gc,
        [Input Fields] as inputfields
    FROM 
        dbo.catalog_data
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
            'column8': row.gc,
            'column9': row.inputfields
            # Add more columns as needed
        }
        search_results.append(entry)

    # Close the connection
    conn.close()

    return search_results

def perform_search_ssrs_program_dashboards(query):
    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
    cursor = conn.cursor()

    _rt = SSRS_PROGRAM_DASHBOARD_REPORT_TYPE.replace("'", "''")

    # Write your SQL query with the search term between '%' signs for wildcard matching
    sql_query = f'''
    SELECT 
        [Name] AS ReportType,
        [Template Link] AS TemplateLink,
        Description AS description,
        [Average Execution Time (h:m:s:ms)] AS averagetime,
        CONVERT(DATE, [Creation Date]) AS Creation_Date,
        [Modified Date] AS modifieddate,
        [Group Contracts] as gc,
        [Input Fields] as inputfields
        
    FROM 
        dbo.catalog_data
    WHERE 
        [Name] LIKE ? AND [Report Type] = '{_rt}'
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
            'column8': row.gc,
            'column9': row.inputfields
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
    web_dashboard_results = None
    ssrs_dashboard_results = None
    ssrs_program_dashboard_results = None

    # Check if a search query has been submitted
    if query:
        # Call your functions to fetch search results based on the query for different categories
        ssrs_automated_reports_results = perform_search_ssrs_automated_reports(query)
        web_dashboard_results = perform_search_web_platform_dashboards(query)
        ssrs_dashboard_results = perform_search_ssrs_dashboards(query)
        ssrs_program_dashboard_results = perform_search_ssrs_program_dashboards(query)

    # Render the search results template with the search results
    return render_template('search.html', title='Search Reports',
                           ssrs_automated_reports_results=ssrs_automated_reports_results,
                           web_dashboard_results=web_dashboard_results,
                           ssrs_dashboard_results=ssrs_dashboard_results,
                           ssrs_program_dashboard_results=ssrs_program_dashboard_results)





@app.route('/web_dashboards')
def web_dashboard_catalog():
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
    return render_template('web_dashboard_page.html', data=data, title='Web Dashboard Catalog', page=page, items_per_page=items_per_page, next_page_number=next_page_number, previous_page_number=previous_page_number)


def fetch_data_from_database(page, items_per_page):

    # Manual mapping of dashboard names to document paths
    dashboard_to_document_mapping = {
        'Agent Charge Backs': '/dashboard_pseudocode/odag_table_1_pseudocode.docx',
        # Add more mappings as needed
    }

    # Calculate the offset to fetch the correct items based on the page number
    offset = (page - 1) * items_per_page
    _rt = WEB_PLATFORM_DASHBOARD_REPORT_TYPE.replace("'", "''")

    # Establish a connection to the SQL Server database using Windows Authentication
    conn = catalog_db_connection()
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
    [Group Contracts] as gc,
    [Input Fields] as inputfields
    
    FROM 
    dbo.catalog_data
    WHERE [Report Type] = '{_rt}'
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
            'column8': row.gc,
            'column9': row.inputfields,
            'document_link': dashboard_to_document_mapping.get(row.ReportType)  # Get document link from manual mapping
            # Add more columns as needed
        }
        data.append(entry)

    # Close the connection
    conn.close()

    return data
