import oracledb
import os

DB_USER = "APP_USER"
DB_PASSWORD = "MatKhauManh2025!!" 
WALLET_PASSWORD = "MatKhauManh2025!!" 
WALLET_DIR = os.path.join(os.getcwd(), "wallet")
DSN_ALIAS = "db1_high"

try:
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DSN_ALIAS,
        config_dir=WALLET_DIR,
        wallet_location=WALLET_DIR,
        wallet_password=WALLET_PASSWORD
    )
    with connection.cursor() as cursor:
        print("ĐAll Accessible Tables...")
        sql = "SELECT owner, table_name FROM all_tables WHERE owner = 'APP_USER' ORDER BY table_name"
        cursor.execute(sql)
        rows = cursor.fetchall()

        print(f"Tổng cộng tìm thấy: {len(rows)} bảng")
        print("-" * 50)
        print(f"{'OWNER':<20} | {'TABLE_NAME'}")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<20} | {row[1]}")
    connection.close()
    
except oracledb.Error as e:
    print("Lỗi kết nối:")
    print(e)