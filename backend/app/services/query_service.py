import sys
from app.db.database import SessionLocal
from app.models.mock_data import Order, Customer, Product

def test_query_orders():
    """
    ฟังก์ชันสำหรับทดสอบดึงข้อมูล Orders มาแสดง
    เพื่อให้มั่นใจว่าโครงสร้างฐานข้อมูลใช้งานได้จริง
    """
    db = SessionLocal()
    try:
        print("🔍 กำลังดึงข้อมูล Orders 5 รายการล่าสุด...")
        print("-" * 60)
        
        # ค้นหา Orders พร้อม join ข้อมูล Customer และ Product
        results = (
            db.query(Order, Customer, Product)
            .join(Customer, Order.customer_id == Customer.id)
            .join(Product, Order.product_id == Product.id)
            .limit(5)
            .all()
        )
        
        if not results:
            print("❌ ไม่พบข้อมูลในตาราง Orders")
            return
            
        for order, customer, product in results:
            total_price = order.quantity * product.price
            print(f"📦 Order ID: {order.id} | วันที่: {order.date}")
            print(f"   👤 ลูกค้า: {customer.name} ({customer.email})")
            print(f"   🛒 สินค้า: {product.name} (x{order.quantity})")
            print(f"   💰 ยอดรวม: ฿{total_price:,.2f}")
            print("-" * 60)
            
        print("✅ ทดสอบดึงข้อมูลสำเร็จ ฐานข้อมูลพร้อมใช้งาน!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # แก้ปัญหา encoding บน Windows ให้แสดงภาษาไทยได้
    sys.stdout.reconfigure(encoding="utf-8")
    test_query_orders()
