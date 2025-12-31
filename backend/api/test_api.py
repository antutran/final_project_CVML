"""
Simple test script to verify API endpoints work correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_create_session():
    """Test session creation."""
    response = requests.post(f"{BASE_URL}/api/session/create")
    print(f"\nCreate session: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    return data.get("session_id") if response.status_code == 200 else None


def test_list_kols():
    """Test KOL listing."""
    response = requests.get(f"{BASE_URL}/api/kol/list")
    print(f"\nList KOLs: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} KOLs")
    if data:
        print(f"First KOL: {data[0]}")
    return data


def test_set_gender(session_id):
    """Test setting gender."""
    response = requests.post(
        f"{BASE_URL}/api/session/{session_id}/gender",
        json={"gender": "female"}
    )
    print(f"\nSet gender: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_select_kol(session_id, kol_id):
    """Test KOL selection."""
    response = requests.post(
        f"{BASE_URL}/api/session/{session_id}/kol",
        json={"kol_id": kol_id}
    )
    print(f"\nSelect KOL: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_get_state(session_id):
    """Test getting session state."""
    response = requests.get(f"{BASE_URL}/api/session/{session_id}/state")
    print(f"\nGet state: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def main():
    """Run basic tests."""
    print("=" * 60)
    print("Testing AI Fashion Recommendation API")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed!")
        return
    
    # Test session creation
    session_id = test_create_session()
    if not session_id:
        print("\n❌ Session creation failed!")
        return
    
    print(f"\n✅ Session created: {session_id}")
    
    # Test KOL listing
    kols = test_list_kols()
    if not kols:
        print("\n❌ No KOLs found!")
        return
    
    # Test setting gender
    if not test_set_gender(session_id):
        print("\n❌ Setting gender failed!")
        return
    
    # Test selecting KOL
    first_kol_id = kols[0]["id"]
    if not test_select_kol(session_id, first_kol_id):
        print("\n❌ Selecting KOL failed!")
        return
    
    # Test getting state
    if not test_get_state(session_id):
        print("\n❌ Getting state failed!")
        return
    
    print("\n" + "=" * 60)
    print("✅ All basic tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
