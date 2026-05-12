import sqlite3

def run():
    conn = sqlite3.connect('db/medierp_v2.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all inventory items
    inventory = cursor.execute("SELECT * FROM inventory").fetchall()
    
    # Group by name
    items_by_name = {}
    for item in inventory:
        name = item['name'].strip().lower()
        if name not in items_by_name:
            items_by_name[name] = []
        items_by_name[name].append(dict(item))
        
    for name, items in items_by_name.items():
        if len(items) > 1:
            print(f"Found {len(items)} duplicates for '{name}'. Cleaning up...")
            # Keep the first one, sum quantities
            first_item = items[0]
            total_qty = sum([i['quantity'] for i in items])
            max_threshold = max([i['min_threshold'] for i in items])
            
            # Update the first item
            cursor.execute("UPDATE inventory SET quantity = ?, min_threshold = ? WHERE id = ?",
                           (total_qty, max_threshold, first_item['id']))
            
            # Delete the rest
            ids_to_delete = [i['id'] for i in items[1:]]
            placeholders = ','.join(['?'] * len(ids_to_delete))
            cursor.execute(f"DELETE FROM inventory WHERE id IN ({placeholders})", ids_to_delete)
            
    conn.commit()
    print("Cleanup complete.")

if __name__ == "__main__":
    run()
