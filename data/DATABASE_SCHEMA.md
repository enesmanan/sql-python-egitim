# E-Commerce Database Schema

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          E-COMMERCE DATABASE SCHEMA                             │
└─────────────────────────────────────────────────────────────────────────────────┘


                    ┌─────────────────────────────────┐
                    │        CATEGORIES               │
                    │─────────────────────────────────│
                    │ • category_id (PK)              │
                    │ • category_name                 │
                    │ • parent_category_id (FK)  ──┐  │
                    └─────────────────────────────┘  │
                             ▲                       │ SELF-REFERENCE
                             │ 1:N                   │ (Hierarchical)
                             │                       └──────────────┘
                             │
                             │
                    ┌─────────────────────────────────┐
                    │         PRODUCTS                │
                    │─────────────────────────────────│
                    │ • product_id (PK)               │
                    │ • product_name                  │
                    │ • category_id (FK)              │
                    │ • brand                         │
                    │ • price                         │
                    │ • stock_quantity                │
                    │ • created_date                  │
                    └─────────────────────────────────┘
                             ▲
                             │
                ┌────────────┼────────────┐
                │ 1:N        │ 1:N        │
                │            │            │
    ┌───────────────────┐   │   ┌───────────────────┐
    │   ORDER_ITEMS     │   │   │     REVIEWS       │
    │───────────────────│   │   │───────────────────│
    │ • item_id (PK)    │   │   │ • review_id (PK)  │
    │ • order_id (FK)   │   │   │ • product_id (FK) │
    │ • product_id (FK) │───┘   │ • customer_id (FK)│
    │ • quantity        │       │ • rating (1-5)    │
    │ • unit_price      │       │ • review_text     │
    │ • discount_rate   │       │ • review_date     │
    └───────────────────┘       └───────────────────┘
             ▲                           ▲
             │ N:1                       │ N:1
             │                           │
    ┌─────────────────────────────────────────────┐
    │              ORDERS                         │
    │─────────────────────────────────────────────│
    │ • order_id (PK)                             │
    │ • customer_id (FK)  ────────────────────────┼─────┐
    │ • campaign_id (FK)  ────────────────────────┼──┐  │
    │ • order_date                                │  │  │
    │ • order_status                              │  │  │
    │ • total_amount                              │  │  │
    │ • payment_method                            │  │  │
    │ • shipping_cost                             │  │  │
    └─────────────────────────────────────────────┘  │  │
                                                     │  │
         ┌───────────────────────────────────────────┘  │
         │ N:1                                          │
         │                                              │
    ┌───────────────────┐                              │
    │    CAMPAIGNS      │                              │
    │───────────────────│                              │
    │ • campaign_id (PK)│                              │
    │ • campaign_name   │                              │
    │ • discount_rate   │                              │
    │ • start_date      │                              │
    │ • end_date        │                              │
    │ • min_basket_amt  │                              │
    └───────────────────┘                              │
                                                       │ N:1
                                                       │
                                    ┌──────────────────────────┐
                                    │       CUSTOMERS          │
                                    │──────────────────────────│
                                    │ • customer_id (PK)       │
                                    │ • first_name             │
                                    │ • last_name              │
                                    │ • email (UNIQUE)         │
                                    │ • phone                  │
                                    │ • birth_date             │
                                    │ • gender                 │
                                    │ • registration_date      │
                                    │ • city                   │
                                    │ • customer_segment       │
                                    └──────────────────────────┘
