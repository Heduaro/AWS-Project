# Importing necessary libraries
import os
import pyodbc
from flask import Flask, render_template, request, url_for, redirect
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

# Retrieving connection string and port from environment variables
conn_str = os.environ.get("CONN_STR")
print("Connection string:", conn_str)
port = os.environ.get("PORT", "5000")

# Creating Flask application instance
app = Flask(__name__)

# Establishing connection to the database
conn = pyodbc.connect(conn_str)

# Route for the start page of the demo application
@app.route("/")
def index():
    """Start page of the demo application"""
    return render_template("index.html")

# Route for performing a simple query to the database
@app.route("/query1")
def query1():
    """Performs simple query to DB"""
    with conn.cursor() as cursor:
        cursor.execute("SELECT TOP (20) * FROM [SalesLT].[Product]")
        rows = cursor.fetchall()
        return render_template("query1result.html", rows=rows)

# Route for performing a better query to the database
@app.route("/query2")
def query2():
    """Performs better query to DB"""
    with conn.cursor() as cursor:
        cursor.execute("""SELECT TOP (20) [ProductID],
                            [Name],
                            [ProductNumber],
                            [StandardCost],
                            [Weight],
                            [SellStartDate]
                            [SellEndDate]
                        FROM [SalesLT].[Product]""")
        rows = cursor.fetchall()
        return render_template("query2result.html", rows=rows)

# Route for performing a query to the database using a template to display it
@app.route("/query3")
def query3():
    """Performs query to DB using template to display it"""
    with conn.cursor() as cursor:
        cursor.execute("""SELECT TOP (20) [ProductID],
                            [Name],
                            [ProductNumber]
                        FROM [SalesLT].[Product]
                        ORDER BY [ProductID] DESC""")
        all_rows = cursor.fetchall()
        return render_template("query3result.html", rows=all_rows)

# Route for editing an item in the database
@app.route("/edit/<int:product_id>", methods=['POST','GET'])
def edit(product_id):
    """Performs query to DB but display using template"""
    if request.method == 'GET':
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT [ProductID],
                                [Name],
                                [ProductNumber],
                                [Color],
                                [StandardCost],
                                [Size]
                            FROM [SalesLT].[Product]
                            WHERE [ProductID]='{product_id}'""")
            row = cursor.fetchone()
            return render_template("edit.html", row=row)
    else:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE [SalesLT].[Product]
                SET [Name] = ?, [ProductNumber] = ?
                WHERE [ProductID] = ?""", 
                (request.form['Name'], request.form['ProductNumber'], product_id))
            conn.commit()
        return redirect(url_for('query3'))

# Route for deleting an item from the database
@app.route("/delete/<int:product_id>")
def delete(product_id):
    """Delete one item from the table"""
    with conn.cursor() as cursor:
        cursor.execute("""DELETE FROM [SalesLT].[Product]
            WHERE [ProductID] = ?""", 
            (product_id))
        conn.commit()
    return redirect(url_for('query3'))

# Route for inserting a new item into the database
@app.route("/insert", methods=['POST','GET'])
def insert():
    """Inserts a new item into table"""
    if request.method == 'GET':
        return render_template("insert.html")
    else:
        with conn.cursor() as cursor:
            # Some of fields required by Address table are not present 
            # in the form, so the default values (eg. for 'province' 
            # for StateProvince) are provided
            cursor.execute("""INSERT INTO [SalesLT].[Product] 
                (Name, ProductNumber, Color, StandardCost, ListPrice, Size) 
                VALUES (?, ?, ?, ?, ?, ? )""", 
                (request.form['Name'], request.form['ProductNumber']))
            conn.commit()
        return redirect(url_for('query3'))

# Running the Flask application
if __name__ == "__main__":
    app.run(port)
