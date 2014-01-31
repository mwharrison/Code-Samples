'''
This is the function I use to get data from the Zillow API, it lives
'''

import xml.etree.ElementTree as ET
import json

from django.http import HttpResponse

import requests
from rentolize.unit.models import Unit
from rentolize.unit.forms import UnitForm
from rentolize.profile.functions import get_or_create_user_profile


def zillow_data(request, address, postcode):
    zillow_api = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz1bb8g6cexhn_4vl2o&address=' + address + '&citystatezip=' + postcode + '&rentzestimate=true'
    zillow_api = zillow_api.replace("#", "")
    r = requests.get(zillow_api)
    root = ET.fromstring(r.content)

    response_data = {}

    try:
        zpid = root.find(".//zpid").text
        response_data['zpid'] = zpid
    except AttributeError:
        zpid = None

    try:
        property_type = root.find(".//useCode").text
        response_data['property_type'] = property_type
    except AttributeError:
        property_type = None

    try:
        tax_year = root.find(".//taxAssessmentYear").text
        response_data['tax_year'] = tax_year
    except AttributeError:
        tax_year = None

    try:
        tax_amount = root.find(".//taxAssessment").text
        response_data['tax_amount'] = tax_amount
    except AttributeError:
        tax_amount = None

    try:
        year_built = root.find(".//yearBuilt").text
        response_data['year_built'] = year_built
    except AttributeError:
        year_built = None

    try:
        sqft = root.find(".//finishedSqFt").text
        response_data['sqft'] = sqft
    except AttributeError:
        sqft = None

    try:
        bathrooms = root.find(".//bathrooms").text
        response_data['bathrooms'] = bathrooms
    except AttributeError:
        bathrooms = None

    try:
        bedrooms = root.find(".//bedrooms").text
        response_data['bedrooms'] = bedrooms
    except AttributeError:
        bedrooms = None

    try:
        total_rooms = root.find(".//totalRooms").text
        response_data['total_rooms'] = total_rooms
    except AttributeError:
        total_rooms = None

    try:
        last_sold = root.find(".//lastSoldDate").text
        response_data['last_sold'] = last_sold
    except AttributeError:
        last_sold = None

    for z in root.findall(".//zestimate"):
        zestimate = z.find('amount').text
        response_data['zestimate'] = zestimate

        zestimate_update = z.find('last-updated').text
        response_data['zestimate_update'] = zestimate_update

    for r in root.findall(".//rentzestimate"):
        rentzestimate = r.find('amount').text
        response_data['rentzestimate'] = rentzestimate

        rentzestimate_update = r.find('last-updated').text
        response_data['rentzestimate_update'] = rentzestimate_update

    return HttpResponse(json.dumps(response_data), content_type="application/json")
