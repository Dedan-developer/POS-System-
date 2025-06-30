def ensure_key(rows, key, default=0):
    for row in rows:
        if key not in row:
            row[key] = default
    return rows

def ensure_stock_key(rows):
    for row in rows:
        if 'stock' not in row:
            row['stock'] = 0
    return rows

def patch_all_products(cursor):
    # Set all products to have stock=100, price=50.0, category='Uncategorized' if missing or zero
    cursor.execute("UPDATE products SET stock=100 WHERE stock IS NULL OR stock=0")
    cursor.execute("UPDATE products SET price=50.0 WHERE price IS NULL OR price=0")
    cursor.execute("UPDATE products SET category='Uncategorized' WHERE category IS NULL OR category=''")

def ensure_image_path(rows, default_path=None):
    # Use product photo if available, otherwise fallback to logo
    fallback = default_path or 'uploads/devinova_logo.png'
    for row in rows:
        if 'image_path' not in row or not row['image_path']:
            row['image_path'] = fallback
        else:
            # If image_path is logo or not a real product image, try to fix
            if row['image_path'].endswith('devinova_logo.png') or row['image_path'] == 'uploads/devinova_logo.png':
                # Try to find a product image in static/images or static/uploads
                import os
                img_name = row.get('name', '').replace(' ', '_').lower() + '.jpg'
                img_path = os.path.join('uploads', img_name)
                if os.path.exists(os.path.join('static', img_path)):
                    row['image_path'] = img_path
    return rows
