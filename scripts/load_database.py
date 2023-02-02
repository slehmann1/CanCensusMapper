import os
import shutil
import urllib.request
import zipfile
import pandas as pd
from CensusChoropleth.models import Geography, Characteristic, Datum, GeoLevel
import psutil
import geopandas as gpd

_FILENAME = "2021CensusData"
_CEN_URL = "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=005"
_FILENAME_KEEP = "98-401-X2021005_English_CSV_data.csv"
_TEMP_LOC = '\\temp'
_ZIP_FILENAME = "download.zip"
_MAX_MEM_CONSUMPTION = 90
_MAX_BULK_CREATES = 300000
_GEO_LEVELS = ['Country', 'Province', 'Census division',
               'Census subdivision', 'Territory']
_GEO_DATA_LOC = ["mapData/Census Sub Divisions/lcsd000b21a_e.shp",
                 "mapData/Provinces/lpr_000b21a_e.shp", "mapData/Census Divisions/lcd_000b21a_e.shp"]
_GEO_DATA_COLS = ["DGUID", "geometry"]


def run():
    if not Geography.objects.all().exists():
        print("Database empty, building database")
        build_database()
    else:
        print("Database already populated, no need to build database")


def build_database():
    if not os.path.isfile(_FILENAME+".parquet"):
        # Download CSV
        print("Downloading dta")
        download_csv(_CEN_URL, _FILENAME_KEEP, _FILENAME+".csv", False)
        print("Finished download of census data")
        data = save_csv_parquet()

    else:
        print("Files already downloaded. No need to download files")
        data = load_parquet()

    print("Dataframe loaded")
    print("DF columns:")
    print(data.columns.values)

    build_databases(data)


