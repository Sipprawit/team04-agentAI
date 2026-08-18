from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from datetime import date, timedelta
from app.db.database import Base, engine, SessionLocal
import random

# --- กำหนดโครงสร้างตาราง (Models) ---

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    date = Column(Date)

# --- ฟังก์ชันสร้างและจำลองข้อมูล ---

def init_mock_db():
    """
    สร้างตารางและข้อมูลจำลองถ้ายังไม่มีข้อมูล
    """
    # สร้างตารางทั้งหมดในฐานข้อมูล
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # ตรวจสอบว่ามีข้อมูลในตาราง customers หรือไม่
        if db.query(Customer).first() is None:
            print("🌱 กำลังสร้างข้อมูลจำลอง (Mock Data) สำหรับร้านค้า (E-Commerce)...")
            
            # 1. สร้าง Customers (10 รายการ)
            customers_data = [
                Customer(name="สมชาย ใจดี", email="somchai@example.com"),
                Customer(name="สมหญิง รักเรียน", email="somying@example.com"),
                Customer(name="วิชัย เก่งการค้า", email="wichai@example.com"),
                Customer(name="มานี มีนา", email="manee@example.com"),
                Customer(name="ปิติ ยินดี", email="piti@example.com"),
                Customer(name="John Doe", email="john.doe@example.com"),
                Customer(name="Jane Smith", email="jane.smith@example.com"),
                Customer(name="Taro Yamada", email="taro@example.com"),
                Customer(name="Anna Lee", email="anna@example.com"),
                Customer(name="David Beckham", email="david@example.com")
            ]
            db.add_all(customers_data)
            db.commit()
            
            # 2. สร้าง Products (10 รายการ)
            products_data = [
                Product(name="Laptop Pro 15", price=45000.0),
                Product(name="Smartphone X", price=25000.0),
                Product(name="Wireless Earbuds", price=3500.0),
                Product(name="Mechanical Keyboard", price=4200.0),
                Product(name="Gaming Mouse", price=1500.0),
                Product(name="4K Monitor", price=12000.0),
                Product(name="USB-C Hub", price=900.0),
                Product(name="External SSD 1TB", price=3800.0),
                Product(name="Tablet Mini", price=15000.0),
                Product(name="Smart Watch", price=8900.0)
            ]
            db.add_all(products_data)
            db.commit()

            # ดึงข้อมูลลูกค้าและสินค้าที่เพิ่งสร้างเพื่อใช้ ID
            customers = db.query(Customer).all()
            products = db.query(Product).all()
            today = date.today()
            
            # 3. สร้าง Orders (10 รายการ)
            orders_data = []
            for _ in range(10):
                customer = random.choice(customers)
                product = random.choice(products)
                quantity = random.randint(1, 5)
                # สุ่มวันที่ย้อนหลังไม่เกิน 30 วัน
                order_date = today - timedelta(days=random.randint(0, 30))
                
                orders_data.append(
                    Order(
                        customer_id=customer.id,
                        product_id=product.id,
                        quantity=quantity,
                        date=order_date
                    )
                )
            
            db.add_all(orders_data)
            db.commit()
            print("✅ สร้างข้อมูลจำลอง E-Commerce ทั้ง 3 ตารางเสร็จเรียบร้อย!")
        else:
            print("✅ ข้อมูลจำลองมีอยู่แล้ว ข้ามการสร้างใหม่")
            
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    init_mock_db()
