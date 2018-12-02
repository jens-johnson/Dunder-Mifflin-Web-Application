from flask import Flask, render_template, request, jsonify
from enum import Enum
import MySQLdb, re, json, pandas as pd


'''
Initialize the application and SQL connection
'''
app = Flask(__name__)
dbConnection = MySQLdb.connect(db="DunderMifflin", host="ix-dev.cs.uoregon.edu", user="guest", password="guest", port=3872)
dbCursor = dbConnection.cursor()


'''
SQL Formatted queries, passed in as a strng to Pandas or MySQLDb objects
'''
class Query(Enum):
    '''
    Pre-formatted SQL queries for the database connection.
    '''

    # Queries (i.e. GET data)

    SELECT_EMPLOYEES = "SELECT e.ssn, e.fname, e.lname, e.phone, d.dname FROM Employee e JOIN Department d ON e.dno_works_in = d.dno;"
    SELECT_EMPLOYEES_FILTERED = "SELECT e.ssn, e.fname, e.lname, e.phone, d.dname FROM Employee e JOIN Department d ON e.dno_works_in = d.dno WHERE d.dno={};"
    SALARY_BY_DEPARTMENT = "SELECT SUM(e.salary) AS total_salary, d.dname FROM Employee e JOIN Department d ON e.dno_works_in = d.dno GROUP BY d.dno ORDER BY 1 DESC;"
    SALARY_BY_INDIVIDUAL = "SELECT CONCAT(fname,' ', lname) AS full_name, salary FROM Employee ORDER BY salary DESC;"
    AVERAGE_SALARY = "SELECT AVG(salary) FROM Employee;"
    MAX_SALARY = "SELECT MAX(salary) FROM Employee;"
    MIN_SALARY = "SELECT MIN(salary) FROM Employee;"
    SALES_EMPLOYEES = "SELECT ssn, CONCAT(fname,' ',lname) AS full_name FROM Employee WHERE dno_works_in=5;"
    CLIENT_NAMES = "SELECT clientId, name FROM Clients ORDER BY name ASC;"
    CLIENT_NAMES_FILTERED = "SELECT c.name FROM Clients c JOIN Industry i ON c.industryId_partof = i.industryId WHERE i.industryId = {} ORDER BY c.name ASC;"
    STOCK_ITEMS = "SELECT CONCAT('[Stock No #',stockNum,']:',' ',description,' ','($',unitPrice,')') AS stockItem FROM Stock;"
    CURRENT_ORDER = "SELECT MAX(orderNo) FROM Orders;"
    ORDER_HISTORY = "SELECT COUNT(DISTINCT o.orderNo) AS num_orders, SUM(i.totalPrice) AS total_spent FROM Orders o JOIN Item i ON o.orderNo = i.orderNo WHERE o.client_id={} AND o.orderDate BETWEEN '{}' AND '{}';"
    GET_CLIENT = "SELECT name FROM Clients WHERE clientId={};"
    GET_EMPLOYEE = "SELECT CONCAT(fname,' ',lname) FROM Employee WHERE ssn={};"
    ORDER_ITEMS = "SELECT i.itemNo, s.description, i.quantity, i.totalPrice FROM Orders o JOIN Item i ON o.orderNo = i.orderNo JOIN Stock s ON i.stockNum = s.stockNum WHERE o.client_id = {} AND o.orderDate BETWEEN '{}' AND '{}';"
    GET_STOCK_PRODUCTS = "SELECT s.description, SUM(i.quantity) AS total_ordered, SUM(i.totalPrice) AS total FROM Stock s JOIN Item i ON s.stockNum = i.stockNum GROUP BY s.stockNum ORDER BY 3 DESC;"
    CLIENT_ORDERS_BY_REGION = "SELECT c.name, SUM(i.totalPrice) AS total_ordered FROM Sales_Division s JOIN Clients c ON s.divisionNo = c.divisionNo_operatesIn JOIN Orders o ON c.clientId = o.client_id JOIN Item i ON o.orderNo = i.orderNo WHERE s.divisionName='{}' GROUP BY c.clientId ORDER BY 2 DESC;"
    SALES_EMPLOYEE_SUMMARY = "SELECT SUM(i.quantity) AS total_ordered, SUM(i.totalPrice) AS total_price FROM Item i JOIN Orders o ON i.orderNo = o.orderNo JOIN Employee e ON o.sales_employee_ssn = e.ssn WHERE e.ssn = {} GROUP BY e.ssn;"
    CLIENT_SALES_EMPLOYEE_SUMMARY = "SELECT c.name, SUM(i.quantity) AS total_ordered, SUM(i.totalPrice) AS total_price FROM Item i JOIN Orders o ON i.orderNo = o.orderNo JOIN Clients c ON o.client_id = c.clientId WHERE o.sales_employee_ssn = {} GROUP BY o.client_id ORDER BY 2 DESC LIMIT 10;"

    # Insert Queries
    INSERT_ORDER = "INSERT INTO `DunderMifflin`.`Orders` (`orderNo`,`orderDate`,`serviceFee`,`sales_employee_ssn`,`client_id`) VALUES ({},'{}',{},{},{});"
    INSERT_ITEM = "INSERT INTO `DunderMifflin`.`Item` (`orderNo`,`totalPrice`,`quantity`,`stockNum`) VALUES "



