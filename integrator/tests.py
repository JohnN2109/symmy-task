import responses

from django.test import TestCase

from integrator.tasks import send_product


class ApiTest(TestCase):

    @responses.activate
    def test_send_product(self):

        responses.add(
            responses.POST,
            "https://api.fake-eshop.cz/v1/products/",
            json={"success": True},
            status=201
        )

        product = {
            "sku": "SKU-001"
        }

        response = send_product(product)

        self.assertEqual(response.status_code, 201)