def download_csv(url, keep_file, filename, remove_first_line=False):
    """
    Downloads a CSV file from statistics canada
    :param url: The URL of the csv file to download
    :param keep_file: The file that should be kept from the zip file
    :param filename: The final filename that the csv should be saved as
    :param remove_first_line: Should the first line of the CSV be removed? Some CSVs have an additional header text
    :return: None
    """
    # Create a temporary directory
    loc = os.getcwd() + _TEMP_LOC + "\\"
    os.mkdir(loc)

    # Download the file as a zip file and extract it
    print(f"Start file download at this URL: {url}")
    urllib.request.urlretrieve(url, loc + _ZIP_FILENAME)
    print("Download complete")
    with zipfile.ZipFile(loc + _ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(loc)

    # Rename/move the file of interest and delete the temporary directory
    os.rename(loc + keep_file, os.getcwd() + "\\" + filename)
    shutil.rmtree(loc)

    # Sometimes the first line has to be removed due to additional header text
    if remove_first_line:
        with open(filename, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(filename, 'w') as fout:
            fout.writelines(data[1:])


def save_csv_parquet(filename=_FILENAME):
    """
    Loading CSVs are timeconsuming. Read in the CSV and save it as a parquet file which will be quicker to load in the future
    :return: The CSV as a dataframe
    """
    df = pd.read_csv(filename+".csv", encoding="latin-1", dtype="str")
    df.to_parquet(filename+".parquet", compression=None)
    del_csv(filename+".csv")
    return df


def load_parquet(filename=_FILENAME):
    """Loads a parquet representing the census

    Returns:
        Dataframe: The parquet loaded as a dataframe
    """
    df = pd.read_parquet(filename+".parquet")
    print("Parquet loaded")
    return df


def del_csv(filename):
    """Deletes the CSV at the filename

    Args:
        filename (String): The name of the csv file to be deleted
    """
    os.remove(os.getcwd() + "\\" + filename)


def add_geography(suppress_prints=False):

    geos = {geo.dguid: geo for geo in Geography.objects.all()}

    cad = gpd.GeoDataFrame(columns=_GEO_DATA_COLS)

    for i, datum_loc in enumerate(_GEO_DATA_LOC):
        x = gpd.read_file(datum_loc)
        print(f"CRS: {x.crs}")
        cad = gpd.GeoDataFrame(pd.concat([cad, x], ignore_index=True))
        print(
            f"Loaded geography data {i} of {len(_GEO_DATA_LOC)}, length is {len(x)}")

    length = len(cad)
    cad.set_crs(crs=3347, allow_override=True)

    # Set coordinate system properly
    cad = cad.to_crs(4326)

    print(f"All geography data loaded, length is {length}")

    print(f"CRS: {cad.crs}")

    for i in range(len(cad)):
        try:
            row = cad.iloc[[i]]
            geos[row['DGUID'].item()].set_geometry(
                gpd.GeoDataFrame.to_json(row[["geometry"]]))
        except KeyError:
            if not suppress_prints:
                # In the case of testing, less data is used. It is expected that this key error will be thrown repeatedly
                print(
                    f"DGUID {row['DGUID'].item()} is not present in the geography model, but is present in the geography data")

        if i % 100 == 0:
            print(f"Updated geometry of row {i} of {length}")

    print("Updated all geometry")

    Geography.objects.bulk_update(list(geos.values()), ["geometry"])

    print("Bulk update of geography complete")

    null_vals = list(Geography.objects.filter(geometry=True))
    if len(null_vals) > 0:
        print(f"Null geography values: {null_vals}")


def clear_databases():
    """Deletes all objects in all models
    """
    GeoLevel.objects.all().delete()
    Geography.objects.all().delete()
    Characteristic.objects.all().delete()
    Datum.objects.all().delete()
    print("Cleared prior database")


def gen_geo_levels(geo_levels_names=_GEO_LEVELS):
    """Builds geo_levels based on the list _GEO_LEVELS
    """
    geo_levels = {geo_l: GeoLevel(name=geo_l) for geo_l in geo_levels_names}
    GeoLevel.objects.bulk_create(list(geo_levels.values()))
    print("Generated geography levels")
    return geo_levels


def build_databases(df, add_geography=True):
    """Generates databases based on a Pandas dataframe

    Args:
        df (DataFrame): Census data
    """

    clear_databases()

    print(f"Loading database with {len(df)} lines in the dataframe")
    geos = {}
    characteristics = {}
    datum_list = []

    geo_levels = gen_geo_levels()

    char_names = (df["CHARACTERISTIC_NAME"].unique())
    print(f"Generated char_names, length is {len(char_names)}")

    characteristics = {char_name: Characteristic(
        char_name=char_name) for char_name in char_names}
    print("Characteristic List Created")
    Characteristic.objects.bulk_create(list(characteristics.values()))
    print("Generated Characteristics")

    geo_df = df.drop_duplicates(subset=["DGUID"])
    length = len(geo_df)
    for i, row in geo_df.iterrows():
        geo_name = row["GEO_NAME"]

        # Escape double quotes in the string - JSON compatability
        if '"' in geo_name:
            geo_name = geo_name.replace('"', '\\"')

        geo = Geography(dguid=row['DGUID'], geo_name=geo_name,
                        geo_level=geo_levels[row["GEO_LEVEL"]])
        geos[row['DGUID']] = geo

        if (i % 1000 == 0):
            print(f"Loaded row {i} of {length}")

    Geography.objects.bulk_create((geos.values()))
    print("Created Geography")

    length = len(df)
    consecutive_datums = 0
    for i, row in df.iterrows():
        geo = geos[row['DGUID']]
        characteristic = characteristics[row["CHARACTERISTIC_NAME"]]

        datum = Datum(geo=geo, characteristic=characteristic,
                      value=row["C1_COUNT_TOTAL"])

        # geo_list.append(geo)
        datum_list.append(datum)
        consecutive_datums += 1

        if (i % 1000 == 0):
            print(f"Loaded row {i} of {length}")

            if psutil.virtual_memory()[2] > _MAX_MEM_CONSUMPTION or consecutive_datums > _MAX_BULK_CREATES:
                consecutive_datums = 0
                Datum.objects.bulk_create(datum_list)
                datum_list = []
                print("Saved datums at intermediate point")

    Datum.objects.bulk_create(datum_list)

    print("Database saved")
    if add_geography:
        add_geography()
