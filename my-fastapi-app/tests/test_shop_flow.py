# File: tests/test_shop_flow.py

def test_full_product_lifecycle(client):
    # --- STEP 1: CREATE (POST /create) ---
    create_payload = {
        "name": "Sony WH-1000XM5",
        "category": "Electronics",
        "price": 350.0,
        "in_stock": True,
        "stock": 4,
        "rating": 4.9,
        "tags": ["audio", "wireless"],
    }
    create_res = client.post("/create", json=create_payload, headers={"X-API-Key": "anurag-secret-123"})

    assert create_res.status_code == 201
    created_product = create_res.json()
    product_id = created_product["id"]  # Grab the PostgreSQL-generated ID (e.g., 1)

    assert created_product["name"] == "Sony WH-1000XM5"
    assert created_product["total_price"] == 1400.0  # 350.0 * 4 computed field

    # --- STEP 2: READ (GET /products/{product_id}) ---
    get_res = client.get(f"/products/{product_id}")

    assert get_res.status_code == 200
    assert get_res.json()["id"] == product_id
    assert get_res.json()["tags"] == ["audio", "wireless"]

    # --- STEP 3: PARTIAL UPDATE (PATCH /products/{product_id}) ---
    # Only sending 'price' and 'stock' to verify exclude_unset=True works!
    patch_res = client.patch(
        f"/products/{product_id}",
        json={"price": 300.0, "stock": 2},
        
    )

    assert patch_res.status_code == 200
    updated_product = patch_res.json()
    assert updated_product["price"] == 300.0
    assert updated_product["stock"] == 2
    assert updated_product["total_price"] == 600.0     # Recomputed: 300.0 * 2
    assert updated_product["name"] == "Sony WH-1000XM5"  # Unchanged field preserved!

    # --- STEP 4: DELETE (DELETE /products/{product_id}) ---
    delete_res = client.delete(f"/products/{product_id}", headers={"X-API-Key": "anurag-secret-123"})
    assert delete_res.status_code == 204

    # --- STEP 5: CONFIRM DELETED (GET /products/{product_id} -> 404) ---
    confirm_res = client.get(f"/products/{product_id}")
    assert confirm_res.status_code == 404
    assert confirm_res.json()["detail"] == "Product not found"