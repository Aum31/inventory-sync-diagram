import csv
import os

# ==============================================================================
# ANTIGRAVITY LESSON 2: What is an ETL Pipeline?
# ETL stands for Extract, Transform, Load:
# 1. EXTRACT: Read raw data from a source (in this case, our manufacturer's CSV file).
# 2. TRANSFORM: Clean the data, validate it, and convert formats (e.g., ensuring numbers
#    are valid, rejecting products with negative prices, stripping whitespace).
# 3. LOAD: Write the cleaned data to the target database (e.g., Shopify API, SQL Database).
# ==============================================================================

CSV_FILE_PATH = "data/manufacturer_inventory.csv"

def extract_raw_data(file_path):
    """
    EXTRACT: Opens the CSV file and reads the rows into a list of Python dictionaries.
    """
    if not os.path.exists(file_path):
        print(f"[!] Error: Source file {file_path} not found.")
        return []
        
    raw_products = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        # csv.DictReader automatically maps the header row as keys for each row dictionary
        reader = csv.DictReader(f)
        for row in reader:
            raw_products.append(row)
            
    print(f"[+] Extract Phase: Successfully read {len(raw_products)} raw items from CSV.")
    return raw_products

def transform_and_validate(raw_products):
    """
    TRANSFORM: Validates product fields to ensure bad data is never sent to the store.
    """
    valid_products = []
    failed_products = []
    
    for item in raw_products:
        sku = item.get("SKU", "").strip()
        name = item.get("Product Name", "").strip()
        price_str = item.get("Price", "").strip()
        qty_str = item.get("Stock Quantity", "").strip()
        manufacturer = item.get("Manufacturer", "").strip()
        
        errors = []
        
        # Rule 1: SKU must not be empty
        if not sku:
            errors.append("Missing SKU identifier.")
            
        # Rule 2: Product Name must not be empty
        if not name:
            errors.append("Missing product title/name.")
            
        # Rule 3: Price must be a valid positive float number
        try:
            price = float(price_str)
            if price < 0:
                errors.append(f"Invalid negative price: ${price_str}")
        except ValueError:
            errors.append(f"Price is not a valid number: '{price_str}'")
            price = None
            
        # Rule 4: Stock Quantity must be a valid integer >= 0
        try:
            if not qty_str: # Handled empty cells
                errors.append("Stock quantity is blank.")
                qty = None
            else:
                qty = int(qty_str)
                if qty < 0:
                    errors.append(f"Invalid negative stock quantity: {qty_str}")
        except ValueError:
            errors.append(f"Stock quantity is not a valid integer: '{qty_str}'")
            qty = None
            
        # If any validation rules failed, separate this item
        if errors:
            failed_products.append({
                "SKU": sku if sku else "UNKNOWN",
                "Name": name if name else "UNKNOWN",
                "Errors": errors
            })
        else:
            valid_products.append({
                "sku": sku,
                "name": name,
                "price": price,
                "qty": qty,
                "manufacturer": manufacturer
            })
            
    print(f"[+] Transform Phase: Checked all items. {len(valid_products)} passed, {len(failed_products)} failed validation.")
    return valid_products, failed_products

def load_to_store(valid_products):
    """
    LOAD: Simulates uploading the cleaned inventory to the target e-commerce store API.
    """
    print("\n[+] Load Phase: Syncing to storefront API...")
    for product in valid_products:
        # In a real pipeline, this would be a requests.post() call to Shopify's REST/GraphQL API
        print(f"    --> UPDATED STOREFRONT | SKU: {product['sku']} | Name: {product['name']} | Price: ${product['price']:.2f} | Stock: {product['qty']} units")
        
    print(f"[SUCCESS] Load Phase Complete. Synced {len(valid_products)} products successfully.")

def main():
    print("=========================================================")
    print("         ANTIGRAVITY MOCK INVENTORY SYNC PIPELINE        ")
    print("=========================================================\n")
    
    # 1. EXTRACT
    raw_data = extract_raw_data(CSV_FILE_PATH)
    if not raw_data:
        return
        
    # 2. TRANSFORM
    valid_data, failed_data = transform_and_validate(raw_data)
    
    # Report errors to the user (so the distributor knows which items are broken in their supplier's list)
    if failed_data:
        print("\n[!] WARNING: Validation Errors Found in Supplier's File:")
        for fail in failed_data:
            print(f"    - SKU: {fail['SKU']} | Name: {fail['Name']}")
            for err in fail["Errors"]:
                print(f"      * {err}")
                
    # 3. LOAD
    if valid_data:
        load_to_store(valid_data)
    else:
        print("\n[!] Load Phase skipped: No valid products to sync.")

if __name__ == "__main__":
    main()
