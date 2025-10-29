import sqlite3
import sys
import io
import random
from datetime import datetime, timedelta
from faker import Faker

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

fake = Faker('tr_TR')
Faker.seed(42)
random.seed(42)

def clean_name_for_email(name):
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c',
    }
    for turkish_char, latin_char in char_map.items():
        name = name.replace(turkish_char, latin_char)
    return name.lower()

conn = sqlite3.connect('data/ecommerce.db')
cursor = conn.cursor()

print("[*] Creating e-commerce database...")

# Drop existing tables if any
cursor.execute('DROP TABLE IF EXISTS reviews')
cursor.execute('DROP TABLE IF EXISTS order_items')
cursor.execute('DROP TABLE IF EXISTS orders')
cursor.execute('DROP TABLE IF EXISTS products')
cursor.execute('DROP TABLE IF EXISTS campaigns')
cursor.execute('DROP TABLE IF EXISTS customers')
cursor.execute('DROP TABLE IF EXISTS categories')

# ============================================
# CREATE TABLES
# ============================================

print("\n[*] Creating tables...")

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    birth_date DATE,
    gender TEXT,
    registration_date DATE NOT NULL,
    city TEXT,
    customer_segment TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    parent_category_id INTEGER,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    brand TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    created_date DATE NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    discount_rate REAL NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    min_basket_amount REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date DATETIME NOT NULL,
    order_status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    shipping_cost REAL NOT NULL,
    campaign_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_rate REAL DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATETIME NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

print("[+] Tables created successfully!")

# ============================================
# CATEGORIES
# ============================================

print("\n[*] Inserting categories...")

categories_data = [
    ('Elektronik', None),
    ('Moda', None),
    ('Ev & Yaşam', None),
    ('Spor & Outdoor', None),
    ('Kitap & Müzik', None),
    ('Telefon & Aksesuar', 1),
    ('Bilgisayar & Tablet', 1),
    ('Televizyon & Ses Sistemleri', 1),
    ('Kadın Giyim', 2),
    ('Erkek Giyim', 2),
    ('Ayakkabı', 2),
    ('Mobilya', 3),
    ('Mutfak Gereçleri', 3),
    ('Dekorasyon', 3),
    ('Fitness', 4),
    ('Outdoor', 4),
    ('Roman', 5),
    ('Bilim', 5),
]

cursor.executemany('INSERT INTO categories (category_name, parent_category_id) VALUES (?, ?)', categories_data)
print(f"[+] {len(categories_data)} categories inserted!")

# ============================================
# CAMPAIGNS
# ============================================

print("\n[*] Inserting campaigns...")

campaigns_data = [
    ('Yılbaşı Kampanyası', 20, '2022-12-20', '2023-01-05', 500),
    ('Sevgililer Günü', 15, '2023-02-10', '2023-02-14', 200),
    ('Ramazan Kampanyası', 25, '2023-03-22', '2023-04-21', 300),
    ('23 Nisan Özel', 10, '2023-04-20', '2023-04-24', 100),
    ('Yaz İndirimi', 30, '2023-06-15', '2023-08-31', 400),
    ('Black Friday', 40, '2023-11-24', '2023-11-27', 600),
    ('Yeni Yıl 2024', 20, '2023-12-25', '2024-01-10', 500),
    ('Bahar İndirimi', 15, '2024-03-01', '2024-04-30', 250),
    ('Ramazan 2024', 25, '2024-03-10', '2024-04-10', 300),
    ('Yaz Sonu', 35, '2024-08-15', '2024-09-15', 350),
    ('Eylül Kampanyası', 20, '2024-09-01', '2024-09-30', 400),
    ('Kasım Fırsatları', 30, '2024-11-01', '2024-11-30', 500),
    ('Black Friday 2024', 45, '2024-11-29', '2024-12-02', 700),
]

cursor.executemany('''
    INSERT INTO campaigns (campaign_name, discount_rate, start_date, end_date, min_basket_amount)
    VALUES (?, ?, ?, ?, ?)
''', campaigns_data)

print(f"[+] {len(campaigns_data)} campaigns inserted!")

# ============================================
# PRODUCTS
# ============================================

print("\n[*] Inserting products...")