'''
Regular Expressions for parsing HTML forms (explained in placeOrder())
'''
itemFilter = re.compile('item.*')
quantityFilter = re.compile('quantity.*')
totalPriceFilter = re.compile('totalPrice.*')


@app.route('/')
def home():
    '''
    Application home page
    '''
    return render_template("index.html")

@app.route('/Employees')
def employees():
    '''
    Employees page that lists all employees and their information.

    If the user has selected a department to filter the search by, this comes in the url request in the form of a query parameter ("department=<dno>")
    Depending on if their is a query parameter or not, the a pandas dataframe is loaded with the query parameter request, which populates a table on the
    page with all of the employees' information.
    '''
    if request.args.get('department'): employeesList = pd.read_sql_query(Query.SELECT_EMPLOYEES_FILTERED.value.format(request.args.get('department')), dbConnection)
    else: employeesList = pd.read_sql_query(Query.SELECT_EMPLOYEES.value, dbConnection)
    return render_template("employees.html", employees=employeesList)

@app.route('/Salaries')
def salaries():
    '''
    Salaries page.

    Provides summary information about employees' salaries, including average, min, and max salary of all employees.
    It uses a pandas dataframe to load each query, and formats the numbers as a salary on the page.
    '''
    average_salary = "{0:,.2f}".format(pd.read_sql_query(Query.AVERAGE_SALARY.value, dbConnection).itertuples().next()[1])
    max_salary = "{0:,.2f}".format(pd.read_sql_query(Query.MAX_SALARY.value, dbConnection).itertuples().next()[1])
    min_salary = "{0:,.2f}".format(pd.read_sql_query(Query.MIN_SALARY.value, dbConnection).itertuples().next()[1])
    return render_template("salaries.html", average_salary=average_salary, max_salary=max_salary, min_salary=min_salary)

@app.route('/Salaries/Department', methods=['GET'])
def salariesByDepartment():
    '''
    Called by the "Salaries by Department" button to return a JSON list of all of the salaries for each department.
    This list is used to populate a Plotly graph on the page.
    '''
    department_salaries = pd.read_sql_query(Query.SALARY_BY_DEPARTMENT.value, dbConnection).to_json()
    return department_salaries

@app.route('/Salaries/Individual', methods=['GET'])
def salariesByIndividual():
    '''
    Called by the "Individual Salaries" button to return a JSON list of all of the salries for each individual employee.
    This list is used to populate a Plotly graph on the page.
    '''
    individual_salaries = pd.read_sql_query(Query.SALARY_BY_INDIVIDUAL.value, dbConnection).to_json()
    print(individual_salaries)
    return individual_salaries

@app.route('/Place-Order', methods=['GET','POST'])
def placeOrder():
    '''
    Place order page used to place an order for a given client through a sales employee.

    Explained in the function body below.
    '''


    # If our HTTP request is a POST, we know that the user is submitting form data
    if request.method == 'POST':
        orderForm = request.form

        # Because the order form is a dynamic table, we have to use a regex to figure out how many
        # items have been put in the order (this checks for form fields for each of the items)
        totalPrices = [ orderForm[i] for i in list(filter(totalPriceFilter.match, orderForm.keys())) ]
        quantities = [ orderForm[i] for i in list(filter(quantityFilter.match, orderForm.keys())) ]
        items = [ orderForm[i] for i in list(filter(itemFilter.match, orderForm.keys())) ]
        itemRows = zip(items, quantities, totalPrices)

        # Get an orderId to place the current order under (i.e. increment orderNo manually)
        currentOrder = pd.read_sql_query(Query.CURRENT_ORDER.value, dbConnection).itertuples().next()[1] + 1
        
        # Getting the order date, sales employee, client, and order fee from the form
        orderDate = (orderForm['salesDate'].decode('utf-8').replace('T',' ') + ':00').decode('utf-8')
        orderEmployee = int(orderForm['salesEmployee'])
        orderClient = int(orderForm['salesClient'].decode('utf-8'))
        orderFee = float(orderForm['salesFee'].decode('utf-8').replace('$',''))

        # Insert a new order into the orders table
        dbCursor.execute(Query.INSERT_ORDER.value.format(currentOrder, orderDate, orderFee, orderEmployee, orderClient))
        dbConnection.commit()

        # Insert each item into the items table
        insert_item_statement = Query.INSERT_ITEM.value
        for row in itemRows:
            stockNumber = row[0][row[0].find('#')+1:row[0].find(']')]
            quantity = int(row[1])
            totalPrice = float(row[2].replace('$',''))
            row_statement = "({},{},{},{}),".format(currentOrder,totalPrice,quantity,stockNumber)
            print(row_statement)
            insert_item_statement += row_statement
        insert_item_statement = insert_item_statement[:-1] + ';'

        dbCursor.execute(insert_item_statement)
        dbConnection.commit()


    # Returns a list of all the sales employees for the selection box for "Sales Employee"
    sales_employees = pd.read_sql_query(Query.SALES_EMPLOYEES.value, dbConnection)
    
    # Returns a list of all stock items for the item entry JQuery UI autocomplete
    stock_items = json.loads(pd.read_sql_query(Query.STOCK_ITEMS.value, dbConnection).to_json())
    
    # Populates the clients selection box for "Client", filtering by industry if the user has selected a filter
    if request.args.get('industry'): sales_clients = pd.read_sql_query(Query.CLIENT_NAMES_FILTERED.value.format(request.args.get('industry')), dbConnection)
    else: sales_clients = pd.read_sql_query(Query.CLIENT_NAMES.value, dbConnection)
    
    return render_template('place-order.html', sales_employees=sales_employees, sales_clients=sales_clients, stock_items=stock_items)

