"use strict";

let map, marker, loc, content;
let infoWindow = new google.maps.InfoWindow({width: 150});
let bounds = new google.maps.LatLngBounds();

///////////////
// basic map //
///////////////

function initMap() {
  // Initial Map
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 9,
    center: {lat: 37.6653831, lng: -122.4194155}
  });

  // Retrieving the information with AJAX
  let tripId = $('#trip-info').data('tripid');
  $.get('/attractions.json', { 'trip_id': tripId }, function (attractions) {
      // JSON looks like:
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
    let count = Object.keys(attractions).length;

    if (count !== 0) {
      let attraction;
      // let totalLat = 0;
      // let totalLng = 0;

      for (let key in attractions) {
          attraction = attractions[key];

          if (attraction.attractionLat && attraction.attractionLng){
            // Define the marker
            let marker_position = new google.maps.LatLng(
                                        attraction.attractionLat,
                                        attraction.attractionLng);

            marker = new google.maps.Marker({
                position: marker_position,
                map: map,
                title: 'Attraction name: ' + attraction.attractionName,
                // place means a business, point of interest or geographic location.
                // The info window will contain information about the place and an option for the user to save it.
                place: {
                  location: marker_position,
                  query: attraction.attractionName
                },
            });

            // Everytime a new marker is added, append to bounds
            loc = new google.maps.LatLng(
                              marker.position.lat(),
                              marker.position.lng()
            );
            bounds.extend(loc);

            // Content for InfoWindow.
            content = "Attraction: " + attraction.attractionName;

            // Inside the loop we call bindInfoWindow passing it the marker,
            // map, infoWindow, and contentString
            bindInfoWindow(marker, map, infoWindow, content);

            highlightAttraction(marker, map, key);

            // // Calculate the average LatLng with all given positions
            // totalLat += parseFloat(attraction.attractionLat);
            // totalLng += parseFloat(attraction.attractionLng);
          }   // end of if that only make markers for attractions with available latlng
      }   // end of for loop of attractions

      // if (totalLng  && totalLat){
      // map.setCenter({lat: totalLat/count, lng: totalLng/count});
      // }

      map.fitBounds(bounds);       // auto-zoom
      map.panToBounds(bounds);     // auto-center
    } // end of if statement
  }); // end of ajax get method
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
  let attSelector = '.attraction-info[data-attractionid=' + key + ']';
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
  let premise = dest_name + "," + attraction_name;

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

        marker = new google.maps.Marker({
          map: map,
          place: {
            location: results[0].geometry.location,
            query: premise
          },
          animation: google.maps.Animation.DROP,
        });

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

// Reset map center when the destination is added
function resetMapCenter(loc) {
  map.setCenter(loc);
}

// EventListener for trip name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('#trip-info').children('input').blur(function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('tripid'));
  let tripId = $(this).parent().data('tripid');
  let tripName = $(this).val();
  let tripInfo = {'trip_id': tripId,
                  'trip_name': tripName};
  $.post('/update-trip.json', tripInfo, function(results){
    console.log(results);
  });
});

// EventListener for destination name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('.dest-info').children('input').blur(function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('destid'));
  let destId = $(this).parent().data('destid');
  let destName = $(this).val();
  let destInfo = {'dest_id': destId,
                  'dest_name': destName};
  $.post('/update-dest.json', destInfo, function(results){
    console.log(results);
  });
});

// EventListener for attraction name field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur','.attraction-info > input', function(){
  // console.log($(this).val());
  // console.log($(this).parent().data('attractionid'));
  let attractionId = $(this).parent().data('attractionid');
  let attractionName = $(this).val();
  let attractionInfo = {'attraction_id': attractionId,
                        'attraction_name': attractionName};
  $.post('/update-attraction.json', attractionInfo, function(results){
    console.log(results);
  });
});

