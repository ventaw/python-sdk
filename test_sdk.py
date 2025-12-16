
import sys
import os
import time

# Add sdk/python to path for testing without install
sys.path.append(os.path.join(os.getcwd(), "sdk/python"))

import ventaw

def test_sdk():
    # Load API Key
    try:
        with open("/tmp/api_key.txt", "r") as f:
            api_key = f.read().strip()
    except:
        print("API key file not found at /tmp/api_key.txt")
        return

    # 1. Configure SDK
    ventaw.api_key = api_key
    ventaw.api_base = "http://localhost:8000/v1"
    
    print("--- 1. Testing Templates ---")
    templates = ventaw.Template.list()
    print(f"Found {len(templates)} templates.")
    for t in templates:
        print(f" - {t.name} ({t.code})")

    # 2. Create Sandbox
    print("\n--- 2. Creating Sandbox ---")
    sb_name = f"sdk-test-{int(time.time())}"
    try:
        sandbox = ventaw.Sandbox.create(template="nextjs", name=sb_name)
        print(f"Created Sandbox: {sandbox.id} ({sandbox.state})")
    except Exception as e:
        print(f"Creation failed: {e}")
        return

    # 3. Wait for Running
    print("\n--- 3. Waiting for Startup ---")
    retries = 30
    while sandbox.state != "running" and retries > 0:
        time.sleep(1)
        sandbox.refresh()
        print(f"State: {sandbox.state}")
        retries -= 1
    
    if sandbox.state != "running":
        print("Sandbox failed to start.")
        sandbox.delete()
        return

    print(f"Sandbox Running! URL: {sandbox.access_url}")

    # 4. File I/O
    print("\n--- 4. Testing File I/O via SDK ---")
    try:
        # Create Dir (Retry to allow agent boot)
        print("Creating dir /tmp/sdk_test")
        agent_retries = 10
        while agent_retries > 0:
            try:
                sandbox.files.create_dir("/tmp/sdk_test")
                break
            except Exception as e:
                print(f"Waiting for agent... ({e})")
                time.sleep(2)
                agent_retries -= 1
        
        if agent_retries == 0:
            raise Exception("Agent timed out")
        
        # Write
        print("Writing file /tmp/sdk_test/hello.txt")
        written = sandbox.files.write("/tmp/sdk_test/hello.txt", "Hello from SDK")
        print(f"Bytes written: {written}")
        
        # Read
        print("Reading file")
        content = sandbox.files.read("/tmp/sdk_test/hello.txt")
        print(f"Content: '{content}'")
        assert content == "Hello from SDK"
        
        # List
        print("Listing /tmp/sdk_test")
        files = sandbox.files.list("/tmp/sdk_test")
        print(f"Files found: {len(files)}")
        
        # Delete File
        print("Deleting file")
        sandbox.files.delete("/tmp/sdk_test/hello.txt")
        
        # Delete Dir
        print("Deleting dir")
        sandbox.files.delete_dir("/tmp/sdk_test")
        print("File I/O Tests Passed ✅")
        
    except Exception as e:
        print(f"File I/O Failed ❌: {e}")

    # 5. Cleanup
    print("\n--- 5. Deleting Sandbox ---")
    try:
        sandbox.delete()
        print("Sandbox deleted.")
    except Exception as e:
        print(f"Delete failed: {e}")

if __name__ == "__main__":
    test_sdk()
