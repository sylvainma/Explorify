L.mapbox.accessToken = "pk.eyJ1IjoiYnJ5bWNicmlkZSIsImEiOiJXN1NuOFFjIn0.3YNvR1YOvqEdeSsJDa-JUw";

var titleField, cluster, userFields = [], urlParams = {};

var mapboxOSM = L.tileLayer("https://{s}.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token="+L.mapbox.accessToken, {
  maxZoom: 19,
  subdomains: ["a", "b", "c", "d"],
  attribution: 'Basemap <a href="https://www.mapbox.com/about/maps/" target="_blank">© Mapbox © OpenStreetMap</a>'
});

var mapboxSat = L.tileLayer("https://{s}.tiles.mapbox.com/v4/mapbox.streets-satellite/{z}/{x}/{y}.png?access_token="+L.mapbox.accessToken, {
  maxZoom: 19,
  subdomains: ["a", "b", "c", "d"],
  attribution: 'Basemap <a href="https://www.mapbox.com/about/maps/" target="_blank">© Mapbox © OpenStreetMap</a>'
});

var baseLayers = {
  "Street Map": mapboxOSM,
  "Aerial Imagery": mapboxSat
};
/*
var markerClusters = function(color){ return new L.MarkerClusterGroup({
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  zoomToBoundsOnClick: true,
  polygonOptions: {
        fillColor: '#3887be',
        color: '#3887be',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.5
        },
  iconCreateFunction: function(clus) {
    return new L.DivIcon({
      iconSize: [20, 20],
      html: '<div style="text-align:center;color:#fff;background:' +
      color + '">' + clus.getChildCount() + '</div>'
    });
  }
})addTo(map);
}
*/
var markerClusters = new L.MarkerClusterGroup({
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: true,
  zoomToBoundsOnClick: true,
  polygonOptions: {
        fillColor: '#3887be',
        color: '#3887be',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.5
        }
});
var featureLayer = L.mapbox.featureLayer();
var group =[];

featureLayer.on("ready", function(e) {
  function makeGroup(color){
    var markerClusters = new L.MarkerClusterGroup({
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      polygonOptions: {
            fillColor: '#3887be',
            color: '#3887be',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.5
            }
    });
  markerClusters.options["iconCreateFunction"]= function(clus) {
            return new L.DivIcon({
              iconSize: [30, 30],
              html: '<div class = "leaflet-div-icon" style="text-align:center;color:#000;background:' +
              color + ';border-color:' +color+'">' + clus.getChildCount() + '</div>'
            });
          }
  markerClusters.addTo(map)
  return markerClusters
}
  featureLayer.eachLayer(function (layer) {
    //console.log(layer)
    //$("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">' + getTitle(layer) + '</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    if (!(layer.feature.properties.cluster in group)){
        group[layer.feature.properties.cluster] = makeGroup(layer.feature.properties["marker-color"])
        //console.log(layer.feature.properties["marker-color"])
      }
      group[layer.feature.properties.cluster].addLayer(layer);

    $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">'+'<img src='+layer.feature.properties.url+'/>'+'<br />'+ getTitle(layer)+'</td><td class="feature-score">'+layer.feature.properties.aesthetic_score+'</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    //$.getJSON('https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=8dfc2d764539be1fde7d73e3b53a2363&photo_id='+layer.feature.properties["id"]+'&format=json&jsoncallback=?',
    //function (data) {
    //$("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">'+'<img src="https://farm' + data.photo.farm + '.staticflickr.com/' + data.photo.server + '/' + data.photo.id + '_' + data.photo.secret + '.jpg"/>'+'<br />'+ getTitle(layer)+"Score:"+layer.feature.properties.aesthetic_score+'</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    //});
    layer.on("click", function (e) {
      map.closePopup();

      var content = "";
      //content += "<p><a href='http://flickr.com/photo.gne?id="+ e.target.feature.properties["id"] +"'>See on Flickr</a></p>";
      //content += "<table class='table table-striped table-bordered table-condensed'>";
      if (userFields.length > 0) {
        $.each(userFields, function(index, property) {
          if (e.target.feature.properties[property]) {
            content += "<tr><th>" + property + "</th><td>" + formatProperty(e.target.feature.properties[property]) + "</td></tr>";
          }
        });
      } else {
        $.each(e.target.feature.properties, function(index, property) {
          if (property) {
            content += "<tr><th>" + index + "</th><td>" + formatProperty(property) + "</td></tr>";
          }
        });
      }
      content += "<table>";

      $("#feature-title").html(getTitle(e.target));
      //$("#feature-info").html(getImage(e.target));
      $.getJSON('https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=8dfc2d764539be1fde7d73e3b53a2363&photo_id='+layer.feature.properties["id"]+'&format=json&jsoncallback=?',
      function (data) {
      $("#feature-info").html('<img src="https://farm' + data.photo.farm + '.staticflickr.com/' + data.photo.server + '/' + data.photo.id + '_' + data.photo.secret + '.jpg"/>');

      });
      $("#featureModal").modal("show");
      $("#share-btn").click(function() {
        var link = location.toString() + "&id=" + L.stamp(e.target);
        $("#share-hyperlink").attr("href", link);
        $("#share-twitter").attr("href", "https://twitter.com/intent/tweet?url=" + encodeURIComponent(link));
        $("#share-facebook").attr("href", "https://facebook.com/sharer.php?u=" + encodeURIComponent(link));
      });
    });
  });

  if (urlParams.title && urlParams.title.length > 0) {
    var title = decodeURI(urlParams.title);
    $("[name='title']").html(title);
  }
  if (urlParams.sort && urlParams.sort == "desc") {
    sortOrder = "desc";
  }
  else {
    sortOrder = "asc";
  }
  var featureList = new List("features", {valueNames: ["feature-score","feature-name"]});
  featureList.sort("feature-score", {order: sortOrder});
  markerClusters.clearLayers().addLayer(featureLayer);
});

