import sqlite3
from datetime import datetime, timedelta
import random

# Singleton Pattern for Database Connection
class DatabaseConnection:
    _instance = None

    def __new__(cls, db_path):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect(db_path)
        return cls._instance

    @staticmethod
    def get_connection():
        if DatabaseConnection._instance is None:
            raise Exception("DatabaseConnection has not been initialized. Call DatabaseConnection(db_path) first.")
        return DatabaseConnection._instance.connection

db_connection = DatabaseConnection('company_database.db')
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()

# Create the companies table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL
)
''')

# Synthesize data for 10 companies
companies = [
    (1, 'AAPL', 'Apple Inc.'),
    (2, 'GOOGL', 'Alphabet Inc.'),
    (3, 'MSFT', 'Microsoft Corporation'),
    (4, 'AMZN', 'Amazon.com Inc.'),
    (5, 'TSLA', 'Tesla Inc.'),
    (6, 'FB', 'Meta Platforms Inc.'),
    (7, 'NVDA', 'NVIDIA Corporation'),
    (8, 'NFLX', 'Netflix Inc.'),
    (9, 'ADBE', 'Adobe Inc.'),
    (10, 'ORCL', 'Oracle Corporation')
]

# Insert data into the companies table
cursor.executemany('''
INSERT OR IGNORE INTO companies (id, ticker, name)
VALUES (?, ?, ?)
''', companies)

# Create the TimeSeries table
cursor.execute('''
CREATE TABLE IF NOT EXISTS TimeSeries (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    value REAL,
    date TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
''')

# Generate synthetic data for TimeSeries table
start_date = datetime(2023, 1, 1)
num_entries = 100

time_series_data = []

for company in companies:
    company_id = company[0]
    for i in range(num_entries):
        date = start_date + timedelta(days=i)
        value = round(random.uniform(100, 500), 2)  # Generate a random value between 100 and 500
        time_series_data.append((company_id, value, date.strftime('%Y-%m-%d')))

# Insert data into the TimeSeries table
cursor.executemany('''
INSERT INTO TimeSeries (company_id, value, date)
VALUES (?, ?, ?)
''', time_series_data)

# Commit the transaction and close the connection
conn.commit()
conn.close()



# Define the Bollinger Band width as a global variable
bollinger_width = 2

# Define the Window Size for Movine Average
window_size = 20

class Company:
    def __init__(self, company_id, ticker, name):
        self.company_id = company_id
        self.ticker = ticker
        self.name = name
        self.time_series = None
        self.high_bollinger = None
        self.low_bollinger = None
        self.moving_average = None
        self.grade = None

    def load_time_series(self, conn):
        query = '''
        SELECT date, value
        FROM TimeSeries
        WHERE company_id = ?
        '''
        cursor = conn.cursor()
        cursor.execute(query, (self.company_id,))
        self.time_series = cursor.fetchall()

    def calculate_bollinger_bands(self, window=20, num_std_dev=2):
        df = pd.DataFrame(self.time_series, columns=['date', 'value'])
        df['moving_average'] = df['value'].rolling(window=window).mean()
        df['std_dev'] = df['value'].rolling(window=window).std()
        df['high_bollinger'] = df['moving_average'] + (df['std_dev'] * num_std_dev)
        df['low_bollinger'] = df['moving_average'] - (df['std_dev'] * num_std_dev)
        
        self.moving_average = df['moving_average'].tolist()
        self.high_bollinger = df['high_bollinger'].tolist()
        self.low_bollinger = df['low_bollinger'].tolist()

    def assign_grade(self):
        latest_value = self.time_series['value'].iloc[-1]
        if latest_value > self.high_bollinger.iloc[-1]:
            self.grade = 'A'
        elif latest_value < self.low_bollinger.iloc[-1]:
            self.grade = 'C'
        else:
            self.grade = 'B'

    def display(self):
        print(f'Company: {self.name} ({self.ticker})')
        print(f'Grade: {self.grade}')
        print('Time Series Data:')
        print(self.time_series[-5:])  # Print last 5 entries for brevity
        print('Moving Average:')
        print(self.moving_average[-5:])
        print('High Bollinger Band:')
        print(self.high_bollinger[-5:])
        print('Low Bollinger Band:')
        print(self.low_bollinger[-5:])

class DomesticCompany(Company):
    def __init__(self, company_id, ticker, name):
        super().__init__(company_id, ticker, name)

class ForeignCompany(Company):
    def __init__(self, company_id, ticker, name):
        super().__init__(company_id, ticker, name)

def get_company_by_ticker(ticker, conn):
    cursor = conn.cursor()
    query = 'SELECT id, ticker, name FROM companies WHERE ticker = ?'
    cursor.execute(query, (ticker,))
    row = cursor.fetchone()
    if row:
        return Company(row[0], row[1], row[2])

def get_company_by_ticker_or_id(identifier, conn):
    cursor = conn.cursor()
    if isinstance(identifier, int):
        query = 'SELECT id, ticker, name FROM companies WHERE id = ?'
        cursor.execute(query, (identifier,))
    else:
        query = 'SELECT id, ticker, name FROM companies WHERE ticker = ?'
        cursor.execute(query, (identifier,))
    row = cursor.fetchone()
    if row:
        return Company(row[0], row[1], row[2])
    else:
        return None

# Example usage:
conn = sqlite3.connect('company_database.db')

# Get company by ticker or ID
company = get_company_by_ticker('GOOGL', conn)
if company:
    company.load_time_series(conn)
    company.calculate_bollinger_bands()
    company.assign_grade()
    company.display()

conn.close()