```

---

## Veritabanı İlişkileri Tablosu

| # | Kaynak Tablo | Kaynak Kolon | İlişki | Hedef Tablo | Hedef Kolon | Açıklama |
|---|-------------|---------------|--------|------------|---------------|----------|
| 1 | `categories` | `parent_category_id` | **→** (FK) | `categories` | `category_id` | Hiyerarşik kategori yapısı için kendine referans (Ana Kategori → Alt Kategori) |
| 2 | `products` | `category_id` | **→** (FK) | `categories` | `category_id` | Her ürünü kategorisine bağlar |
| 3 | `orders` | `customer_id` | **→** (FK) | `customers` | `customer_id` | Her siparişi veren müşteriye bağlar |
| 4 | `orders` | `campaign_id` | **→** (FK) | `campaigns` | `campaign_id` | Promosyon kampanyasına opsiyonel bağlantı (NULL olabilir) |
| 5 | `order_items` | `order_id` | **→** (FK) | `orders` | `order_id` | Sipariş kalemlerini ana siparişe bağlar |
| 6 | `order_items` | `product_id` | **→** (FK) | `products` | `product_id` | Sipariş kalemlerini satın alınan ürünlere bağlar |
| 7 | `reviews` | `product_id` | **→** (FK) | `products` | `product_id` | Yorumları değerlendirilen ürünlere bağlar |
| 8 | `reviews` | `customer_id` | **→** (FK) | `customers` | `customer_id` | Yorumları yazan müşterilere bağlar |

---

## Tablo Şemaları

### 1. CATEGORIES (Kategoriler)
Ürün kategorilerini hiyerarşik yapıda saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `category_id` | INTEGER | PRIMARY KEY | Benzersiz kategori tanımlayıcısı |
| `category_name` | TEXT | NOT NULL | Kategorinin adı (Türkçe) |
| `parent_category_id` | INTEGER | FOREIGN KEY → categories(category_id) | Üst kategoriye referans (ana kategoriler için NULL) |


---

### 2. PRODUCTS (Ürünler)
Tüm ürün bilgilerini saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `product_id` | INTEGER | PRIMARY KEY | Benzersiz ürün tanımlayıcısı |
| `product_name` | TEXT | NOT NULL | Ürün adı (Marka + Tip) |
| `category_id` | INTEGER | FOREIGN KEY → categories(category_id) | Ürün kategorisine bağlantı |
| `brand` | TEXT | - | Marka adı (Apple, Samsung, vb.) |
| `price` | REAL | NOT NULL | Ürün fiyatı (TL) |
| `stock_quantity` | INTEGER | NOT NULL | Mevcut stok miktarı |
| `created_date` | DATE | NOT NULL | Ürünün sisteme eklenme tarihi |


---

### 3. CUSTOMERS (Müşteriler)
Müşteri bilgilerini ve segmentasyonunu saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `customer_id` | INTEGER | PRIMARY KEY | Benzersiz müşteri tanımlayıcısı |
| `first_name` | TEXT | NOT NULL | Müşterinin adı (Türkçe) |
| `last_name` | TEXT | NOT NULL | Müşterinin soyadı (Türkçe) |
| `email` | TEXT | UNIQUE, NOT NULL | E-posta adresi (@gmail.com) |
| `phone` | TEXT | - | Telefon numarası (format: +90...) |
| `birth_date` | DATE | - | Doğum tarihi |
| `gender` | TEXT | - | Cinsiyet: erkek, kadin, belirtmek_istemiyorum |
| `registration_date` | DATE | NOT NULL | Hesap oluşturma tarihi |
| `city` | TEXT | - | Şehir adı (Türk şehirleri) |
| `customer_segment` | TEXT | - | Segment: platinum, gold, silver, bronze |


---

### 4. CAMPAIGNS (Kampanyalar)
İndirim bilgileriyle promosyon kampanyalarını saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `campaign_id` | INTEGER | PRIMARY KEY | Benzersiz kampanya tanımlayıcısı |
| `campaign_name` | TEXT | NOT NULL | Kampanya adı (Türkçe) |
| `discount_rate` | REAL | NOT NULL | İndirim yüzdesi (0-100) |
| `start_date` | DATE | NOT NULL | Kampanya başlangıç tarihi |
| `end_date` | DATE | NOT NULL | Kampanya bitiş tarihi |
| `min_basket_amount` | REAL | - | Kampanyadan yararlanmak için minimum sepet tutarı (NULL olabilir) |

---

### 5. ORDERS (Siparişler)
Sipariş bilgilerini ve durumunu saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `order_id` | INTEGER | PRIMARY KEY | Benzersiz sipariş tanımlayıcısı |
| `customer_id` | INTEGER | FOREIGN KEY → customers(customer_id) | Siparişi veren müşteri |
| `campaign_id` | INTEGER | FOREIGN KEY → campaigns(campaign_id) | Uygulanan kampanya (yoksa NULL) |
| `order_date` | DATETIME | NOT NULL | Sipariş tarihi ve saati |
| `order_status` | TEXT | NOT NULL | Durum: teslim_edildi, kargoda, hazirlaniyor, iptal |
| `total_amount` | REAL | NOT NULL | Toplam sipariş tutarı (TL, indirimler sonrası) |
| `payment_method` | TEXT | NOT NULL | Ödeme yöntemi: kredi_karti, havale, kapida_odeme |
| `shipping_cost` | REAL | NOT NULL | Kargo ücreti (ücretsizse 0) |


---

### 6. ORDER_ITEMS (Sipariş Kalemleri)
Her sipariş içindeki bireysel ürünleri saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `item_id` | INTEGER | PRIMARY KEY | Benzersiz sipariş kalemi tanımlayıcısı |
| `order_id` | INTEGER | FOREIGN KEY → orders(order_id) | Ana sipariş |
| `product_id` | INTEGER | FOREIGN KEY → products(product_id) | Satın alınan ürün |
| `quantity` | INTEGER | NOT NULL | Ürün adedi |
| `unit_price` | REAL | NOT NULL | Sipariş anındaki birim fiyat |
| `discount_rate` | REAL | DEFAULT 0 | Ürün seviyesinde indirim yüzdesi |


---

### 7. REVIEWS (Yorumlar)
Müşteri ürün yorumlarını ve değerlendirmelerini saklar.

| Kolon Adı | Veri Tipi | Kısıtlamalar | Açıklama |
|-----------|-----------|-------------|----------|
| `review_id` | INTEGER | PRIMARY KEY | Benzersiz yorum tanımlayıcısı |
| `product_id` | INTEGER | FOREIGN KEY → products(product_id) | Değerlendirilen ürün |
| `customer_id` | INTEGER | FOREIGN KEY → customers(customer_id) | Yorumu yazan müşteri |
| `rating` | INTEGER | NOT NULL, CHECK(1-5) | Yıldız puanı (1-5) |
| `review_text` | TEXT | - | Yorum metni (NULL olabilir) |
| `review_date` | DATETIME | NOT NULL | Yorum tarihi ve saati |

---

## Kardinalite İlişkileri

| İlişki Tipi | Kaynak → Hedef | Açıklama |
|-------------|---------------|----------|
| **1:1** (Bire-Bir) | Bu şemada kullanılmıyor | Her kayıt tam olarak bir diğer kayıtla ilişkili |
| **1:N** (Bire-Çok) | Çoğu ilişki | Bir ana kayıt birçok alt kayda sahip olabilir |
| **N:1** (Çoka-Bir) | 1:N'in tersi | Birçok alt kayıt bir ana kayıtla ilişkili |
| **N:M** (Çoka-Çok) | Doğrudan kullanılmıyor | Gerekirse ara tablolarla uygulanır |

### Detaylı Kardinaliteler:

1. **CATEGORIES → CATEGORIES** (1:N - Kendine Referans)
   - Bir ana kategori birçok alt kategoriye sahip olabilir
   - Her alt kategorinin tam olarak bir ana kategorisi var (veya yoksa ana kategoridir)

2. **CATEGORIES → PRODUCTS** (1:N)
   - Bir kategori birçok ürün içerebilir
   - Her ürün tam olarak bir kategoriye aittir

3. **CUSTOMERS → ORDERS** (1:N)
   - Bir müşteri birçok sipariş verebilir
   - Her sipariş tam olarak bir müşteriye aittir

4. **CUSTOMERS → REVIEWS** (1:N)
   - Bir müşteri birçok yorum yazabilir
   - Her yorum tam olarak bir müşteri tarafından yazılır

5. **CAMPAIGNS → ORDERS** (1:N - Opsiyonel)
   - Bir kampanya birçok siparişte uygulanabilir
   - Her sipariş sıfır veya bir kampanyaya sahip olabilir

6. **ORDERS → ORDER_ITEMS** (1:N)
   - Bir sipariş bir veya daha fazla sipariş kalemi içerir
   - Her sipariş kalemi tam olarak bir siparişe aittir

7. **PRODUCTS → ORDER_ITEMS** (1:N)
   - Bir ürün birçok sipariş kaleminde görünebilir
   - Her sipariş kalemi tam olarak bir ürüne referans verir

8. **PRODUCTS → REVIEWS** (1:N)
   - Bir ürün birçok yoruma sahip olabilir
   - Her yorum tam olarak bir ürün hakkındadır

---