featureLayer.once("ready", function(e) {
  /* Update navbar & layer title from URL parameter */
  if (urlParams.title && urlParams.title.length > 0) {
    var title = decodeURI(urlParams.title);
    $("[name='title']").html(title);
  }
  /* Add navbar logo from URL parameter */
  if (urlParams.logo && urlParams.logo.length > 0) {
    $("#navbar-title").prepend("<img src='" + urlParams.logo + "'>");
  }
  /* If id param passed in URL, zoom to feature, else fit to cluster bounds or fitWorld if no data */
  if (urlParams.id && urlParams.id.length > 0) {
    var id = parseInt(urlParams.id);
    zoomToFeature(id);
  } else {
    if (featureLayer.getLayers().length === 0) {
      map.fitWorld();
    } else {
      map.fitBounds(this.getBounds(), {
        maxZoom: 19
      });
    }
  }
});

var map = L.map("map", {
  zoom: 10,
  layers: [mapboxOSM]
}).fitWorld();
map.attributionControl.setPrefix("");

var layerControl = L.control.layers(baseLayers, null, {
  collapsed: document.body.clientWidth <= 767 ? true : false
}).addTo(map);

var locateControl = L.control.locate({
  drawCircle: true,
  follow: true,
  setView: true,
  keepCurrentZoomLevel: false,
  markerStyle: {
    weight: 1,
    opacity: 0.8,
    fillOpacity: 0.8
  },
  circleStyle: {
    weight: 1,
    clickable: false
  },
  icon: "fa fa-crosshairs",
  metric: false,
  strings: {
    title: "My location",
    popup: "You are within {distance} {unit} from this point",
    outsideMapBoundsMsg: "You seem located outside the boundaries of the map"
  },
  locateOptions: {
    maxZoom: 19,
    watch: true,
    enableHighAccuracy: true,
    maximumAge: 10000,
    timeout: 10000
  }
}).addTo(map);

