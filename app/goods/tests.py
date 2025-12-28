# goods/tests.py
from django.test import TestCase
from goods.models import Products, Categories
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class CatalogViewTest(TestCase):

    def setUp(self):
        # Создаём пользователя и логиним
        self.user = User.objects.create(username="testuser")
        self.user.set_password("12345")
        self.user.save()
        self.client.force_login(self.user)

        # Создаём категорию
        self.category = Categories.objects.create(name="Мебель")

        # Создаём продукт
        self.product = Products.objects.create(
            name="Стул", category=self.category, price=1500
        )

    def test_catalog_page_status_code(self):
        response = self.client.get(reverse("catalog:category_all"))
        self.assertEqual(response.status_code, 200)


class ProductModelTest(TestCase):

    def test_create_product(self):
        category = Categories.objects.create(name="Мебель")

        product = Products.objects.create(name="Стул", category=category, price=1500)

        self.assertEqual(product.name, "Стул")
        self.assertEqual(product.category.name, "Мебель")
