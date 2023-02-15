from flask import Flask,request,jsonify
import urllib.request, json
import keys
from geolib import geohash
import re
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
def hello():
    return app.send_static_file("index.html")

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def check_coordinate(val):
    try:
        lat,long = val.split(',')
        if float(lat) and float(long):
            return True
        else:
            return False
    except:
        return False


def geoCoding(address):
    if check_coordinate(address):
        lat,long = address.split(',')
        return geohash.encode(lat,long,7)
    else:
        address = re.sub("[^a-zA-Z0-9]","+",address)
        url = "https://maps.googleapis.com/maps/api/geocode/json?address="+ address +"&key=" + keys.Geocoding_api_key
        response = urllib.request.urlopen(url)
        data = response.read()
        dict = json.loads(data)
        if dict['results']:
            latitude,longitude = '',''
            latitude = dict.get('results')[0].get('geometry').get('location').get('lat')
            longitude = dict.get('results')[0].get('geometry').get('location').get('lng')
            print(latitude,longitude)
            return geohash.encode(latitude,longitude,7)
        else:
            return False


    
@app.route('/allEvents', methods=['GET'])
@cross_origin(supports_credentials=True)
def getAllEvents():
    args = request.args
    keyword = args.get('keyword')
    keyword = re.sub("[^a-zA-Z0-9]","+",keyword)
    radius = args.get('radius',default='10')
    location = args.get('location')
    category = args.get('category',default='Default')

    segmentID = {'Music': 'KZFzniwnSyZfZ7v7nJ', 'Sports':'KZFzniwnSyZfZ7v7nE', 'Arts':'KZFzniwnSyZfZ7v7na', 'Film':'KZFzniwnSyZfZ7v7nn', 'Miscellanious': 'KZFzniwnSyZfZ7v7n1','Default':''}
    geoPoint = geoCoding(location)
    
    if not geoPoint:
        return {}

    url = "https://app.ticketmaster.com/discovery/v2/events.json?apikey="+ keys.ticketmaster_api_key +"&keyword="+ keyword +"&segmentId="+ segmentID.get(category) +"&radius="+ str(radius) + "&unit=miles&geoPoint="+ geoPoint
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    
    if '_embedded' not in dict:
        return {}

    Data = {}
    Date,Time,Icon,Event,Genre,Venue = '','','','','',''
    count = 0
    if 'events' in dict['_embedded']:
        for event in dict.get('_embedded').get('events'):
            if 'dates' in event and 'start' in event['dates'] and 'localDate' in event['dates']['start']:
                Date = event.get('dates').get('start').get('localDate')
            if 'dates' in event and 'start' in event['dates'] and 'localTime' in event['dates']['start']:
                Time = event.get('dates').get('start').get('localTime')
            if 'images' in event:
                Icon = event.get('images')
            if 'name' in event:
                Event = event.get('name')
            if 'classifications' in event and 'segment' in event['classifications'][0] and 'name' in event['classifications'][0]['segment']:
                Genre = event.get('classifications')[0].get('segment').get('name')
            if '_embedded' in event and 'venues' in event['_embedded'] and 'name' in event['_embedded']['venues'][0]:
                Venue = event.get('_embedded').get('venues')[0].get('name')
            Data[event['id']] = {'Date':Date,'Time':Time,'Icon':Icon,'Event':Event,'Genre':Genre,'Venue':Venue}
            count += 1
            if count > 20:
                break
    return Data