function fetchDataWithUrl() {
  $("#loading").show();
  featureLayer.clearLayers();
  $("#feature-list tbody").empty();
  if (urlParams.src.indexOf(".topojson") > -1) {
    omnivore.topojson(decodeURIComponent(urlParams.src), null, featureLayer).on("ready", function(layer) {
      $("#loading").hide();
    });
  }
  else {
    featureLayer.loadURL(decodeURIComponent(urlParams.src)).on("ready", function(layer) {
      $("#loading").hide();
    });
  }
}
function fetchDataLocally() {
  $("#loading").show();
  featureLayer.clearLayers();
  $("#feature-list tbody").empty();
  featureLayer.loadURL(decodeURIComponent("atlantadata.geojson")).on("ready", function(layer) {
    $("#loading").hide();
  });
}

function fetchData() {
  return fetchDataLocally();
}

function getTitle(layer) {
  if (urlParams.title_field) {
      titleField = decodeURI(urlParams.title_field);
  }
  if (titleField && layer.feature.properties[titleField]) {
    return layer.feature.properties[titleField];
  }
  else {
    if ("title" in layer.feature.properties) {
      return layer.feature.properties["title"];
    }
    else {
      if (userFields.length > 0) {
        return layer.feature.properties[userFields[0]];
      }
      else {
        return layer.feature.properties[Object.keys(layer.feature.properties)[0]];
      }
    }
  }
}


function formatProperty(value) {
  if (typeof value == "string" && (value.indexOf("http") === 0 || value.indexOf("https") === 0)) {
    return "<a href='" + value + "' target='_blank'>" + value + "</a>";
  } else {
    return value;
  }
}

function zoomToFeature(id) {
  var layer = featureLayer.getLayer(id);
  if (layer instanceof L.Marker) {
    map.setView([layer.getLatLng().lat, layer.getLatLng().lng], 19);
  }
  else {
    map.fitBounds(layer.getBounds());
  }
  layer.fire("click");
  /* Hide sidebar and go to the map on small screens */
  if (document.body.clientWidth <= 767) {
    $("#sidebar").hide();
    map.invalidateSize();
  }
}

if (location.search) {
  var parts = location.search.substring(1).split("&");
  for (var i = 0; i < parts.length; i++) {
    var nv = parts[i].split("=");
    if (!nv[0]) continue;
    urlParams[nv[0]] = nv[1] || true;
  }
}

if (urlParams.fields) {

  fields = urlParams.fields.split(",");
  $.each(fields, function(index, field) {
    field = decodeURI(field);
    userFields.push(field);
  });
}

if (urlParams.cluster && (urlParams.cluster === "false" || urlParams.cluster === "False" || urlParams.cluster === "0")) {
  cluster = false;
} else {
  cluster = false; // Sylvain: should be true here, set false for experimentations
}

if (urlParams.attribution) {
  var attribution = decodeURI(urlParams.attribution);
  map.attributionControl.setPrefix(attribution);
}

/*
if (cluster === true) {
  map.addLayer(markerClusters);
  layerControl.addOverlay(markerClusters, "<span name='title'>GeoJSON Data</span>");
} else {
  map.addLayer(featureLayer);
  layerControl.addOverlay(featureLayer, "<span name='title'>GeoJSON Data</span>");
}
*/
$("#refresh-btn").click(function() {
  fetchData();
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#auto-refresh").click(function() {
  if ($(this).prop("checked")) {
    autoRefresh = window.setInterval(fetchData, 60 * 1000);
    fetchData();
  } else {
    clearInterval(autoRefresh);
  }
});

$("#full-extent-btn").click(function() {
  map.fitBounds(featureLayer.getBounds());
  $(".navbar-collapse.in").collapse("hide");
  return false;
});

$("#list-btn").click(function() {
  $("#sidebar").toggle();
  map.invalidateSize();
  return false;
});

$("#nav-btn").click(function() {
  $(".navbar-collapse").collapse("toggle");
  return false;
});

$("#sidebar-toggle-btn").click(function() {
  $("#sidebar").toggle();
  map.invalidateSize();
  return false;
});

$("#sidebar-hide-btn").click(function() {
  $("#sidebar").hide();
  map.invalidateSize();
});

$(document).ready(function() {
  fetchData();
  $("#download").attr("href", urlParams.src);
});

$(document).on("click", ".feature-row", function(e) {
  zoomToFeature(parseInt($(this).attr("id"), 10));
});
