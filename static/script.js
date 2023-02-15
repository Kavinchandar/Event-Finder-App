

const search_button = document.getElementById('search-button');
const clear_button = document.getElementById('clear-button');
const auto_detect = document.getElementById('auto-location');

 //keep location tab closed if screen is refreshed
if (auto_detect.checked) {
    var element= document.getElementById("location");
    element.style.display = "none";
    element.value = ""
}
else{
    var element= document.getElementById("location");
    element.style.display = "block";
    element.value = ""
}

 //location tab closed if checked
auto_detect.addEventListener('click',(e) => {
    if (auto_detect.checked) {
        //hide location when auto detect is checked
        var element= document.getElementById("location");
        element.style.display = "none";
        element.value = ""
    }
    else{
        //show location when auto detect is not checked
        var element = document.getElementById("location");
        element.style.display = "block";
    } 
});


// all async functions

//calls ipinfo api and returns form data to backend
async function handleClick() {
    var keyword = document.getElementById("keyword").value;
    var distance = document.getElementById("distance").value;
    var category = document.getElementById("category").value;
    let location;
    
    //ipinfo api call to get location
    if(auto_detect.checked){
        let response = await fetch('https://ipinfo.io/?token=08d62f3d270fd3',{
            method: 'GET',
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            headers: {
                'Content-Type': 'application/json',
            }
        })
        response = await response.json()
        location = response['loc']
    }else{
        location = document.getElementById("location").value;
    }
    //console.log(keyword,distance,category,location)
    
    //sending form data to backend if form valid
    if(keyword != '' && location != ''){
            //reset all elements before searching a new event
            let response = await fetch(`/allEvents?keyword=${keyword}&radius=${distance}&category=${category}&location=${location}`, {
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                headers: {
                    'Content-Type': 'application/json'
                }
                })
    
                response = await response.json()
                console.log(response);

                //check if return json is valid
                if (jQuery.isEmptyObject(response)){
                    notfound = document.getElementById('not-found')
                    notfound.innerHTML =  `<span class="nope">No Records Found</span>`;
                    //reset table and other elements if exists already
                    clearAllElement(notfound=true);

                }else{
                    head = document.getElementById('table-head')
                    head.innerHTML = `<th>Date</th>
                    <th>Icon</th>
                    <th onclick="sortTableByEvents(2)">Event</th>
                    <th onclick="sortTable(3)">Genre</th>
                    <th onclick="sortTable(4)">Venue</th>`;
                    
                    //reset table for new 
                    body = document.getElementById('table-body');
                    body.innerHTML = ``;
                    
                    const keys =  Object.keys(response).reverse();

                    keys.forEach(x => {
                        Event_id = x;
                    
                        Date = isUndefined(response[x]['Date'])
                        Time = isUndefined(response[x]['Time']) 
                        Icon = isUndefined(response[x]['Icon'][1]['url'])  
                        Event = isUndefined(response[x]['Event'])
                        Genre = isUndefined(response[x]['Genre'])
                        Venue = isUndefined(response[x]['Venue'])
                        
                        
                        body.innerHTML += `
                            <tr class="table-row">
                                <td class='cell date-cell'>
                                    <p>${Date}</p>
                                    <p>${Time}</p>
                                </td>
                                <td class='cell icon-cell'>
                                    <img src='${Icon}' width="100" height="56"></img>
                                </td>
                                <td class='cell event-cell'>
                                    <a href="#my-event-card" onClick="displayDetail('${Event_id}')">${Event}</a>
                                </td>
                                <td class='cell genre-cell'>
                                    ${Genre}
                                </td>
                                <td class='cell venue-cell'>
                                    ${Venue}
                                </td>
                            </tr>
                        `;
                    });
                }
                      
    }
}

