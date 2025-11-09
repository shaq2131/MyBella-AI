from backend import create_app
import traceback

try:
    app, _ = create_app()

    if __name__ == "__main__":
        client = app.test_client()
        response = client.get("/")
        print("Status:", response.status_code)
        print("Data snippet:")
        print(response.data[:500])
        if response.status_code != 200:
            print("Full response:")
            print(response.data.decode())
except Exception as e:
    print("Error during app creation or request:")
    print(traceback.format_exc())