@app.route('/Order-History', methods=['GET','POST'])
def order_history():
    orderInfo, clientName, orderHistoryRange, orderItemsInfo = None, None, None, None
    if request.method == 'POST':
        dates = request.form['orderDates'].split(' - ')
        client = int(request.form['salesClient'])
        startlist = dates[0].split('/')
        endlist = dates[1].split('/')

        start = '{}-{}-{}'.format(startlist[2],startlist[0],startlist[1])
        end = '{}-{}-{}'.format(endlist[2],endlist[0],endlist[1])

        order_query = Query.ORDER_HISTORY.value.format(client,start,end)
        order_items_query = Query.ORDER_ITEMS.value.format(client,start,end)

        orderInfo = pd.read_sql_query(order_query, dbConnection)
        orderItemsInfo = pd.read_sql_query(order_items_query, dbConnection)
        clientName = pd.read_sql_query(Query.GET_CLIENT.value.format(client), dbConnection).itertuples().next()[1]
        orderHistoryRange = request.form['orderDates']

    sales_clients = pd.read_sql_query(Query.CLIENT_NAMES.value, dbConnection)
    return render_template('order-history.html', sales_clients=sales_clients, orderInfo=orderInfo, clientName=clientName, orderHistoryRange=orderHistoryRange, orderItemsInfo=orderItemsInfo)

@app.route('/Products')
def products():
    '''
    Products page for all of the stock items
    '''
    return render_template('products.html')

@app.route('/Products/Stock', methods=['GET'])
def getStockProducts():
    '''
    Called by the products page to return a JSON list of all stock items and their total quantities and revenue over all orders.

    This data is then graphed on a Plotly graph on the page.
    '''
    stock_products = pd.read_sql_query(Query.GET_STOCK_PRODUCTS.value, dbConnection).to_json()
    return stock_products

@app.route('/Sales-Regions/Companies/<region>', methods=['GET'])
def salesRegionsSalesData(region=None):
    '''
    Called by the sales regions page to show the revenue each sales region has generated over time for each of the companies in
    that region. Returns a JSON list of revenues by company for the region.
    '''
    sales_region_data = pd.read_sql_query(Query.CLIENT_ORDERS_BY_REGION.value.format(region), dbConnection).to_json()
    return sales_region_data

@app.route('/Sales-Regions')
def salesRegions():
    '''
    Sales regions page to display revenues for each region
    '''
    return render_template('sales-regions.html')

@app.route('/Sales-Employees')
def salesEmployees():
    '''
    Returns information about sales for the company's employees.
    '''
    sales_employees = pd.read_sql_query(Query.SALES_EMPLOYEES.value, dbConnection)
    return render_template('sales-employees.html', sales_employees=sales_employees)

@app.route('/Sales-Employees/<employeeSSN>', methods=['GET'])
def salesEmployeesInformation(employeeSSN=None):
    '''
    Returns information about sales for the company's employees.

    Used in an AJAX call from the front-end of the application to return a json payload of information abotu the company's sales employees.
    '''
    if employeeSSN != None:
        employeeName = pd.read_sql_query(Query.GET_EMPLOYEE.value.format(employeeSSN), dbConnection).itertuples().next()[1]
        employeeInformation = pd.read_sql_query(Query.SALES_EMPLOYEE_SUMMARY.value.format(employeeSSN), dbConnection).to_json()
        clientInformation = pd.read_sql_query(Query.CLIENT_SALES_EMPLOYEE_SUMMARY.value.format(employeeSSN), dbConnection).to_json()
        returnInfo = json.dumps({'employeeInfo':employeeInformation,'clientInfo':clientInformation,'employeeName':employeeName})
        return returnInfo

@app.route('/About')
def about():
    return render_template('about.html')

