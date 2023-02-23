from flask import Flask,request,jsonify
import urllib.request, json
import keys
from geolib import geohash
import re
from flask_cors import CORS, cross_origin
import json
from collections import OrderedDict

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
        address = address.replace(' ','+')
        url = "https://maps.googleapis.com/maps/api/geocode/json?address="+ address +"&key=" + keys.Geocoding_api_key
        response = urllib.request.urlopen(url)
        data = response.read()
        dictionary = json.loads(data)
        if dictionary['results']:
            latitude,longitude = '',''
            latitude = dictionary.get('results')[0].get('geometry').get('location').get('lat')
            longitude = dictionary.get('results')[0].get('geometry').get('location').get('lng')
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
    
    if not radius:
        radius = '10'

    segmentID = {'Music': 'KZFzniwnSyZfZ7v7nJ', 'Sports':'KZFzniwnSyZfZ7v7nE', 'Arts':'KZFzniwnSyZfZ7v7na', 'Film':'KZFzniwnSyZfZ7v7nn', 'Miscellanious': 'KZFzniwnSyZfZ7v7n1','Default':''}
    geoPoint = geoCoding(location)
    if geoPoint == False:
        return {}

    url = "https://app.ticketmaster.com/discovery/v2/events.json?apikey="+ keys.ticketmaster_api_key +"&keyword="+ keyword +"&segmentId="+ segmentID.get(category) +"&radius="+ str(radius) + "&unit=miles&geoPoint="+ geoPoint
    response = urllib.request.urlopen(url)
    data = response.read()
    dictionary = json.loads(data, object_pairs_hook=OrderedDict)
    
    if '_embedded' not in dictionary:
        return {}

    Data = {}
    Date,Time,Icon,Event,Genre,Venue = '','','','','',''
    count = 0
    if 'events' in dictionary['_embedded']:
        for event in dictionary.get('_embedded').get('events'):
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
    dictionary = json.loads(data)
    
    Data = {}
    Name,Date,Time,Artist,Venue,Genre,Prices,Ticket_status,Buy_link,Seat_map = '','','',[],'','','','','',''
    Name = dictionary['name']
    Artist_urls = []
    if 'dates' in dictionary and 'start' in dictionary['dates']:
        Date = dictionary.get('dates').get('start').get('localDate')
        Time = dictionary.get('dates').get('start').get('localTime')

    if '_embedded' in dictionary:
        if 'attractions' in dictionary['_embedded']:
            for event_name in dictionary.get('_embedded').get('attractions'):
                Artist.append(event_name.get('name'))
                Artist_urls.append(event_name.get('url'))
        if 'venues' in dictionary['_embedded']:
            Venue = dictionary.get('_embedded').get('venues')[0].get('name')
    
    if 'classifications' in dictionary:
        if 'subGenre' in dictionary['classifications'][0] and 'name' in dictionary['classifications'][0]['subGenre'] :
            Genre += dictionary.get('classifications')[0].get('subGenre').get('name') + ' | '
        if 'genre' in dictionary['classifications'][0] and 'name' in dictionary['classifications'][0]['genre'] :
            Genre += dictionary.get('classifications')[0].get('genre').get('name')  + ' | '
        if 'segment' in dictionary['classifications'][0] and 'name' in dictionary['classifications'][0 ]['segment'] :
            Genre += dictionary.get('classifications')[0].get('segment').get('name')  + ' | '
        if 'subType' in dictionary['classifications'][0] and 'name' in dictionary['classifications'][0]['subType'] :
            Genre += dictionary.get('classifications')[0].get('subType').get('name')  + ' | '
        if 'type' in dictionary['classifications'][0] and 'name' in dictionary['classifications'][0]['type'] :
            Genre += dictionary.get('classifications')[0].get('type').get('name')  + ' | '
    
    lst = Genre.split(' | ');
    Genre = ''
    for i in lst :
        if i != 'Undefined' and i != '':
            Genre += i + ' | '
    Genre = Genre[:-3]
    

    if 'priceRanges' in dictionary:
        Prices = str(dictionary.get('priceRanges')[0].get('min')) + ' - ' + str(dictionary.get('priceRanges')[0].get('max')) + ' USD'
    
    if 'dates' in dictionary and 'status' in dictionary['dates']:
        Ticket_status = dictionary.get('dates').get('status').get('code')
    
    if 'url' in dictionary:
        Buy_link = dictionary.get('url')
    
    if 'seatmap' in dictionary:
        Seat_map = dictionary.get('seatmap').get('staticUrl')

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
    dictionary = json.loads(data)

    Data = {}
    Name,Address,City,PostalCode,Upcoming_Events,Image = '','','','','',''
    if '_embedded' in dictionary and 'venues' in dictionary['_embedded']:
        parent = dictionary['_embedded']['venues'][0]
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
