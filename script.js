function set_markers (map, drivers) {
    var colors = ['red', 'darkred', 'orange', 'green', 'darkgreen', 'blue', 'purple', 'darkpuple', 'cadetblue'];
    for (i = 0; i < drivers.length; i++) {
        var styleMarker = L.AwesomeMarkers.icon({
            markerColor: colors[i * 2]
        });
        for (j = 0; j < drivers[i].points.length; j++) {
            createMarker(map, styleMarker, drivers[i], colors, drivers);
        }
    }
}

function createMarker(map, icon, driver, colors, drivers) {
    var marker = L.marker(
        [driver.points[j].point_coordinates.lng, driver.points[j].point_coordinates.lat],
        {icon: icon}
    ).addTo(map);
    marker.bindPopup("<b>" + driver.last_name + "</b> " + driver.car +"<br><b>" + driver.points[j].point_title + "</b> " + driver.points[j].point_value + " м. куб.");
    marker.on('mouseover', function(e) {
        marker.openPopup();
        var current_color = this.options.icon.options.markerColor;
        var checkColor = function(color) {
            return color != current_color;
        };
        to_hide = colors.filter(checkColor);
        for (var i = 0; i < to_hide.length; i++ ) {
            $('.awesome-marker-icon-' + to_hide[i]).hide();
        }
        var total_value = 0;
        $.each(driver.points, function() {
            total_value += this.point_value;
        });
        $('#total_value').text(total_value);
        $('#total_points').text($('.awesome-marker-icon-' + current_color).length);
    });

    marker.on('mouseout', function(e) {
        marker.closePopup();
        var current_color = this.options.icon.options.markerColor;
        var checkColor = function(color) {
            return color != current_color;
        };
        to_show = colors.filter(checkColor);
        for (var i = 0; i < to_show.length; i++ ) {
            $('.awesome-marker-icon-' + to_hide[i]).show();
        }
        var total_value = 0;
        $.each(drivers, function() {
            $.each(this.points, function() {
                total_value += this.point_value;
            });
        });
        $('#total_value').text(total_value);

        var total_points = 0;
        $.each(colors, function(){
            total_points += $('.awesome-marker-icon-' + this).length;
        });
        $('#total_points').text(total_points);
    });
}

function output_distances(drivers){
    $.each(drivers, function() {
        var driver = this.last_name;
        $.each(this.points, function (){
            var point_title = this.point_title;
            $.each(this.distances, function (){
                var row = $("<tr />");
                $("#distances").append(row);
                row.append($("<td>" + driver + "</td>"));
                row.append($("<td>" + point_title + "</td>"));
                row.append($("<td>" + this.point_title + "</td>"));
                row.append($("<td>" + this.distance + "</td>"));
            });
        });
    });
}

$(document).ready(function() {
    var mymap = L.map('mapid').setView([55.55, 36.15], 11);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18
    }).addTo(mymap);
    set_markers(mymap, drivers);
    output_distances(drivers);
});
