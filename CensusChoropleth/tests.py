from django.test import TestCase
from scripts import load_database
from CensusChoropleth.models import Geography, Characteristic, Datum

class LoadDatabaseTests(TestCase):
    COL_NAMES = ['CENSUS_YEAR', 'DGUID', 'ALT_GEO_CODE', 'GEO_LEVEL', 'GEO_NAME', 'TNR_SF', 'TNR_LF', 'DATA_QUALITY_FLAG', 'CHARACTERISTIC_ID', 'CHARACTERISTIC_NAME', 'CHARACTERISTIC_NOTE', 'C1_COUNT_TOTAL', 'SYMBOL', 'C2_COUNT_MEN+', 'SYMBOL.1', 'C3_COUNT_WOMEN+', 'SYMBOL.2', 'C10_RATE_TOTAL', 'SYMBOL.3', 'C11_RATE_MEN+', 'SYMBOL.4', 'C12_RATE_WOMEN+', 
'SYMBOL.5']


    def test_correct_df(self):
        """Checks dataframe has been made correctly by checking column names
        """
        df = load_database.load_parquet()
        for i in range(len(df.columns.values)):
            self.assertEqual(df.columns.values[i], self.COL_NAMES[i])

