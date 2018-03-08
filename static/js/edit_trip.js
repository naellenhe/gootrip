'use strict';

let map, marker, loc, content;
let infoWindow = new google.maps.InfoWindow({width: 150});
let bounds = new google.maps.LatLngBounds();
let labels = ['1','2','3','4','5','6','7','8','9','10',
              '11','12','13','14','15','16','17','18','19','20',
              '21','22','23','24','25','26','27','28','29','30'];
let labelIndex = 0;

///////////////
// basic map //
///////////////

function initMap() {
  // Initial Map
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 9,
    center: {lat: 37.6653831, lng: -122.4194155}
  });

  // Retrieving$(".trip-info").data('tripid'); the information with AJAX
  let tripId = $("#trip-info").data('tripid');
  $.get('/attractions.json', { 'trip_id': tripId }, function (dests_attractions) {

    for (let dest_id in dests_attractions) {
      // In JSON the attractions looks like:
      // {
      //   "1": {
      //     "attractionLat": "37.7879797", 
      //     "attractionLng": "-122.4075169", 
      //     "attractionName": "Union Square"
      //   }, 
      //   "2": {
      //     "attractionLat": "37.8079996", 
      //     "attractionLng": "-122.4177434", 
      //     "attractionName": "Fishermans Warf"
      //   }, 
      //   "3": {
      //     "attractionLat": "37.8269775", 
      //     "attractionLng": "-122.4229555", 
      //     "attractionName": "Alcatraz Island"
      //   }, 
      //   "4": {
      //     "attractionLat": "37.8199286", 
      //     "attractionLng": "-122.4782551", 
      //     "attractionName": "Golden Gate Bridge"
      //   }
      // }

      let attractions = dests_attractions[dest_id];
      let count = Object.keys(attractions).length;

      if (count !== 0) {
        let attraction;

        let keys = Object.keys(attractions);
        keys.sort();

        //Sort attraction object by the key
        for (let i = 0; i < count; i++) {
            let key = keys[i];
            attraction = attractions[key];
            // console.log(key, i);
            // console.log(attraction);

            if (attraction.attractionLat && attraction.attractionLng){
              // Define the marker
              let markerPosition = new google.maps.LatLng(
                                          attraction.attractionLat,
                                          attraction.attractionLng);


              marker = addMarker(markerPosition, map, attraction.attractionName);

              // marker = new google.maps.Marker({
              //     position: markerPosition,
              //     map: map,
              //     title: 'Attraction name: ' + attraction.attractionName,
              //     // place means a business, point of interest or geographic location.
              //     // The info window will contain information about the place and an option for the user to save it.
              //     place: {
              //       location: markerPosition,
              //       query: attraction.attractionName
              //     },
              // });

              // Everytime a new marker is added, append to bounds
              loc = new google.maps.LatLng(
                                marker.position.lat(),
                                marker.position.lng()
              );
              bounds.extend(loc);

              // Content for InfoWindow
              content = "Attraction: " + attraction.attractionName;

              // Inside the loop we call bindInfoWindow passing it the marker,
              // map, infoWindow, and content
              bindInfoWindow(marker, map, infoWindow, content);

              highlightAttraction(marker, map, key);
            }
        }
      }

      map.fitBounds(bounds);       // auto-zoom
      map.panToBounds(bounds);     // auto-center
    } // end of if statement
  }); // end of ajax get method
}

// Adds a marker to the map.
function addMarker(markerPosition, map, attractionName) {

  // Add the marker at the clicked location, and add the next-available label
  // from the array of alphabetical characters.
  marker = new google.maps.Marker({
      position: markerPosition,
      map: map,
      title: 'Attraction name: ' + attractionName,
      // place means a business, point of interest or geographic location.
      // The info window will contain information about the place and an option for the user to save it.
      place: {
        location: markerPosition,
        query: attractionName
      },
      label: labels[labelIndex++ % labels.length],
  });
  return marker;
}


initMap();

// Opens the InfoWindow when marker is clicked.
function bindInfoWindow(marker, map, infoWindow, content) {
  marker.addListener('click', function() {
    infoWindow.close();
    infoWindow.setContent(content);
    infoWindow.open(map, marker);
  });
}