brands = {
    6: ['Apple', 'Samsung', 'Xiaomi', 'Huawei', 'Oppo'],
    7: ['Apple', 'Lenovo', 'HP', 'Dell', 'Asus'],
    8: ['Samsung', 'LG', 'Sony', 'Philips', 'Vestel'],
    9: ['Zara', 'Mango', 'Koton', 'LC Waikiki', 'H&M'],
    10: ['Mavi', 'Colin\'s', 'Levi\'s', 'Defacto', 'Polo'],
    11: ['Nike', 'Adidas', 'Puma', 'New Balance', 'Skechers'],
    12: ['IKEA', 'Bellona', 'Alfemo', 'Istikbal', 'Kilim'],
    13: ['Tefal', 'Karaca', 'Arzum', 'Korkmaz', 'Fakir'],
    14: ['Madame Coco', 'English Home', 'Koçtaş', 'Ikea', 'Chakra'],
    15: ['Nike', 'Adidas', 'Reebok', 'Under Armour', 'Puma'],
    16: ['The North Face', 'Columbia', 'Quechua', 'Jack Wolfskin', 'Salomon'],
    17: ['Doğan Kitap', 'Can Yayınları', 'İş Bankası Kültür', 'Yapı Kredi', 'Epsilon'],
    18: ['TÜBİTAK', 'Bilim ve Gelecek', 'Alfa', 'Nobel', 'Paloma'],
}

product_templates = {
    6: ['Akıllı Telefon', 'Telefon Kılıfı', 'Şarj Cihazı', 'Kulaklık', 'Powerbank'],
    7: ['Laptop', 'Tablet', 'Mouse', 'Klavye', 'Monitör'],
    8: ['Smart TV', 'Soundbar', 'Hoparlör', 'Kulaklık', 'TV Ünitesi'],
    9: ['Elbise', 'Bluz', 'Pantolon', 'Ceket', 'Triko'],
    10: ['Gömlek', 'Tişört', 'Pantolon', 'Ceket', 'Kazak'],
    11: ['Spor Ayakkabı', 'Günlük Ayakkabı', 'Bot', 'Sandalet', 'Terlik'],
    12: ['Koltuk Takımı', 'Yatak', 'Gardolap', 'Yemek Masası', 'TV Ünitesi'],
    13: ['Tencere Seti', 'Tava', 'Blender', 'Mikser', 'Çay Makinesi'],
    14: ['Vazo', 'Tablo', 'Mum', 'Saksı', 'Ayna'],
    15: ['Yoga Matı', 'Dambıl Seti', 'Koşu Bandı', 'Fitness Topu', 'Direnç Bandı'],
    16: ['Çadır', 'Uyku Tulumu', 'Sırt Çantası', 'Trekking Ayakkabısı', 'Matara'],
    17: ['Roman', 'Hikaye Kitabı', 'Polisiye', 'Macera Romanı', 'Klasik'],
    18: ['Bilim Kitabı', 'Astronomi', 'Fizik', 'Biyoloji', 'Matematik'],
}

products = []
start_date = datetime(2021, 1, 1)
end_date = datetime(2025, 1, 1)

for category_id in range(6, 19):
    for _ in range(random.randint(15, 30)):
        template = random.choice(product_templates[category_id])
        brand = random.choice(brands[category_id])
        product_name = f"{brand} {template}"
        
        if category_id in [6, 7, 8, 12]:
            price = round(random.uniform(500, 25000), 2)
        elif category_id in [9, 10, 11]:
            price = round(random.uniform(50, 2000), 2)
        else:
            price = round(random.uniform(20, 500), 2)
        
        stock = random.randint(0, 500)
        created_date = fake.date_between(start_date=start_date, end_date=end_date)
        
        products.append((product_name, category_id, brand, price, stock, created_date))

cursor.executemany('''
    INSERT INTO products (product_name, category_id, brand, price, stock_quantity, created_date)
    VALUES (?, ?, ?, ?, ?, ?)
''', products)

print(f"[+] {len(products)} products inserted!")

# ============================================
# CUSTOMERS
# ============================================

print("\n[*] Inserting customers...")

turkish_cities = {
    'İstanbul': 30,
    'Ankara': 15,
    'İzmir': 12,
    'Bursa': 7,
    'Antalya': 6,
    'Adana': 5,
    'Gaziantep': 5,
    'Konya': 5,
    'Mersin': 4,
    'Kayseri': 4,
    'Eskişehir': 4,
    'Diyarbakır': 3
}

customers = []
customer_count = 5000