async function displayDetail(Event_id){
    console.log(Event_id);
    let response = await fetch(`/eventDetails?event_id=${Event_id}`, {
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                headers: {
                    'Content-Type': 'application/json'
                }
                })
                response = await response.json()
                console.log(response);
                
    Name = response.Name;
    Date = response.Date[0];
    Time = response.Date[1]
    Artist = response.Artist;
    Artist_url = response.Artist_urls;
    Venue = response.Venue;
    Genre = response.Genre;
    Price = response.Prices;
    Ticket = response.Ticket_status;
    Buy = response.Buy_link;
    Seat = response.Seat;
    //console.log(Date,Time,Artist,Artist_url,Venue,Genre,Price,Ticket,Buy,Seat);
            
    card = document.getElementById('my-event-card');
    card.classList.add('glass');

    title = document.getElementById('my-event-title');
    title.innerHTML = `<h1 class='font'>${Name}</h1>`;

    
    info = document.getElementById('my-event-info');
    //reset event card for new event info
    info.innerHTML=``;
    
    if (Date && Time){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Date</h1>
                                <p><span class='font'>${Date} ${Time}</span></p>
                            </div>`;
    }
    if (Artist.length != 0){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class='font'>Artist/Team</h1>    
                                <div id="artists">
                                </div>
                            </div>`;
        n = Artist.length;
        artists = document.getElementById('artists');
        for (i=0; i<n; i++) {
            //console.log(Artist[i],Artist_url[i]);
            artists.innerHTML += `<p><a href="${Artist_url[i]}" target="_blank"><span style='color:aqua;' class='font'>${Artist[i]}</span></a></p>`;
            if (i != n-1){
                artists.innerHTML += '<p style="font-size:20px;" class="font"> | </p>'
            }
        }
        
    }
    if (Venue){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Venue</h1>
                                <p><span class='font'>${Venue}</span></p>
                            </div>`;
    }
    if (Genre){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Genre</h1>
                                <p><span class='font'>${Genre}</span></p>
                            </div>`;
    }
    if (Price){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Price Ranges</h1>
                                <p><span class='font'>${Price}</span></p>
                            </div>`;
    }
    if (Ticket){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Ticket Status</h1>
                                <div id="ticket-status">
                                    <span class='font' style="padding-left:5px;padding-right:5px;">${Ticket}</span>
                                </div>
                            </div>`;

        if (Ticket.valueOf() === "onsale"){
            document.getElementById('ticket-status').style.backgroundColor = 'green';
            document.getElementById('ticket-status').querySelector('span').innerHTML = 'On Sale';
        }
        else if (Ticket.valueOf()=== "offsale"){
            document.getElementById('ticket-status').style.backgroundColor = 'red';
            document.getElementById('ticket-status').querySelector('span').innerHTML = 'Off Sale';
        }
        else if (Ticket.valueOf() === "cancelled"){
            document.getElementById('ticket-status').style.backgroundColor = 'black';
            document.getElementById('ticket-status').querySelector('span').innerHTML = 'Cancelled';
        }
        else if (Ticket.valueOf() === "postponed"){
            document.getElementById('ticket-status').style.backgroundColor = 'orange';
            document.getElementById('ticket-status').querySelector('span').innerHTML = 'Postponed';
        }
        else if (Ticket.valueOf() === "rescheduled"){
            document.getElementById('ticket-status').style.backgroundColor = 'orange';
            document.getElementById('ticket-status').querySelector('span').innerHTML = 'Resheduled';
        }
    }
    if (Buy){
        info.innerHTML += `<div class="event-info-item">
                                <h1 class="font">Buy Ticket At:</h1>
                                <p><span class='font'><a href='${Buy}' style='text-decoration:none; color:aqua;' target="_blank">Ticketmaster</a></span></p>
                            </div>`;
    }
   

    image = document.getElementById('my-event-img');
    image.innerHTML = `<img src='${Seat}' class='seatmap-size'></img>`;
    
    button = document.getElementById('collapse');
    button.innerHTML = `<div class="wrapper">
                            <div>
                                <h1 class="font">Show Venue Details</h1>
                            </div>
                            <div>
                                <a href="#venue-details" onClick="displayVenue('${Venue}')">
                                    <div class="venue-button"></div>  
                                </a>
                            </div>
                        </div>`;

    //reset venue card for new venue info
    document.getElementById('venue-details').innerHTML = ``;

}