function highlightAttraction(marker, map, key) {
  let attSelector = '.attraction-info[data-attractionid=' + key + '] .thumbnail-row';
  marker.addListener('mouseover', function() {
    console.log("mouseover the marker of ", key);

    $(attSelector).attr('style', 'background-color: #cce6ff;');
  });
  marker.addListener('mouseout', function() {
    $(attSelector).removeAttr('style', 'background-color: #cce6ff;');
  });
}


/////////////////////////////
// geocoding by place name //
/////////////////////////////

function addAttractionMarkerByName(dest_name, attraction_id, attraction_name) {
  let attraction = new google.maps.Geocoder();
  let premise = attraction_name + "," + dest_name;

  attraction.geocode({'address': premise}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);

        // Send the location to db
        let locationResult = {
                        'attraction_id': attraction_id,
                        'attraction_lat': results[0].geometry.location.lat,
                        'attraction_lng': results[0].geometry.location.lng
                      };

        $.post("/add-attraction-coordinate", locationResult, function(results){
          console.log(results);
          console.log("Successfully added coordinate to db");
        });

        marker = addMarker(results[0].geometry.location, map, premise);
        marker.setAnimation(google.maps.Animation.DROP);

        // marker = new google.maps.Marker({
        //   map: map,
        //   place: {
        //     location: results[0].geometry.location,
        //     query: premise
        //   },
        //   animation: google.maps.Animation.DROP,
        // });

        // // Construct a new InfoWindow.
        // infoWindow = new google.maps.InfoWindow({
        //   content: "found:" + premise
        // });

        content = "Found:" + premise;
        bindInfoWindow(marker, map, infoWindow, content);

        loc = new google.maps.LatLng(
                          marker.place.location.lat(),
                          marker.place.location.lng()
                        );
        bounds.extend(loc);

        highlightAttraction(marker, map, attraction_id);

        resetMapCenter(loc);
        map.setZoom(13);

        // map.fitBounds(bounds);       // auto-zoom
        // map.panToBounds(bounds);     // auto-center

        // // Opens the InfoWindow when marker is clicked.
        // marker.addListener('click', function() {
        //   infoWindow.open(map, marker);
        // });
      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
    });
}

// get geocode for destination 
function getDestGeocode(dest_id, dest_name) {
  let dest = new google.maps.Geocoder();
  let premise = dest_name;

  dest.geocode({'address': dest_name}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);

        // Send the location to db
        let locationResult = {
                        'dest_id': dest_id,
                        'dest_lat': results[0].geometry.location.lat,
                        'dest_lng': results[0].geometry.location.lng
                      };

        let loc = new google.maps.LatLng(
                        results[0].geometry.location.lat(),
                        results[0].geometry.location.lng()
                      );
        resetMapCenter(loc);

        $.post("/add-dest-coordinate", locationResult, function(results){
          console.log(results);
          console.log("Successfully added coordinate to db");
        });

      } else {
        alert('Geocode was not successful for the following reason: ' + status);
      }
    });
}


// Reset map center when the destination is added
function resetMapCenter(loc) {
  map.setCenter(loc);
}

// Google place library autocomplete widget
function placeAutocomplete(element_id){
  let destInput = document.getElementById(element_id);
  let autocomplete = new google.maps.places.Autocomplete(destInput);

}


// EventListener for trip name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur', '#trip-info input', function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('tripid'));
  let tripId = $(this).parent().data('tripid');
  let tripName = $(this).val();
  // Check the input data is not blank
  if ( tripName == false){
    alert("Trip name cannot be empty!");
  } else {
    let tripInfo = {'trip_id': tripId,
                    'trip_name': tripName};
    $.post('/update-trip.json', tripInfo, function(results){
      console.log(results);
    });
  }
});


// EventListener for destination name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur', '.dest-info > input:not(#add-dest-name)', function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('destid'));
  let destId = $(this).parent().data('destid');
  let destName = $(this).val();
  // Check the input data is not blank
  if ( destName == false){
    alert("Destination name cannot be empty!");
  } else {
    let destInfo = {'dest_id': destId,
                    'dest_name': destName};
    $.post('/update-dest.json', destInfo, function(results){
      console.log(results);
    });    
  }
});