@app.route('/eventDetails', methods=['GET'])
@cross_origin(supports_credentials=True)
def getEventDetails():
    args = request.args
    eventId = args.get('event_id')
    url = "https://app.ticketmaster.com/discovery/v2/events/"+eventId+"?apikey="+keys.ticketmaster_api_key
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    
    Data = {}
    Name,Date,Time,Artist,Venue,Genre,Prices,Ticket_status,Buy_link,Seat_map = '','','',[],'','','','','',''
    Name = dict['name']
    Artist_urls = []
    if 'dates' in dict and 'start' in dict['dates']:
        Date = dict.get('dates').get('start').get('localDate')
        Time = dict.get('dates').get('start').get('localTime')

    if '_embedded' in dict:
        if 'attractions' in dict['_embedded']:
            for event_name in dict.get('_embedded').get('attractions'):
                Artist.append(event_name.get('name'))
                Artist_urls.append(event_name.get('url'))
        if 'venues' in dict['_embedded']:
            Venue = dict.get('_embedded').get('venues')[0].get('name')
    
    if 'classifications' in dict:
        if 'subGenre' in dict['classifications'][0] and 'name' in dict['classifications'][0]['subGenre'] :
            Genre += dict.get('classifications')[0].get('subGenre').get('name') + ' | '
        if 'genre' in dict['classifications'][0] and 'name' in dict['classifications'][0]['genre'] :
            Genre += dict.get('classifications')[0].get('genre').get('name')  + ' | '
        if 'segment' in dict['classifications'][0] and 'name' in dict['classifications'][0 ]['segment'] :
            Genre += dict.get('classifications')[0].get('segment').get('name')  + ' | '
        if 'subType' in dict['classifications'][0] and 'name' in dict['classifications'][0]['subType'] :
            Genre += dict.get('classifications')[0].get('subType').get('name')  + ' | '
        if 'type' in dict['classifications'][0] and 'name' in dict['classifications'][0]['type'] :
            Genre += dict.get('classifications')[0].get('type').get('name')  + ' | '
    
    lst = Genre.split(' | ');
    Genre = ''
    for i in lst :
        if i != 'Undefined' and i != '':
            Genre += i + ' | '
    Genre = Genre[:-3]
    

    if 'priceRanges' in dict:
        Prices = str(dict.get('priceRanges')[0].get('min')) + '-' + str(dict.get('priceRanges')[0].get('max')) + ' USD'
    
    if 'dates' in dict and 'status' in dict['dates']:
        Ticket_status = dict.get('dates').get('status').get('code')
    
    if 'url' in dict:
        Buy_link = dict.get('url')
    
    if 'seatmap' in dict:
        Seat_map = dict.get('seatmap').get('staticUrl')

    Data = {'Name':Name,'Date':(Date,Time), 'Artist':Artist,'Artist_urls':Artist_urls, 'Venue':Venue, 'Genre':Genre, 'Prices':Prices, 'Ticket_status':Ticket_status, 'Buy_link':Buy_link, 'Seat':Seat_map}
    return Data
    

@app.route('/venueDetails', methods=['GET'])
@cross_origin(supports_credentials=True)
def getVenueDetails():
    args = request.args
    keyword = args.get('keyword')
    keyword = keyword.replace(' ', '%20')
    url = "https://app.ticketmaster.com/discovery/v2/venues?apikey="+ keys.ticketmaster_api_key +"&keyword="+keyword
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    Data = {}
    Name,Address,City,PostalCode,Upcoming_Events,Image = '','','','','',''
    if '_embedded' in dict and 'venues' in dict['_embedded']:
        parent = dict['_embedded']['venues'][0]
        if 'name' in parent:
            Name = parent.get('name')
        if 'address' in parent and 'line1' in parent['address']:
            Address = parent.get('address').get('line1')
        if 'city' in parent and 'state' in parent:
            City = parent['city'].get('name') + ' ,' + parent['state'].get('stateCode')
        if 'postalCode' in parent:
            PostalCode = parent['postalCode']
        if 'url' in parent:
            Upcoming_Events = parent['url']
        if 'images' in parent:
            Image = parent['images'][0].get('url')
    
    Data = {'Name':Name,'Image':Image, 'Address':Address, 'City':City, 'PostalCode':PostalCode, 'Upcoming_Events':Upcoming_Events}
    return Data
 

if __name__ == '__main__':
    app.run(debug=True,port="8080")
