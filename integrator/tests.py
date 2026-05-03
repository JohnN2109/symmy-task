from django.test import TestCase
from integrator.tasks import transform_product
from unittest.mock import patch
from integrator.tasks import send_to_eshop

class TransformProductTest(TestCase):

    def test_transform_product(self):
        item = {
            "id": "SKU-001",
            "title": "Test",
            "price_vat_excl": 100,
            "stocks": {
                "a": 5,
                "b": 3
            },
            "attributes": {}
        }

        result = transform_product(item)

        self.assertEqual(result["sku"], "SKU-001")
        self.assertEqual(result["price"], 121.0)
        self.assertEqual(result["stock"], 8)
        self.assertEqual(result["color"], "N/A")



class ApiTest(TestCase):

    @patch("integrator.tasks.requests.post")
    def test_send_to_eshop(self, mock_post):

        mock_post.return_value.status_code = 200

        product = {
            "sku": "SKU-001"
        }

        response = send_to_eshop(product)

        self.assertEqual(response.status_code, 200)