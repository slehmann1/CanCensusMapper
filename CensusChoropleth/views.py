from django.shortcuts import render
from django.http import HttpResponse
from CensusChoropleth.models import Geography, Characteristic, Datum, GeoLevel
import json
from django.views import View

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

    def get(self, request, level_name = "Province", char_name = "Population, 2021"):

        context = {"data": Map.gen_geojson(level_name, char_name)}
        context = {"data": Map.gen_text(level_name, char_name)}
        return render(request, "CensusChoropleth/map.html", context)

    @staticmethod
    def gen_geo_obj(name, value, geometry):
        return {"type":"Feature", "properties":{"name":name, "value":value}, "geometry":geometry}

    @staticmethod
    def gen_text(level_name, char_name):
        geo_level = GeoLevel.objects.get(name = level_name)
        characteristic = Characteristic.objects.get(char_name = char_name)

        filt = Geography.objects.filter(geo_level = geo_level)

        geos = list(filt)

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


    def gen_list(level_name, char_name):
        geo_level = GeoLevel.objects.get(name = level_name)
        characteristic = Characteristic.objects.get(char_name = char_name)
        geos = list(Geography.objects.filter(geo_level = geo_level, geo_name = "Saskatchewan"))

        values = []

        for geo in geos:
            
           values.append(geo.geometry)
        
        return values


    @staticmethod
    def gen_geojson( level_name, char_name):
        geo_level = GeoLevel.objects.get(name = level_name)
        characteristic = Characteristic.objects.get(char_name = char_name)
        geos = list(Geography.objects.filter(geo_level = geo_level))

        print(f"CHARACTERISTIC: {characteristic}")

        values = []

        for geo in geos:
            
           values.append(Map.gen_geo_obj(geo.geo_name, Datum.objects.get(geo = geo, characteristic = characteristic).value, geo.geometry))

        return [json.dumps(values)]





