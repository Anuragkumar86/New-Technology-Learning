# File: tests/test_products.py

def test_create_product_saves_to_test_db(client):
    # 1. Send POST request to create a product in shop_test_db (port 5433)
    response = client.post(
        "/create",
        json={
            "name": "Gaming Mouse",
            "category": "Accessories",
            "price": 50.0,
            "stock": 4,
            "tags": ["wireless", "rgb"],
        },
        headers={"X-API-Key": "anurag-secret-123"}
    )

    # 2. Check response status and returned JSON
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gaming Mouse"
    assert data["id"] == 1
    assert data["total_price"] == 200.0  # 50.0 * 4 computed field!


def test_get_single_product(client, sample_product):
    # 'sample_product' fixture already inserted "iPhone 16" into shop_test_db before this line ran!
    response = client.get(f"/products/{sample_product.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "iPhone 16"
    assert response.json()["tags"] == ["smartphone", "apple"]


def test_delete_product(client, sample_product):
    # 1. Delete the sample product
    delete_res = client.delete(f"/products/{sample_product.id}",headers={"X-API-Key": "anurag-secret-123"})
    assert delete_res.status_code == 204

    # 2. Confirm it is actually gone from shop_test_db!
    get_res = client.get(f"/products/{sample_product.id}")
    assert get_res.status_code == 404