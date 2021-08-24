import configparser
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import re 
from configparser import ConfigParser
 
app = Flask(__name__)
app.secret_key = 'secret-key'
 
config =  ConfigParser()

config.read('database.ini')

DB_HOST = config['connect']['host']
DB_USER = config['connect']['user']
DB_PASS = config['connect']['password']
DB_NAME = config['connect']['database']

conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)

@app.route('/customers', methods=['GET', 'POST']) 
def customers():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM customers')
    data = cursor.fetchall() 
    return render_template('customers.html', data=data)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('DELETE FROM customers WHERE id='+str(id))
    conn.commit()
    return render_template("customers.html")
 
@app.route('/customers/new', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("CREATE TABLE IF NOT EXISTS customers(id serial PRIMARY KEY, company_name varchar, contact_name varchar, contact_mail varchar, mail_domain varchar, identity varchar, device_number varchar, other varchar);")
    if request.method == 'POST' and 'company_name' in request.form and 'contact_name' in request.form and 'contact_mail' in request.form and 'mail_domain' in request.form  and 'identity' in request.form and 'device_number' in request.form and 'other' in request.form:
        
        company_name = request.form['company_name']
        contact_name = request.form['contact_name']
        contact_mail = request.form['contact_mail']
        mail_domain = request.form['mail_domain']
        identity = request.form.get('identity')
        device_number = request.form['device_number']
        other = request.form['other']

        cursor.execute('SELECT * FROM customers WHERE company_name = %s', (company_name,))
        account = cursor.fetchone()
        print(account)

        if not company_name or not contact_name or not contact_mail or not mail_domain or not identity:
            flash('Please fill out the form!', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact_mail):
            flash('Invalid email address!', 'danger')
        else:
            cursor.execute("INSERT INTO customers (company_name, contact_name, contact_mail, mail_domain, identity, device_number, other) VALUES (%s,%s,%s,%s,%s,%s,%s)", (company_name, contact_name, contact_mail, mail_domain, identity, device_number, other))
            conn.commit()
            flash('You have successfully registered!', 'success')
    elif request.method == 'POST':
        flash('Please fill out the form!')
    
    return render_template('new.html')

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)