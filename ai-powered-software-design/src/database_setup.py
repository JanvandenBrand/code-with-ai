from pydoc import text
from sqlite3 import IntegrityError
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.context import CryptContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Create an engine that stores data in the local directory's ecommerce.db file.
try:
    engine = create_engine('sqlite:///ecommerce.db')
    connection = engine.connect()
    logger.info("Connection successful")
except Exception as e:
    logger.error(f"Connection error: {e}")

# Create a base class for our classes definitions.
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """
    User class which will be mapped to the users table.

    :param id: Primary key
    :type id: int
    :param username: Username of the user
    :type username: str
    :param email: Email of the user
    :type email: str
    :param password: Password of the user (hashed)
    :type password: str
    :param is_active: Whether the user is active
    :type is_active: bool
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        self.password = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

class Product(Base):
    """
    Product class which will be mapped to the products table.

    :param id: Primary key
    :type id: int
    :param name: Name of the product
    :type name: str
    :param description: Description of the product
    :type description: str
    :param price: Price of the product
    :type price: float
    :param quantity: Quantity of the product in stock
    :type quantity: int
    :param category: Category of the product
    :type category: str
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    category = Column(Enum('Electronics', 'Clothing', 'Books', 'Home', 'Toys', name='product_category'))

class Order(Base):
    """
    Order class which will be mapped to the orders table.

    :param id: Primary key
    :type id: int
    :param user_id: Foreign key to the users table
    :type user_id: int
    :param total_amount: Total amount of the order
    :type total_amount: float
    :param order_date: Date of the order
    :type order_date: date
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    order_date = Column(Date, nullable=False)

    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    """
    OrderItem class which will be mapped to the order_items table.

    :param id: Primary key
    :type id: int
    :param order_id: Foreign key to the orders table
    :type order_id: int
    :param product_id: Foreign key to the products table
    :type product_id: int
    :param quantity: Quantity of the product in the order
    :type quantity: int
    :param price: Price of the product in the order
    :type price: float
    """
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship('Order', back_populates='order_items')
    product = relationship('Product')

# Establish relationships
User.orders = relationship('Order', order_by=Order.id, back_populates='user')

# Drop all tables (use with caution in a development environment)
Base.metadata.drop_all(engine)

# Create all tables in the engine.
Base.metadata.create_all(engine)

# Create a configured "Session" class.
Session = sessionmaker(bind=engine)

# Create a Session.
session = Session()

# CRUD Operations for User
def create_user(username, email, password):
    """
    Create a new user.

    :param username: Username of the user
    :type username: str
    :param email: Email of the user
    :type email: str
    :param password: Password of the user
    :type password: str
    :return: The created user
    :rtype: User
    """
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    try:
        session.add(new_user)
        session.commit()
        logger.info(f"User created: {username}")
        return new_user
    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError: {e}")
        return None

def read_user(user_id):
    """
    Retrieve a user by ID.

    :param user_id: ID of the user
    :type user_id: int
    :return: The retrieved user
    :rtype: User
    """
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        logger.info(f"User retrieved: {user.username}")
    else:
        logger.warning(f"User not found: {user_id}")
    return user

def update_user(user_id, username=None, email=None, password=None):
    """
    Update a user's information.

    :param user_id: ID of the user
    :type user_id: int
    :param username: New username of the user
    :type username: str, optional
    :param email: New email of the user
    :type email: str, optional
    :param password: New password of the user
    :type password: str, optional
    :return: The updated user
    :rtype: User
    """
    user = read_user(user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        session.commit()
        logger.info(f"User updated: {user.username}")
    return user

def delete_user(user_id):
    """
    Delete a user by ID.

    :param user_id: ID of the user
    :type user_id: int
    :return: The deleted user
    :rtype: User
    """
    user = read_user(user_id)
    if user:
        session.delete(user)
        session.commit()
        logger.info(f"User deleted: {user.username}")
    return user

# CRUD Operations for Product
def create_product(name, description, price, quantity):
    """
    Create a new product.

    :param name: Name of the product
    :type name: str
    :param description: Description of the product
    :type description: str
    :param price: Price of the product
    :type price: float
    :param quantity: Quantity of the product in stock
    :type quantity: int
    :return: The created product
    :rtype: Product
    """
    new_product = Product(name=name, description=description, price=price, quantity=quantity)
    session.add(new_product)
    session.commit()
    logger.info(f"Product created: {name}")
    return new_product

def read_product(product_id):
    """
    Retrieve a product by ID.

    :param product_id: ID of the product
    :type product_id: int
    :return: The retrieved product
    :rtype: Product
    """
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        logger.info(f"Product retrieved: {product.name}")
    else:
        logger.warning(f"Product not found: {product_id}")
    return product

def update_product(product_id, name=None, description=None, price=None, quantity=None):
    """
    Update a product's information.

    :param product_id: ID of the product
    :type product_id: int
    :param name: New name of the product
    :type name: str, optional
    :param description: New description of the product
    :type description: str, optional
    :param price: New price of the product
    :type price: float, optional
    :param quantity: New quantity of the product in stock
    :type quantity: int, optional
    :return: The updated product
    :rtype: Product
    """
    product = read_product(product_id)
    if product:
        if name:
            product.name = name
        if description:
            product.description = description
        if price:
            product.price = price
        if quantity:
            product.quantity = quantity
        session.commit()
        logger.info(f"Product updated: {product.name}")
    return product

def delete_product(product_id):
    """
    Delete a product by ID.

    :param product_id: ID of the product
    :type product_id: int
    :return: The deleted product
    :rtype: Product
    """
    product = read_product(product_id)
    if product:
        session.delete(product)
        session.commit()
        logger.info(f"Product deleted: {product.name}")
    return product

# CRUD Operations for Order
def create_order(user_id, total_amount):
    """
    Create a new order.

    :param user_id: ID of the user who placed the order
    :type user_id: int
    :param total_amount: Total amount of the order
    :type total_amount: float
    :return: The created order
    :rtype: Order
    """
    new_order = Order(user_id=user_id, total_amount=total_amount)
    session.add(new_order)
    session.commit()
    logger.info(f"Order created: {new_order.id}")
    return new_order

def read_order(order_id):
    """
    Retrieve an order by ID.

    :param order_id: ID of the order
    :type order_id: int
    :return: The retrieved order
    :rtype: Order
    """
    order = session.query(Order).filter(Order.id == order_id).first()
    if order:
        logger.info(f"Order retrieved: {order.id}")
    else:
        logger.warning(f"Order not found: {order_id}")
    return order

def update_order(order_id, total_amount=None):
    """
    Update an order's information.

    :param order_id: ID of the order
    :type order_id: int
    :param total_amount: New total amount of the order
    :type total_amount: float, optional
    :return: The updated order
    :rtype: Order
    """
    order = read_order(order_id)
    if order:
        if total_amount:
            order.total_amount = total_amount
        session.commit()
        logger.info(f"Order updated: {order.id}")
    return order

def delete_order(order_id):
    """
    Delete an order by ID.

    :param order_id: ID of the order
    :type order_id: int
    :return: The deleted order
    :rtype: Order
    """
    order = read_order(order_id)
    if order:
        session.delete(order)
        session.commit()
        logger.info(f"Order deleted: {order.id}")
    return order

# CRUD Operations for OrderItem
def create_order_item(order_id, product_id, quantity, price):
    """
    Create a new order item.

    :param order_id: ID of the order
    :type order_id: int
    :param product_id: ID of the product
    :type product_id: int
    :param quantity: Quantity of the product ordered
    :type quantity: int
    :param price: Price of the product ordered
    :type price: float
    :return: The created order item
    :rtype: OrderItem
    """
    new_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
    session.add(new_order_item)
    session.commit()
    logger.info(f"Order item created: {new_order_item.id}")
    return new_order_item

def read_order_item(order_item_id):
    """
    Retrieve an order item by ID.

    :param order_item_id: ID of the order item
    :type order_item_id: int
    :return: The retrieved order item
    :rtype: OrderItem
    """
    order_item = session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if order_item:
        logger.info(f"Order item retrieved: {order_item.id}")
    else:
        logger.warning(f"Order item not found: {order_item_id}")
    return order_item

def update_order_item(order_item_id, quantity=None):
    """
    Update an order item's information.

    :param order_item_id: ID of the order item
    :type order_item_id: int
    :param quantity: New quantity of the product ordered
    :type quantity: int, optional
    :return: The updated order item
    :rtype: OrderItem
    """
    order_item = read_order_item(order_item_id)
    if order_item:
        if quantity:
            order_item.quantity = quantity
        session.commit()
        logger.info(f"Order item updated: {order_item.id}")
    return order_item

def delete_order_item(order_item_id):
    """
    Delete an order item by ID.

    :param order_item_id: ID of the order item
    :type order_item_id: int
    :return: The deleted order item
    :rtype: OrderItem
    """
    order_item = read_order_item(order_item_id)
    if order_item:
        session.delete(order_item)
        session.commit()
        logger.info(f"Order item deleted: {order_item.id}")
    return order_item

# Add EXPLAIN functionalty
def explain_query(query):
    """
    Explain the execution plan of a query.

    :param query: The query to explain
    :type query: str
    :return: The execution plan
    :rtype: list of dict
    """
    result = connection.execute(text(f"EXPLAIN {query}"))
    return result.fetchall()


# Function to add sample data
def add_sample_data():
    # Adding users
    user_data = [
        ("Alice", "alice@example.com", "password1"),
        ("Bob", "bob@example.com", "password2"),
        ("Charlie", "charlie@example.com", "password3"),
        ("David", "david@example.com", "password4"),
        ("Eve", "eve@example.com", "password5"),
        ("Frank", "frank@example.com", "password6"),
        ("Grace", "grace@example.com", "password7"),
        ("Heidi", "heidi@example.com", "password8"),
        ("Ivan", "ivan@example.com", "password9"),
        ("Judy", "judy@example.com", "password10")
    ]
    for username, email, password in user_data:
        create_user(username, email, password)

    # Adding products
    product_data = [
        ("Laptop", "High performance laptop", 1000, 50),
        ("Smartphone", "Latest model smartphone", 500, 100),
        ("Tablet", "10-inch screen tablet", 300, 75),
        ("Monitor", "24-inch monitor", 150, 60),
        ("Keyboard", "Mechanical keyboard", 50, 200),
        ("Mouse", "Wireless mouse", 25, 150),
        ("Printer", "All-in-one printer", 200, 40),
        ("Router", "High-speed router", 75, 80),
        ("Webcam", "HD webcam", 60, 90),
        ("Headphones", "Noise-cancelling headphones", 80, 70)
    ]
    for name, description, price, quantity in product_data:
        create_product(name, description, price, quantity)

    # Adding orders
    for i in range(1, 11):
        create_order(i, 100.0 * i)  # Assuming total_amount is 100.0 * i for simplicity

    # Adding order_items
    order_item_data = [
        (1, 1, 2, 1000),
        (1, 2, 1, 500),
        (2, 3, 1, 300),
        (2, 4, 2, 150),
        (3, 5, 3, 50),
        (3, 6, 1, 25),
        (4, 7, 2, 200),
        (4, 8, 1, 75),
        (5, 9, 1, 60),
        (5, 10, 2, 80),
        (6, 1, 1, 1000),
        (6, 2, 2, 500),
        (7, 3, 1, 300),
        (7, 4, 1, 150),
        (8, 5, 2, 50),
        (8, 6, 1, 25),
        (9, 7, 3, 200),
        (9, 8, 1, 75),
        (10, 9, 1, 60),
        (10, 10, 1, 80)
    ]
    for order_id, product_id, quantity, price in order_item_data:
        create_order_item(order_id, product_id, quantity, price)

# Example usage
if __name__ == "__main__":
    try:
        # Add sample data to the database
        add_sample_data()

        # Create a new user
        user = create_user("johndoe", "john@example.com", "securepassword")
        if user:
            print(f"Created User: {user.username}, {user.email}")
        else:
            print("Failed to create user due to duplicate entry.")

        # Attempt to create a duplicate user
        duplicate_user = create_user("johndoe", "john@example.com", "securepassword")
        if duplicate_user:
            print(f"Created User: {duplicate_user.username}, {duplicate_user.email}")
        else:
            print("Failed to create duplicate user due to duplicate entry.")

        # Explain the query to read the user
        query = f"SELECT * FROM users WHERE id = {user.id}"
        execution_plan = explain_query(query)
        print("Execution Plan for reading user:")
        for row in execution_plan:
            print(row)

        # Read the user
        user = read_user(user.id)
        print(f"Retrieved User: {user.username}, {user.email}")

        # Update the user
        user = update_user(user.id, username="john_doe", email="john_doe@example.com")
        print(f"Updated User: {user.username}, {user.email}")

        # Delete the user
        delete_user(user.id)
        print(f"Deleted User: {user.username}, {user.email}")

        # Create a new product
        product = create_product("Sample Product", "This is a sample product.", 19.99, 100)
        print(f"Created Product: {product.name}, {product.description}, {product.price}, {product.quantity}")

        # Read the product
        product = read_product(product.id)
        print(f"Retrieved Product: {product.name}, {product.description}, {product.price}, {product.quantity}")

        # Update the product
        product = update_product(product.id, name="Updated Product", price=29.99)
        print(f"Updated Product: {product.name}, {product.description}, {product.price}, {product.quantity}")

        # Delete the product
        delete_product(product.id)
        print(f"Deleted Product: {product.name}, {product.description}, {product.price}, {product.quantity}")

        # Create a new order
        order = create_order(user.id, 39.98)
        print(f"Created Order: {order.id}, User ID: {order.user_id}, Total Amount: {order.total_amount}")

        # Create a new order item
        order_item = create_order_item(order.id, product.id, 2, product.price)
        print(f"Created Order Item: {order_item.id}, Order ID: {order_item.order_id}, Product ID: {order_item.product_id}, Quantity: {order_item.quantity}, Price: {order_item.price}")
    except Exception as e:
        logger.error(f"Error during example usage: {e}")