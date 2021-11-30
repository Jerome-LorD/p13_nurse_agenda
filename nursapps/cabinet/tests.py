"""Test cabinet module."""
from django.test import TestCase
from nursapps.cabinet.forms import (
    CreateCabinet,
    SearchForCabinet,
    AssociationValidation,
)


class TestCabinet(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_cabinet(self):
        form = CreateCabinet()
        self.assertIn('placeholder="Votre nouveau cabinet"', form.as_ul())

    def test_search_for_cabinet(self):
        form = SearchForCabinet()
        self.assertIn('placeholder="nom du cabinet"', form.as_ul())

    def test_association_validation(self):
        form = AssociationValidation()
        self.assertIn('class="form-control me-2"', form.as_ul())
