import unittest
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from server.app import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_status_endpoint(self):
        """Test if the system status endpoint works."""
        print("\nTesting /api/status...")
        response = self.app.get('/api/status')
        data = json.loads(response.data)
        print(f"Status Response: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'online')
        self.assertIn('system_stats', data)

    def test_chat_endpoint_simulation(self):
        """
        Test the chat endpoint. 
        Note: We mock the LLM response to avoid loading the heavy model during this quick test,
        or we assume the model handles it if loaded. 
        For this unit test, we'll let it run (it might be slow if it loads the model).
        """
        print("\nTesting /api/chat...")
        payload = {"text": "Open Notepad"}
        
        # We assume the server is running on the host where LLM is available.
        # If this hangs, it's because it's loading the 3GB model.
        # For a true unit test, we should mock 'brain.chat', but for an integration test, this is good.
        try:
            response = self.app.post('/api/chat', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
            
            data = json.loads(response.data)
            print(f"Chat Response: {data}")
            self.assertEqual(response.status_code, 200)
            # Check if it recognized the command intent (even if LLM varies)
            # The LLM prompt says to include [OPEN: ...]
            self.assertTrue("original_response" in data)
        except Exception as e:
            self.fail(f"Chat endpoint failed: {e}")

if __name__ == '__main__':
    unittest.main()
