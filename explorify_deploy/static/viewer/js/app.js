const BASE_URL = window.location.origin;

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
var GoogleContent = {
  lat : 0,
  lon : 0
};

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
featureLayer.on('layeradd', function(e) {
        var marker = e.layer,
        feature = marker.feature;
        var icon = L.divIcon({
				className: 'custom-div-icon',
        html: '<div class="marker-pin" style= "background:'+e.layer.feature.properties["marker-color"]+';"></div><i class="fa fa-camera awesome">',
        iconSize: [30, 42],
        iconAnchor: [15, 42]
    });
    marker.setIcon(icon);
});

featureLayer.on("ready", function(e) {
  console.log("Ready,steady,go")
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
              iconSize: [1, 1],
              html: '<div class = "leaflet-div-icon" style="text-align:center;color:#000;background:' +
              color + ';border-color:' +color+'">' + clus.getChildCount() + '</div>'
            });
          }
  markerClusters.addTo(map)
  return markerClusters
}
  featureLayer.eachLayer(function (layer) {

    if (!(layer.feature.properties.cluster in group)){
        group[layer.feature.properties.cluster] = makeGroup(layer.feature.properties["marker-color"])
      }

      group[layer.feature.properties.cluster].addLayer(layer);

    $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">'+'<img src='+layer.feature.properties.url+'/>'+'<br />'+ getTitle(layer)+'</td><td class="feature-score">'+layer.feature.properties.aesthetic_score+'</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    // $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">'+'<img src='+layer.feature.properties.url+'/>'+'<br />'+ eval(layer.feature.properties.tags)+'</td><td class="feature-score">'+layer.feature.properties.aesthetic_score+'</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    // $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">' + getTitle(layer) + '</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    layer.on("click", function (e) {
      map.closePopup();
      var content = "";
      GoogleContent.lat = e.target.feature.properties["lat"]
      GoogleContent .lon = e.target.feature.properties["lon"]
      content += "<img align='center' src='"+ e.target.feature.properties["url"] +"'/>";
      content += `<div id='survey' style='width: 100%; position: relative; float:left;'>How did we do?
                          <br>
                          <button type='button' value='g' class='btn btn-feedback' style='margin: 1px; border-color: green;color: green; background-color: white;'>Great Picture!</button>
                          <button type='button'value='n' class='btn btn-feedback' style='margin: 1px; border-color: #ffc107;color: #ffc107; background-color: white;'>Its ok.</button>
                          <button type='button' value='b' class='btn btn-feedback' style='margin: 1px; border-color: red;color: red; background-color: white;'>I don't like it.</button>
                        </div>`;
      content += "<p><a style='float:right; position:relative;' href='http://flickr.com/photo.gne?id="+ e.target.feature.properties["id"] +"'>See on Flickr</a></p>";
      content += "<table class='table table-striped table-bordered table-condensed'>";
      index = 0;
      var array = e.target.feature.properties['tags']

      while (index < array.length) {
        array[index] = ('#' + array[index]).replace(/(#)*/, "#");
        index ++;
      }

      if (userFields.length > 0) {
        $.each(userFields, function(index, property) {
          if (e.target.feature.properties[property]) {
            if (property == 'tags') {
              content +=  "<tr><th>" + property + "</th><td>" + formatProperty(array) + 'hhhh' + "</td></tr>";
            }
            else {
              content += "<tr><th>" + property + "</th><td>" + formatProperty(e.target.feature.properties[property]) + "</td></tr>";
            }
          }
        });
      } else {
        //TODO make the titles work better
        $.each(e.target.feature.properties, function(index, property) {
          if (property) {
            if (index == 'id') {
              //donothing
            } else if (index == 'title') {
              //donothing
            } else if (index == 'lat') {
              //donothing
            } else if (index == 'lon') {
              //donothing
            } else if (index == 'url') {
              //donothing
            } else if (index == 'cluster') {
              //donothing
            } else if (index == 'urls') {
              //donothing
            } else if (index == 'marker-color') {
              //donothing
            } else if (index == 'tags') {
              content +=  "<tr><th>" + index + "</th><td>" + formatProperty(array) + "</td></tr>";
            } else if (index == 'aesthetic_score_scaled' || index == 'rank_score'){
              content += "<tr><th>" + index + "</th><td>" + formatProperty(property) + " out of 5" +"</td></tr>";
            } else if (index == "likes" || index == "views"){
              content += "<tr><th>" + index + "</th><td>" + formatProperty(property) +"</td></tr>";
            }
          }
        });
      }

      content += "<table>";
      $("#feature-title").html(getTitle(e.target));
      $("#feature-info").html(content);
      $("#featureModal").modal("show");
      $("#google-btn").click(function() {
        window.location.href = 'https://www.google.com/maps/search/' + GoogleContent.lat + ',' + GoogleContent.lon, "_blank";
      });
      $("#share-btn").click(function() {
        var link = location.toString() + "&id=" + L.stamp(e.target);
        $("#share-hyperlink").attr("href", link);
        $("#share-twitter").attr("href", "https://twitter.com/intent/tweet?url=" + encodeURIComponent(link));
        $("#share-facebook").attr("href", "https://facebook.com/sharer.php?u=" + encodeURIComponent(link));
      });
      $(".btn-feedback").click(function(clicked_button){
        try{
          selected = clicked_button.target.attributes.value;
          value = selected["value"];
          //Rating on a 5 point scale, which is what rank score is on.
          updateMap = {'g': 5, 'n': 2.5, 'b': 0};
          updateValue = updateMap[value];
          alpha = .005;
          if("rank_score" in e.target.feature.properties){
            oldScore = e.target.feature.properties["rank_score"];
            newRankScore= updateValue * alpha + (1-alpha) * oldScore;
            e.target.feature.properties["rank_score"] = newRankScore;
          }
          alpha = .01;
          if("aesthetic_score_scaled" in e.target.feature.properties){
            oldScore = e.target.feature.properties["aesthetic_score_scaled"];
            newRankScore= updateValue * alpha + (1-alpha) * oldScore;
            e.target.feature.properties["aesthetic_score_scaled"] = newRankScore;
          }
          var params = new URLSearchParams(window.location.search);
            if(params.get("city")){
              let requestData = {city: params.get("city"), properties: e.target.feature.properties};
              var x = new XMLHttpRequest();
              x.open("POST",BASE_URL + '/image', true );
              x.setRequestHeader("Content-Type", "application/json");
              x.onreadystatechange = ()=>{
                if(this.readState === XMLHttpRequest.DONE && this.status ===200){
                  console.log("Yahh")
                }else{
                  console.log(this.status);
                }
              }
              x.send(JSON.stringify(requestData));
            }
        }catch(err){
          console.log(err);
          console.log("something went wrong")
        }finally {
          $("#survey").empty();
          $("#survey").append("<p>Thank You!</p>");
          $("#survey").delay(1000).fadeOut(1000);
        }
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
  var featureList = new List("features", {valueNames: ["feature-name"]});
  featureList.sort("feature-name", {order: sortOrder});
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
  featureLayer.loadURL(decodeURIComponent("atlanta.geojson")).on("ready", function(layer) {
    $("#loading").hide();
  });
}

function fetchData() {
  var params = new URLSearchParams(window.location.search);
  if(params.get("city")){
    urlParams.src = BASE_URL + "/city?city=" + params.get("city");
    return fetchDataWithUrl();
  }else{
    window.location.href="/"
    return;
  }
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
  } else if(typeof value == "number"){
    return value.toFixed(2);
  }else{
    return value;
  }
}

var circle1;
function zoomToFeature(id) {
  if (circle1!=undefined){
  map.removeLayer(circle1);
}
  var layer = featureLayer.getLayer(id);
  if (layer instanceof L.Marker) {
    map.setView([layer.getLatLng().lat, layer.getLatLng().lng], 19);
    console.log(layer.getLatLng())

    circle1 = L.circle([layer.getLatLng().lat, layer.getLatLng().lng], 5, {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5,
        radius: 500
    }).addTo(map);
  }
  else {
    map.fitBounds(layer.getBounds());
  }
  //layer.fire("click");
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

function populateSideBar(bounds){
  $("#feature-list tbody").html("")

  featureLayer.eachLayer(function (layer){

  if((layer.feature.geometry.coordinates[1] <= bounds._northEast.lat)&&(layer.feature.geometry.coordinates[1] >= bounds._southWest.lat)&&(layer.feature.geometry.coordinates[0] <= bounds._northEast.lng)&&(layer.feature.geometry.coordinates[0] >= bounds._southWest.lng)){
    $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '"><td class="feature-name">'+'<img src='+layer.feature.properties.url+'/>'+'<br />'+ eval(layer.feature.properties.tags)+'</td><td class="feature-score">'+layer.feature.properties.aesthetic_score+'</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
    };
  });
  if (urlParams.sort && urlParams.sort == "desc") {
    sortOrder = "desc";
  }
  else {
    sortOrder = "asc";
  }
  var featureList = new List("features", {valueNames: ["feature-score","feature-name"]});
  featureList.sort("feature-score", {order: sortOrder});
}

map.on('moveend', function(){
  populateSideBar(map.getBounds());
});
$("#location-btn").on('click', function() {
  window.location.href = "/"
  //window.location.href = "/"
});
