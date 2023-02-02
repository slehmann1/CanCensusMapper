from django.shortcuts import render
from django.http import HttpResponse
from CensusChoropleth.models import Geography, Characteristic, Datum, GeoLevel
import numpy as np
import math
from django.views import View
from django.db.models import Q
import json

# Create your views here.


def test(request):
    return HttpResponse("Hello, world.")


def print_characteristics(request, geoname):

    try:
        geo = Geography.objects.get(geo_name=geoname)
    except Geography.DoesNotExist:
        return HttpResponse("Invalid value")

    data = list(Datum.objects.filter(geo=geo))

    text = [str(datum) for datum in data]
    context = {"text": text}
    return render(request, "CensusChoropleth/print.html", context)


class Map(View):
    _GEO_HEAD = '{"type": "FeatureCollection", "features": ['
    _GEO_TAIL = ']}'
    _PROP_SPLIT = 'properties": {'
    _char_list = None

    GEO_LEVELS = ['Provinces and Territories',
                  'Census Divisions', 'Census Subdivisions']
    _SINGULAR_GEO_LEVELS = ['Provinces and Territories',
                            'Census division', 'Census subdivision']
    _LEGEND_STEPS = 6

    def get(self, request):
        geolevel = request.GET.get("geolevel", Map.GEO_LEVELS[0])
        char_name = request.GET.get("characteristic", "Population, 2021")

        data, leg_vals = Map.gen_text(geolevel, char_name)

        context = {"data": data, "leg_vals": json.dumps(list(
            leg_vals)), "geo_levels": Map.GEO_LEVELS, "characteristics": Map.get_char_list()}
        return render(request, "CensusChoropleth/map.html", context)

    # TODO: Unit test - Req database
    @staticmethod
    def get_char_list():
        # Memoize
        if Map._char_list is None:
            chars = Characteristic.objects.all()

            Map._char_list = [char.char_name for char in chars]

        return Map._char_list

    @staticmethod
    def de_pluaralize_geo_levels(geo_level):
        """Converts a plural geo_level string displayed on the page to the singular value used in the database

        Args:
            geo_level (string): String represenation of the plural geo_level

        Raises:
            ValueError: If the geo_level is not recognized

        Returns:
            String: Singular representation of the geo_level
        """
        for i in range(len(Map.GEO_LEVELS)):
            if geo_level == Map.GEO_LEVELS[i]:
                return Map._SINGULAR_GEO_LEVELS[i]

        raise ValueError

    # TODO: Unit test - Req database
    @staticmethod
    def gen_text(level_name, char_name):
        """Generates JSON representation of a feature collection which can be plotted by a map

        Args:
            level_name (String): The level of geography that should be displayed. Member of Map.GEO_LEVELS
            char_name (String): The characteristic to be plotted

        Returns:
            String: JSON representation of feature collection
        """
        level_name = Map.de_pluaralize_geo_levels(level_name)
        print(f"Level Name: {level_name}, Char Name: {char_name}")

        # Return both provinces and territories together
        geo_levels = GeoLevel.objects.all()
        if level_name == Map.GEO_LEVELS[0]:
            geo_levels = geo_levels.filter(
                Q(name="Province") | Q(name="Territory"))
        else:
            geo_levels = geo_levels.filter(name=level_name)

        characteristic = Characteristic.objects.get(char_name=char_name)

        filt = Geography.objects.filter(geo_level__in=geo_levels)
        geos = list(filt)

        values = []

        # Generate Text
        text = Map._GEO_HEAD
        for geo in geos:
            add = geo.geometry[len(Map._GEO_HEAD):len(
                geo.geometry)-len(Map._GEO_TAIL)].split(Map._PROP_SPLIT)
            datum = Datum.objects.filter(
                geo=geo, characteristic=characteristic)[0]
            value = datum.value
            # Add properties
            props = f'"name":"{geo.geo_name}",'
            if value is None:
                props += '"value":'+'"N/A"'
            else:
                props += f'"value":{str(value)}'
                values.append(value)
            text += ''.join([add[0], Map._PROP_SPLIT, props, add[1]])

            text += ","

        # Remove trailing comma
        text = text[:-1]
        text += Map._GEO_TAIL
        leg_ranges = Map.legend_ranges(values)

        return text, leg_ranges

    @staticmethod
    def legend_ranges(values):
        """For a given list of values generates a numpy array of suitable legend steps

        Args:
            values ([float]): values to create legend steps fro

        Returns:
            [float]: legend steps
        """
        quant_025 = np.quantile(values, 0.25)
        quant_075 = np.quantile(values, 0.75)
        iqr = quant_075 - quant_025

        min_val, max_val = quant_025 - 3 * iqr, quant_075 + 3 * iqr

        if min_val < 0 and min(values) >= 0:
            min_val = 0

        min_val, max_val = Map.round_leg_val(min_val, max_val)

        # Determine the number of decimals to round the legend steps to, based on what the maximum value is
        decs = 0
        val = abs(max_val)

        while val < 50:
            val *= 10
            decs += 1

        return np.round(np.arange(min_val, max_val, (max_val-min_val)/Map._LEGEND_STEPS), decs)

    @staticmethod
    def round_leg_val(min_val, max_val):
        """Rounds values to numbers suitable for legend values.

        Args:
            The value to round (int)

        Raises:
            TypeError: _description_

        Returns:
            _type_: A rounded value
        """
        diff = max_val - min_val

        first_dig = int(str(diff)[0])
        num_digs = len(str(int(diff)))

        if first_dig < 3:
            num_digs -= 1

        diff = math.ceil(diff/(10**(num_digs-1)))*10**(num_digs-1)

        max_val = min_val+diff

        return min_val, max_val