async function displayVenue(venue){
    document.getElementById('collapse').innerHTML = '';
    let response = await fetch(`/venueDetails?keyword=${venue}`, {
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                headers: {
                    'Content-Type': 'application/json'
                }
                })
    
                response = await response.json()
                console.log(response);

    address = isUndefined(response.Address);
    city = isUndefined(response.City);
    Name = isUndefined(response.Name);
    postalCode = isUndefined(response.PostalCode);
    upcoming = isUndefined(response.Upcoming_Events);
    image = isUndefined(response.Image);
    console.log(image);
    //<Name of venue>, <street address>, <city>, <state>, <zip code>
    Query = Name +' '+ address +' '+ city +' '+ postalCode
    Query = Query.replace(/ /g,'+')
    Query = Query.replace(',','%2C')
    //console.log(Query);

    venue_details = document.getElementById('venue-details');
    venue_details.innerHTML = `
    <div class="container">
        <div class="venue-card">
            <div class="border">
                <div class='venue-box'>
                    <div class='venue-box-title'>
                        <span class="font">${Name}</span>
                    </div>
                    <div class='venue-box-image'>
                        <image src="${image}" class='venue-size'></image>
                    </div>
                    <div class='special-box'>
                        <div class='venue-box-info address'>
                            <div style="">
                                <span class="font"><strong>Address:</strong></span>
                            </div>
                            <div class="font">${address}
                                <p>${city}</p>
                                <p>${postalCode}</p>
                            </div>
                        </div> 
                        <div class="Map">
                            <a href="https://www.google.com/maps/search/?api=1&query=${Query}" target="_blank"><span class="font" style="color: blue;">Open in google Maps</span></a>
                        </div>                                  
                    </div>
                    <div class='venue-box-next'>
                        <a href="${upcoming}" target="_blank"><span class="font" style="color: blue;">More Events at this Venue</span></a>
                    </div>
                </div>                            
            </div>
        </div>
    </div>`;
}

//buttons
search_button.addEventListener('click', (e) => {
    var keyword = document.getElementById("keyword").value;
    var location = document.getElementById("location").value;
    if(keyword != '' && location != '') {
        e.preventDefault();
    }
    clearAllElement();
    handleClick();
});
    
clear_button.addEventListener('click', (e) => {
    e.preventDefault();
    var element= document.getElementById("location");
    element.style.display = "block";
    element.value = ""
    document.getElementById('my-form').reset();
    clearAllElement();
});


//functions

//function to sort tables by Venue and Genre alphabetically
function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("table-body");
    switching = true;
    dir = "asc"; 
    while (switching) {
      switching = false;
      rows = table.rows;
      for (i = 0; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        if (dir == "asc") {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            shouldSwitch= true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            shouldSwitch = true;
            break;
          }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;      
      } else {
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }

  //function to sort tables by Events alphabetically
  function sortTableByEvents(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("table-body");
    switching = true;
    dir = "asc"; 
    while (switching) {
      switching = false;
      rows = table.rows;
      for (i = 0; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n].getElementsByTagName("a")[0];
        y = rows[i + 1].getElementsByTagName("TD")[n].getElementsByTagName("a")[0];
        if (dir == "asc") {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            shouldSwitch= true;
            break;
          }
        } else if (dir == "desc") {
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            shouldSwitch = true;
            break;
          }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;      
      } else {
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }

//function to clear all elements
function clearAllElement(notfound=false) {
    document.getElementById('table-head').innerHTML = '';
    document.getElementById('table-body').innerHTML = '';
    if(notfound == false) {
        document.getElementById('not-found').innerHTML='';
    }
    document.getElementById('my-event-card').classList.remove('glass');
    document.getElementById('my-event-title').innerHTML = '';
    document.getElementById('my-event-info').innerHTML = '';
    document.getElementById('my-event-img').innerHTML = '';
    document.getElementById('venue-details').innerHTML = '';
    
}

//function to check for Undefined
function isUndefined(val) {
    if(val === 'Undefined'){
        val = '';
    }
    return val;
}