for _ in range(customer_count):
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Clean email from Turkish characters
    email_first = clean_name_for_email(first_name)
    email_last = clean_name_for_email(last_name)
    email = f"{email_first}.{email_last}{random.randint(1, 9999)}@gmail.com"
    
    # Phone with +90
    phone_number = fake.phone_number().replace('0', '', 1)  # Remove leading 0
    phone = f"+90{phone_number}"
    
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=75)
    
    # Normalized gender values
    gender = random.choice(['erkek', 'kadin', 'belirtmek_istemiyorum'])
    
    registration_date = fake.date_between(start_date=datetime(2022, 1, 1), end_date=datetime(2025, 1, 1))
    city = random.choices(list(turkish_cities.keys()), weights=list(turkish_cities.values()))[0]
    
    customers.append((first_name, last_name, email, phone, birth_date, gender, registration_date, city, None))

cursor.executemany('''
    INSERT INTO customers (first_name, last_name, email, phone, birth_date, gender, registration_date, city, customer_segment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', customers)

print(f"[+] {customer_count} customers inserted!")

# ============================================
# ORDERS WITH GROWTH TREND AND SEASONALITY
# ============================================

print("\n[*] Creating orders...")

# Normalized status and payment method values
order_statuses = ['teslim_edildi', 'teslim_edildi', 'teslim_edildi', 'kargoda', 'hazirlaniyor', 'iptal']
payment_methods = ['kredi_karti', 'kredi_karti', 'havale', 'kapida_odeme']

cursor.execute('SELECT product_id, price FROM products')
products_list = cursor.fetchall()

cursor.execute('SELECT customer_id, registration_date FROM customers')
customers_list = cursor.fetchall()

cursor.execute('SELECT campaign_id, start_date, end_date, discount_rate, min_basket_amount FROM campaigns')
campaigns_list = cursor.fetchall()

def get_monthly_multiplier(month):
    seasonal_factors = {
        1: 1.0, 2: 0.9, 3: 1.2, 4: 1.1, 5: 1.0, 6: 1.3,
        7: 1.4, 8: 1.3, 9: 1.0, 10: 1.1, 11: 1.8, 12: 1.5,
    }
    return seasonal_factors.get(month, 1.0)

def get_yearly_growth(year):
    base_year = 2022
    growth_rate = 0.25
    return 1.0 + (year - base_year) * growth_rate

def get_applicable_campaign(order_date, total_amount):
    order_date_str = order_date.strftime('%Y-%m-%d')
    for campaign_id, start_date, end_date, discount_rate, min_basket in campaigns_list:
        if start_date <= order_date_str <= end_date:
            if min_basket is None or total_amount >= min_basket:
                return campaign_id, discount_rate
    return None, 0

orders = []
order_items_list = []
customer_spending = {c[0]: 0 for c in customers_list}

order_id_counter = 1

for customer_id, registration_date in customers_list:
    order_count = random.choices(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20],
        weights=[100, 200, 250, 200, 150, 100, 50, 30, 20, 10, 5, 3, 1]
    )[0]
    
    for _ in range(order_count):
        order_date = fake.date_time_between(
            start_date=datetime.strptime(registration_date, '%Y-%m-%d'),
            end_date=datetime(2025, 10, 29)
        )
        
        year = order_date.year
        month = order_date.month
        
        growth_factor = get_yearly_growth(year)
        seasonal_factor = get_monthly_multiplier(month)
        
        if random.random() > (growth_factor * seasonal_factor) / 3.0:
            continue
        
        order_status = random.choice(order_statuses)
        payment_method = random.choice(payment_methods)
        shipping_cost = round(random.choice([0, 0, 0, 15.99, 24.99, 34.99]), 2)
        
        product_count = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        selected_products = random.sample(products_list, min(product_count, len(products_list)))
        
        total_amount = shipping_cost
        
        for product_id, product_price in selected_products:
            quantity = random.choices([1, 2, 3, 4], weights=[70, 20, 7, 3])[0]
            unit_price = product_price
            discount_rate = random.choices([0, 5, 10, 15, 20, 25], weights=[60, 15, 10, 8, 5, 2])[0]
            
            line_total = quantity * unit_price * (1 - discount_rate / 100)
            total_amount += line_total
            
            order_items_list.append((order_id_counter, product_id, quantity, unit_price, discount_rate))
        
        total_amount = round(total_amount, 2)
        
        campaign_id, campaign_discount = get_applicable_campaign(order_date, total_amount)
        if campaign_id:
            total_amount = round(total_amount * (1 - campaign_discount / 100), 2)
        
        if order_status == 'teslim_edildi':
            customer_spending[customer_id] += total_amount
        
        orders.append((order_id_counter, customer_id, order_date, order_status, total_amount, payment_method, shipping_cost, campaign_id))
        order_id_counter += 1

cursor.executemany('''
    INSERT INTO orders (order_id, customer_id, order_date, order_status, total_amount, payment_method, shipping_cost, campaign_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', orders)

cursor.executemany('''
    INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_rate)
    VALUES (?, ?, ?, ?, ?)
''', order_items_list)

print(f"[+] {len(orders)} orders and {len(order_items_list)} order items inserted!")

# ============================================
# CUSTOMER SEGMENTATION
# ============================================

print("\n[*] Calculating customer segmentation...")

spending_sorted = sorted(customer_spending.items(), key=lambda x: x[1], reverse=True)

total_customers = len(spending_sorted)
platinum_limit = int(total_customers * 0.10)
gold_limit = int(total_customers * 0.30)
silver_limit = int(total_customers * 0.65)

for idx, (customer_id, spending) in enumerate(spending_sorted):
    if idx < platinum_limit:
        segment = 'platinum'
    elif idx < gold_limit:
        segment = 'gold'
    elif idx < silver_limit:
        segment = 'silver'
    else:
        segment = 'bronze'
    
    cursor.execute('UPDATE customers SET customer_segment = ? WHERE customer_id = ?', (segment, customer_id))

print("[+] Customer segmentation completed!")

cursor.execute('SELECT customer_segment, COUNT(*) FROM customers GROUP BY customer_segment')
segment_stats = cursor.fetchall()
print("\n[*] Segment Distribution:")
for segment, count in segment_stats:
    print(f"   {segment}: {count} customers ({count/customer_count*100:.1f}%)")

# ============================================
# REVIEWS
# ============================================

print("\n[*] Inserting reviews...")

review_templates = {
    5: [
        'Mükemmel bir ürün! Kesinlikle tavsiye ederim. Kalitesi çok yüksek ve beklentilerimin çok üstünde çıktı.',
        'Harika! Tam aradığım gibi. Fiyat/performans açısından çok başarılı. Kargo da çok hızlıydı.',
        'Bu ürünü aldığıma çok memnun oldum. Kalitesi gerçekten çok iyi, hiç pişman olmadım.',
        'Kesinlikle 5 yıldız hak ediyor! Ürün açıklamasında yazanların hepsine sahip. Çok beğendim.',
        'İkinci defa alıyorum, aileme hediye ettim. Herkes çok memnun kaldı. Kalite farkı belli oluyor.',
        'Paranın hakkını veriyor. Daha önce pahalı markaları kullandım ama bu ürün onlardan hiç geri kalmıyor.',
        'Çok kaliteli bir ürün. Aldığım en iyi alışverişlerden biriydi. Herkese gönül rahatlığıyla önerebilirim.',
    ],
    4: [
        'Gayet iyi bir ürün. Beklentilerimi karşıladı. Küçük detaylar dışında memnunum.',
        'Güzel ürün. Fiyatına göre gayet başarılı. Birkaç eksik tarafı var ama genel olarak iyi.',
        'Beğendim, kaliteli. Sadece kargo biraz geç geldi ama ürün güzel.',
        'İyi bir alışveriş oldu. Ürün fotoğraflardaki gibi. Çok memnun oldum diyemem ama iyi.',
        'Fiyatına göre iyi sayılır. Daha iyisi olabilirdi ama bu fiyata bu kalite yeterli.',
        'Normal, idare eder. Beklediğim kadar iyi değildi ama kötü de değil. Gayet kullanılabilir.',
    ],
    3: [
        'Ortalama bir ürün. Ne çok iyi ne çok kötü. İhtiyacımı karşılıyor ama o kadar.',
        'Fena değil ama beklediğim gibi değildi. Daha iyi olabilirdi açıkçası.',
        'İdare eder. Fiyatı biraz pahalı olmuş gibi. Aynı paraya daha iyisi bulunur sanırım.',
        'Eh işte, normal. Özel bir özelliği yok. Sıradan bir ürün. Pişman olmadım ama çok da memnun sayılmam.',
        'Tam ortası işte. Kötü değil iyi de değil. Kullanıyorum ama bir daha alır mıyım emin değilim.',
    ],
    2: [
        'Pek beğenmedim. Kalitesi düşük, beklentimin altında kaldı. Tavsiye etmem.',
        'Maalesef memnun kalmadım. Ürün fotoğraflardaki gibi değil. Kalitesiz.',
        'Hayal kırıklığı. Bu fiyata daha iyisi bulunur. Para vermeye değmez.',
        'Kötü bir alışveriş oldu. Ürün vasat, kalitesi çok düşük. Pişmanım.',
        'Beklediğimden çok daha kötü çıktı. Birkaç kere kullandım ama beğenmedim. İade etmek istiyorum.',
        'Fiyatına göre bile kötü. Ucuz malzeme kullanılmış belli. Tavsiye etmiyorum.',
    ],
    1: [
        'Berbat! Kesinlikle almayın. Paranızı çöpe atmayın. Çok kötü kalite.',
        'Rezalet bir ürün. İlk kullanımda bozuldu. Müşteri hizmetleri de ilgilenmiyor. Çok kötü deneyim.',
        'Tam bir fiyasko. Bu kadar kötü olacağını düşünmemiştim. Kesinlikle tavsiye etmiyorum.',
        'Çok pişmanım. Param boşa gitti. Ürün tamamen çöp. Satıcı ile de iletişim kuramadım.',
        'Korkunç! Hiç kullanmadım bile, direkt iade ettim. Kalitesiz, ucuz malzeme. Berbat!',
        'Aldatmaca bir ürün. Görseller ile hiç alakası yok. Çok düşük kalite. Para iadesi istiyorum.',
        'Hayatımda aldığım en kötü ürün. Çalışmıyor bile. Satıcıdan dönüş yok. Çok kötü!',
    ]
}

reviews = []
review_count = 3000

cursor.execute('''
    SELECT DISTINCT oi.product_id, o.customer_id, o.order_date
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'teslim_edildi'
''')
reviewable_items = cursor.fetchall()

cursor.execute('SELECT product_id FROM products')
all_product_ids = [row[0] for row in cursor.fetchall()]

bad_products = set(random.sample(all_product_ids, int(len(all_product_ids) * 0.10)))
average_products = set(random.sample([p for p in all_product_ids if p not in bad_products], 
                                     int(len(all_product_ids) * 0.20)))

for _ in range(min(review_count, len(reviewable_items))):
    product_id, customer_id, order_date_str = random.choice(reviewable_items)
    
    if product_id in bad_products:
        rating = random.choices([1, 2, 3], weights=[50, 40, 10])[0]
    elif product_id in average_products:
        rating = random.choices([2, 3, 4], weights=[10, 50, 40])[0]
    else:
        rating = random.choices([3, 4, 5], weights=[10, 35, 55])[0]
    
    if random.random() > 0.15:
        review_text = random.choice(review_templates[rating])
    else:
        review_text = None
    
    order_date = datetime.strptime(order_date_str, '%Y-%m-%d %H:%M:%S')
    review_date = fake.date_time_between(
        start_date=order_date,
        end_date=datetime(2025, 10, 29)
    )
    
    reviews.append((product_id, customer_id, rating, review_text, review_date))

cursor.executemany('''
    INSERT INTO reviews (product_id, customer_id, rating, review_text, review_date)
    VALUES (?, ?, ?, ?, ?)
''', reviews)

print(f"[+] {len(reviews)} reviews inserted!")

cursor.execute('SELECT rating, COUNT(*) FROM reviews GROUP BY rating ORDER BY rating DESC')
print("\n[*] Rating Distribution:")
for rating, count in cursor.fetchall():
    print(f"   {rating} stars: {count} reviews ({count/len(reviews)*100:.1f}%)")

# ============================================
# STATISTICS
# ============================================

print("\n" + "="*50)
print("[*] DATABASE STATISTICS")
print("="*50)

tables = ['customers', 'categories', 'products', 'orders', 'order_items', 'reviews', 'campaigns']

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f"   {table.upper()}: {count:,} records")

cursor.execute('SELECT SUM(total_amount) FROM orders WHERE order_status = "teslim_edildi"')
total_sales = cursor.fetchone()[0]
print(f"\n[*] Total Sales (Delivered): {total_sales:,.2f} TL")

cursor.execute('SELECT MIN(order_date), MAX(order_date) FROM orders')
min_date, max_date = cursor.fetchone()
print(f"[*] Date Range: {min_date[:10]} - {max_date[:10]}")

cursor.execute('SELECT COUNT(*) FROM orders WHERE campaign_id IS NOT NULL')
campaign_orders = cursor.fetchone()[0]
print(f"[*] Orders with Campaign: {campaign_orders:,} ({campaign_orders/len(orders)*100:.1f}%)")

print("\n" + "="*50)

conn.commit()
conn.close()

print("\n[+] Database successfully created: data/ecommerce.db")
