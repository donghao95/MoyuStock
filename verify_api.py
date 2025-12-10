import sys
import os

# Ensure we can import from core
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from core.api_client import BaiduApiClient

def main():
    client = BaiduApiClient()
    # Test valid and invalid codes
    test_codes = ["601888", "000001", "INVALID_CODE"]
    
    print("-" * 50)
    print("Starting Baidu API Verification")
    print("-" * 50)

    for code in test_codes:
        print(f"Testing code: {code} ...", end=" ")
        result = client.fetch_quote(code)
        
        if result.get("success"):
            data = result["data"]
            print("✅ SUCCESS")
            print(f"  Name: {data['name']}")
            print(f"  Price: {data['price']}")
            print(f"  Ratio: {data['ratio']}")
            print(f"  Time: {data['update_time']}")
        else:
            print("❌ FAILED")
            print(f"  Error: {result.get('error')}")
        print("-" * 30)

if __name__ == "__main__":
    main()
