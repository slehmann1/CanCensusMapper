from django.shortcuts import render
from django.http import HttpResponse
from CensusChoropleth.models import Geography, Characteristic, Datum, GeoLevel
import json
from django.views import View
from django.db.models import Q

# Create your views here.


def test(request):
    return HttpResponse("Hello, world.")


def print_characteristics(request, geoname):

    try:
        geo = Geography.objects.get(geo_name=geoname)
    except Geography.DoesNotExist:
        return HttpResponse("Invalid value")

    data = list(Datum.objects.filter(geo=geo))

    text = []
    for datum in data:
        text.append(str(datum))
        
    # text+=str(data[0])
    # print(text)
    context = {"text": text}
    return render(request, "CensusChoropleth/print.html", context)

class Map(View):
    _GEO_HEAD = '{"type": "FeatureCollection", "features": ['
    _GEO_TAIL = ']}'
    _PROP_SPLIT = 'properties": {'
    _char_list = None

    GEO_LEVELS = ['Provinces and Territories', 'Census Divisions', 'Census Subdivisions']
    _SINGULAR_GEO_LEVELS = ['Provinces and Territories', 'Census division', 'Census subdivision']

    def get(self, request):
        geolevel = request.GET.get("geolevel", Map.GEO_LEVELS[0])
        char_name = request.GET.get("characteristic", "Population, 2021")
        
        context = {"data": Map.gen_text(geolevel, char_name), "geo_levels":Map.GEO_LEVELS, "characteristics":Map.get_char_list(), "characteristic":char_name}
        return render(request, "CensusChoropleth/map.html", context)

    #TODO: Unit test - Req database
    @staticmethod
    def get_char_list():
        # Memoize
        if Map._char_list is None:
            chars = Characteristic.objects.all()
            Map._char_list = []
            for char in chars:
                Map._char_list.append(char.char_name)
        
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
            if geo_level==Map.GEO_LEVELS[i]:
                return Map._SINGULAR_GEO_LEVELS[i]
        
        raise ValueError

    #TODO: Unit test - Req database
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
            geo_levels = geo_levels.filter(Q(name = "Province") | Q(name="Territory"))
        else:
            geo_levels = geo_levels.filter(name = level_name)
        geo_levels = geo_levels

        characteristic = Characteristic.objects.get(char_name = char_name)

        geos = list(Geography.objects.filter(geo_level__in = geo_levels))

        # Generate Text
        text = Map._GEO_HEAD
        # TODO: Batch requests from datum model to decrease database calls
        for geo in geos:
            add = geo.geometry[len(Map._GEO_HEAD):len(geo.geometry)-len(Map._GEO_TAIL)].split(Map._PROP_SPLIT)
            datum = Datum.objects.get(geo=geo, characteristic=characteristic)

            # Add properties
            props = '"name":"'+geo.geo_name+'",'
            props += '"value":'+str(datum.value)
            text+= ''.join([add[0],Map._PROP_SPLIT,props,add[1]])
            
            text+=","
        
        # Remove trailing comma
        text = text[0:len(text)-1]
        text+=Map._GEO_TAIL
        
        return text


