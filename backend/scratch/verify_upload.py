import requests

def test_upload():
    login_url = "http://localhost:8000/api/v1/auth/login"
    try:
        # 1. Login to get token
        r = requests.post(login_url, json={"email": "admin@buildwise.ai", "password": "Admin@123"})
        if r.status_code != 200:
            print("Login failed:", r.status_code, r.text)
            return
        
        token = r.json().get("access_token")
        print("Logged in successfully. Token obtained.")

        # 2. Perform upload
        upload_url = "http://localhost:8000/api/v1/knowledge/upload"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        files = {
            "file": ("test_doc.txt", "This is some test content for the knowledge base about AC leak repair procedures.", "text/plain")
        }
        data = {
            "title": "AC Leak Repair Procedure",
            "description": "Step-by-step instructions on repairing AC unit water leakage.",
            "document_type": "manual"
        }
        
        r2 = requests.post(upload_url, headers=headers, files=files, data=data)
        print("Upload Response status:", r2.status_code)
        print("Upload Response body:", r2.text)
    except Exception as e:
        print("Error connecting to server:", e)

if __name__ == "__main__":
    test_upload()
