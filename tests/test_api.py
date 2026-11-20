
import unittest

from app import app


class CloudOpsAPITests(unittest.TestCase):

    def setUp(self):
        """Create a Flask test client."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["application"], "CloudOps")
        self.assertEqual(data["status"], "running")

    def test_monitoring_api(self):
        response = self.client.get("/api/monitoring")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_alerts_api(self):
        response = self.client.get("/api/alerts")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_dashboard(self):
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"CloudOps Dashboard",
            response.data
        )


if __name__ == "__main__":
    unittest.main()