// EventListener for attraction name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur','.attraction-info > input', function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('attractionid'));
  let attractionId = $(this).parent().data('attractionid');
  let attractionName = $(this).val();
  // Check the input data is not blank
  if ( attractionName == false){
    alert("Attraction name cannot be empty!");
  } else {
    let attractionInfo = {'attraction_id': attractionId,
                          'attraction_name': attractionName};
    $.post('/update-attraction.json', attractionInfo, function(results){
      console.log(results);
    });
  }
});


// EventListener for note content field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur','.note-info > textarea', function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('noteid'));
  let noteId = $(this).parent().data('noteid');
  let noteContent = $(this).val();
  let noteInfo = {'note_id': noteId,
                  'note_content': noteContent};
  $.post('/update-note.json', noteInfo, function(results){
    console.log(results);
  });
});


// EventListener when mouse over the input fields, show border to let user know it's editable
$('body').on({
  mouseenter: function(evt) {
    $(this).attr('style', 'border-color: grey');
  }, mouseleave: function(evt) {
    $(this).attr('style', 'border-color: transparent');
  }
}, '.btn-hidden-input-field');

$('.dest-info').on({
  mouseenter: function(evt) {
    $(this).find('.add-new-attraction :button').show();
  }, mouseleave: function(evt) {
    $(this).find('.add-new-attraction :button').hide();
  }
});


//Delete a dest
function deleteDest(evt){
  let target = $(evt.target);
  let tripId = target.data('tripid');
  let destId = target.data('destid');
  let destName = target.data('destname');
  let destSelector = '.dest-info[data-destid=' + destId + ']';
  let msg = 'Do you want to delete your destination: ' + destName + '?';
  let confirmResponse = confirm(msg);
  if (confirmResponse === true){
    $(destSelector).remove();

    //Use ajax to delete dest data in the database
    $.post("/delete-dest", {'dest_id': destId, 'trip_id': tripId}, function(results){
      console.log(results);
    });
  }
}

$('body').on('click', '.btn-delete-dest', deleteDest);


//Delete a attraction and its note
function deleteAttraction(evt){
  let target = $(evt.target);
  let destId = $(evt.target).data('destid');
  let destName = $(evt.target).data('destname');
  let attractionId = target.data('attractionid');
  let attractionName = target.data('attractionname');
  let attractionSelector = '.attraction-info[data-attractionid=' + attractionId + ']';
  let msg = 'Do you want to delete your attraction: ' + attractionName + '?';
  let confirmResponse = confirm(msg);
  if (confirmResponse === true){
    $(attractionSelector).remove();

    //Use ajax to delete attraction data in the database
    $.post("/delete-attraction", {'attraction_id':attractionId}, function(results){
      console.log(results);
    });

    //Update recommendation
    getRecommendedAttraction(destId, destName);
  }
}

$('body').on('click', '.btn-delete-attraction', deleteAttraction);


//Recommend users attractions based on their current choices to a specific destination.
function getRecommendedAttraction(destId, destName){
  // let destId = $(evt.target).data('destid');
  // let destName = $(evt.target).data('destname');
  $.post('/get-recommendation', {dest_id: destId, dest_name: destName}, function(response){
    console.log(response);
    let destSelector = ".recommeded-atts[data-destid='" + destId + "']";

    //showing recommended attractions
    let recommendAttractionHtml = '';

    //if the level is 1 which means it has the highest similarity
    if (response.recommended_atts.length > 0){
      if (response.recommended_level == '1'){
        recommendAttractionHtml += '<p class="recommended-level">People who visited the attractions in your list also visited:</p>';
      } else {
        recommendAttractionHtml += '<p class="recommended-level">Popular attractions in the city:</p>';
      }

      for (let recommended_att of response.recommended_atts){
        recommendAttractionHtml += "<button class='btn btn-default btn-sm btn-recommended-atts' data-toggle='modal' data-target='#addNewAttractionModal' data-destid='" +  destId + "' data-destname='" + destName + "' data-attractionname='" + recommended_att +  "'>" + recommended_att + "</button> ";
      }
    }
    $(destSelector).html(recommendAttractionHtml);
  });

}