// EventListener for note content field
// The blur event occurs when an element loses focus. 
// Auto-save to the change to the server
$('body').on('blur','.note-info > input', function(){
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

// /////////////// testing for newly added attraction /////////////////
// // EventListener for attraction name field
// // The blur event occurs when an element loses focus. 
// // Auto-save to the change to the server
// $('body').on('blur','.new-attraction-info input', function(){
//   // console.log('1', $(this));
//   // console.log('2', $(this).val());
//   // console.log('3', $(this).parent());
//   // console.log('3', $(this).parent('.new-attraction-info'));
//   // console.log('4', $(this).parent().data('attractionid'));
//   let attractionId = $(this).parent().data('attractionid');
//   let attractionName = $(this).val();
//   let attractionInfo = {'attraction_id': attractionId,
//                         'attraction_name': attractionName};
//   $.post('/update-attraction.json', attractionInfo, function(results){
//     console.log(results);
//   });
// });


// EventListener when mouse over the input fields, show border to let user know it's editable
$('body').on({
  mouseenter: function(evt) {
    $(this).attr('style', 'border-color: grey');
  }, mouseleave: function(evt) {
    $(this).attr('style', 'border-color: transparent');
  }
}, '.btn-hidden-input-field');

$('.attraction-list').on({
  mouseenter: function(evt) {
    $(this).find('.add-new-attraction :button').show();
  }, mouseleave: function(evt) {
    $(this).find('.add-new-attraction :button').hide();
  }
});


//Delete a dest
function deleteDest(evt){
  let target = $(event.target);
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

$(".btn-delete-dest").on('click', deleteDest);

//Delete a attraction and its note
function deleteAttraction(evt){
  let target = $(event.target);
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
  }
}

$('body').on('click', '.btn-delete-attraction', deleteAttraction);



// modal

function addNewAttractionToRoute(evt) {
  console.log('Hi!!!modal button is clicked');
  // send the new attraction name along with its dest_id
  let destId = $(".modal").data("dest_info").destId;
  let destName = $(".modal").data("dest_info").destName;
  let attraction = {'attraction_name': $("#add-attraction-name").val(),
                    'dest_id': destId,
                    'note': $("#add-note").val()};
  $.post("/new-attraction", attraction, function(results){
    let attraction_name = results.name;
    let attraction_id = results.attraction_id;
    let dest_name = destName;
    let note_id = results.note_id;
    let note = results.note;
    console.log("Added to database", attraction_name);
    addAttractionMarkerByName(dest_name, attraction_id, attraction_name);
    console.log("Found the geocode for:" + results.name);
    // Reset the form value
    $('#add-attraction-name, #add-note').val('');
     let html ="<li class='attraction-info' data-attractionid='" + attraction_id + "'>" +
                  "<button class='btn btn-default btn-xs btn-del-minus-mark btn-delete-attraction' data-attractionid='" + attraction_id + 
                  "' data-attractionname='" + attraction_name + "'> - </button>" +
                  "<input class='btn-hidden-input-field' type='text' value='" + attraction_name + "' size='35'>" +
                    "<div>" +
                      "<ul>" +
                        "<li class='note-info' data-noteid='" + note_id + "'>" +
                          "<input class='btn-hidden-input-field' type='text' value='"+ note + "' size='60'>" +
                        "</li>" +
                      "</ul>" +
                    "</div>" +
                "</li>";

      console.log('html looks like:', html);
      let destSelector = ".dest-info[data-destid='" + destId + "'] .populated-dests";
      $(destSelector).append(html);

  });
}

$('.modal').on('show.bs.modal', function (evt) {
  let button = $(evt.relatedTarget); // Button that triggered the modal
  let destId = button.data('destid'); // Extract info from data-* attributes
  let destName = button.data('destname');

  // Store the data to the modal
  $(".modal").data("dest_info",{
                              destId: destId, 
                              destName: destName
                            });

  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  $('#addNewAttractionModal .modal-title').text('New attraction to: ' + destName);

  // When the save button is clicked, send data to the route
  $('#btn-save-new-attraction').off('click', addNewAttractionToRoute);

  $('#btn-save-new-attraction').on('click', addNewAttractionToRoute);
});

// When the user clicked 'add a new destination' button
// Send request to '/new-dest-id' route with a placeholder-kind dest_name
// When got the trip_id, send request to '/new-attraction' with with a placeholder-kind attraction_name
// Go to the same 'edit-trip' page



