var geojson, map, info, hovered_geo, hovered_val;
var hovered = false;

//#edf8fb
var colors = ['#edf8fb', '#bfd3e6', '#9ebcda', '#8c96c6', '#8c6bb1', '#88419d', '#6e016b']
var naColor = '#525252'

build_map();

function build_map() {
    var data = JSON.parse(raw_data);
    map = L.map('map').setView([66, -96], 4);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E">Data From 2021 Canada Census of Population</a>'
    }).addTo(map);

    geojson = L.geoJson(data, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    // Create popups
    map.on('click', function (e) {
        if (!hovered) {
            return
        }
        var popLocation = e.latlng;
        L.popup(popLocation, { content: '<div class = hover><h4>' + hovered_geo + '</h4>' + hovered_val + '</div>' }).openOn(map);
    });

    info = L.control();
    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        this._div.style = ".info"
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = '<h4>' + characteristic + '</h4>' + (props ?
            '<b>' + props.name + '</b><br />' + props.value
            : 'Hover over a region');
    };

    info.addTo(map);

    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend'), labels = [];

        div.innerHTML +=
            '<i style="background:' + getColor(leg_vals[0]) + '"></i> ≤ ' + leg_vals[0] + '<br>';

        // loop through the value intervals and generate a label with a colored square for each interval
        for (var i = 0; i < leg_vals.length - 1; i++) {
            div.innerHTML +=
                '<i style="background:' + getColor(leg_vals[i] + 1) + '"></i> ' +
                leg_vals[i] + '&ndash;' + leg_vals[i + 1] + '<br>';
        }

        div.innerHTML +=
            '<i style="background:' + getColor(leg_vals[leg_vals.length]) + '"></i> ≥ ' + leg_vals[leg_vals.length - 1] + '<br>';

        div.innerHTML +=
            '<i style="background:' + naColor + '"></i> No Data';

        return div;
    };

    legend.addTo(map);
}

function style(feature) {
    return {
        fillColor: getColor(feature.properties.value),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: layer_hover,
        mouseout: layer_dehover,
        mousedown: layer_click

    });

}
function layer_hover(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    layer.bringToFront();
    info.update(layer.feature.properties);
    hovered = true;
}

function layer_dehover(e) {
    geojson.resetStyle(e.target);
    info.update();
    hovered = false;
}

function layer_click(e) {
    var geo = e.target;
    hovered_geo = geo.feature.properties.name;
    hovered_val = geo.feature.properties.value;
}


//TODO: Make this scalable based on mins/maxes/outliers/etc.
function getColor(d) {

    if (d == "N/A") {
        return naColor;
    }

    for (i = 0; i < leg_vals.length; i++) {
        if (d <= leg_vals[i]) {
            return colors[i]
        }
    }

    return colors[colors.length - 1];
}