// modal

function addNewAttractionToRoute(evt) {
  console.log('Hi!!!modal button is clicked');
  // send the new attraction name along with its dest_id
  let destId = $(".modal").data("dest_info").destId;
  let destName = $(".modal").data("dest_info").destName;
  
  //Multiple notes in one attraction
  let noteArray = new Array();
  $(".add-note").each(function(){
    if ($(this).val()){
      noteArray.push($(this).val());
    }
  });

  let attraction = {'attraction_name': $("#add-attraction-name").val(),
                    'dest_id': destId,
                    'note[]': noteArray};
  $.post("/new-attraction", attraction, function(results){
    let attraction_name = results.name;
    let attraction_id = results.attraction_id;
    let dest_name = destName;
    // notes is an array contains mulitiple notes
    let notes = results.notes;
    console.log("Added to database", attraction_name);
    addAttractionMarkerByName(dest_name, attraction_id, attraction_name);
    console.log("Found the geocode for:" + results.name);

    let noteHtmls = '';
    for (let note of notes){
      let noteHtml = '<li class="note-info note-content" data-noteid="' + note.note_id + '">' +
                      '<textarea class="textarea-edit" rows="4" cols="50" placeholder="Add note">'+ note.content + '</textarea>' +
                     '</li>'; 
      noteHtmls += noteHtml;
    }

    let maxDigit  = $(".attraction-info").length;
    // Reset the form value
    $('#add-attraction-name, .add-note').val('');
    let attractionHtml ='<li class="attraction-info" data-attractionid="' + attraction_id + '">' +
                  '<button class="btn btn-default btn-xs btn-del-minus-mark btn-delete-attraction" data-attractionid="' + attraction_id + 
                  '" data-attractionname="' + attraction_name + '" data-destid="' + destId +'" data-destname="'+ destName + '"> - </button> ' +
                  '<div class="marker-container">' +
                    '<img src="/static/red_marker.png" alt="{{ att.name }}" style="width:27px;">' +
                    '<div id="new-marker-digit" class="marker-digit">' + (maxDigit) + '</div>' +
                  '</div> ' +
                  '<input class="btn-hidden-input-field" type="text" value="' + attraction_name + '" size="35">' +
                    '<div>' +
                      '<ul>' + noteHtmls + '</ul>' +
                    '</div>' +
                '</li>';

    console.log('attractionHtml looks like:', attractionHtml);
    let destSelector = ".dest-info[data-destid='" + destId + "'] .populated-dests";
    $(destSelector).append(attractionHtml);

    //Update recommendation
    getRecommendedAttraction(destId, destName);
  });
}


$('.modal').on('show.bs.modal', function (evt) {
  let button = $(evt.relatedTarget); // Button that triggered the modal
  let destId = button.data('destid'); // Extract info from data-* attributes
  let destName = button.data('destname');
  let attractionName = button.data('attractionname');

  // Store the data to the modal
  $(".modal").data("dest_info",{
                              destId: destId, 
                              destName: destName
                            });

  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  $('#addNewAttractionModal .modal-title').text('New attraction to: ' + destName);
  if (attractionName != ''){
    $('#addNewAttractionModal #add-attraction-name').val(attractionName);
  }

  // When the save button is clicked, send data to the route
  $('#btn-save-new-attraction').off('click', addNewAttractionToRoute);

  $('#btn-save-new-attraction').on('click', addNewAttractionToRoute);
});


// Noted added on previous modal will be removed after it closed
$('.modal').on('hide.bs.modal', function (evt) {
  console.log('modal is closed');
  $('.input-note-removed-later').remove();
});


//When clicking the button, add more empty input field for notes
$("#btn-append-note").on('click', function(evt){
  evt.preventDefault();
  $("#note-form").append("<div class='input-note-removed-later note-content'><textarea class='add-note textarea-edit' name='note-content[]' placeholder='Add notes' rows='4' cols='50'></textarea></div>");
});


$( document ).ready(function(){
  $(".recommeded-atts").each(function(){
    let destId = $( this ).data('destid');
    let destName = $( this ).data('destname');
    console.log(destId,destName);
    getRecommendedAttraction(destId, destName);
  });
});

