BAKERY_MENU = {
    "big_loaf": {"name": "Big Loaf of Bread", "price": 4800},
    "small_loaf": {"name": "Small Loaf of Bread", "price": 2500},
    "tiny_loaf": {"name": "Tiny Loaf of Bread", "price": 1000},
    "buns_standard": {"name": "Standard Buns (Pack)", "price": 2500},
    "buns_small": {"name": "Small Buns (Pack)", "price": 2200},
    "cutrolls": {"name": "Fresh Cutrolls", "price": 2500},
    "sweetrolls": {"name": "Sweetrolls", "price": 2500},
    "mandazi": {"name": "Fresh Mandazi (Pack)", "price": 2500},
}

# Simulated volatile order database for our Admin panel session trackers
ORDER_DATABASE = []

def process_combined_order(form_data):
    """
    Calculates dynamic concurrent high-volume quantities across all menu configurations.
    """
    grand_total = 0
    items_ordered = []
    order_style = form_data.get('order_style', 'retail')

    # 1. Parse Loop across all Standard Items simultaneously
    for key, info in BAKERY_MENU.items():
        qty_input = form_data.get(f"qty_{key}")
        qty = int(qty_input) if qty_input and qty_input.strip() != "" else 0
        
        if qty > 0:
            # Override unit tariff for bulk wholesale school operations on buns
            if key == "buns_standard" and order_style == "school":
                unit_p = 2200
                name = "Custom School Buns (Wholesale Pack)"
            else:
                unit_p = info["price"]
                name = info["name"]
                
            item_cost = unit_p * qty
            grand_total += item_cost
            items_ordered.append({
                "name": f"{name} x{qty}",
                "cost": item_cost
            })

    # 2. Parse Custom Celebration Cakes Section
    cake_qty_input = form_data.get('cake_quantity')
    cake_qty = int(cake_qty_input) if cake_qty_input and cake_qty_input.strip() != "" else 0
    
    if cake_qty > 0:
        size = form_data.get('size')
        flavor = form_data.get('flavor')
        layers = int(form_data.get('layers') or 1)
        msg = form_data.get('message', '').strip()

        if size == "Small": base_p = 35000
        elif size == "Medium": base_p = 55000
        else: base_p = 85000

        if layers > 1: base_p += (layers - 1) * 15000
        if flavor in ["Red Velvet", "Black Forest"]: base_p += 10000
        if msg: base_p += 5000

        cake_cost = base_p * cake_qty
        grand_total += cake_cost
        items_ordered.append({
            "name": f"Custom Cake ({size}, {flavor}, {layers} Tier/s) x{cake_qty}",
            "cost": cake_cost
        })

    return {
        "items": items_ordered,
        "grand_total": grand_total,
        "needed_by": form_data.get('delivery_date', 'Immediate Pickup')
    }
