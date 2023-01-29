from django.test import TestCase
from scripts import load_database
from CensusChoropleth.models import Geography, Characteristic, Datum
from CensusChoropleth.views import Map

class MapTests(TestCase):

    def test_de_pluaralize_geo_levels(self):
        self.assertEqual(Map.de_pluaralize_geo_levels("Census Divisions"), "Census division")
        self.assertEqual(Map.de_pluaralize_geo_levels("Census Subdivisions"), "Census subdivision")
        self.assertEqual(Map.de_pluaralize_geo_levels("Provinces and Territories"), "Provinces and Territories")