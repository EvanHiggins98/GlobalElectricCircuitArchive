# -*- coding: utf-8 -*-



from django.conf.urls import handler400
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import render

import MySQLdb
import time
import io

import requests

from graphos.sources.simple import SimpleDataSource
from graphos.sources.model import ModelDataSource
from graphos.renderers.gchart import LineChart

from django.db.models import IntegerField, DateTimeField, ExpressionWrapper, F, Avg, Max, Min

from django.views.decorators.csrf import csrf_exempt
from background_task import background

from . import structure
from . import models
from . import unitConversions as uC
import super_secrets as secrets
import datetime as dt
from datetime import datetime
from datetime import timedelta

import binascii

from django.http import HttpResponse
from . import MapPoints

# Create your views here.

def kmlFile(request):
  return HttpResponse(MapPoints.kmlFileString(), content_type="text/plain")

def dashboard(request):
  
  mostRecentPacket = models.Packet.objects.order_by('-global_id__transmit_time').select_related('global_id')[0]
  mostRecentIridiumData = mostRecentPacket.global_id
  
  
  mostRecentStatus = models.Status.objects.filter(global_id=mostRecentPacket)[0]
  mostRecentSlowMeasurement = models.SlowMeasurement.objects.filter(global_id=mostRecentPacket)[0]
  mostRecentSupData = models.SupData.objects.filter(global_id=mostRecentPacket)
  
  print("Packet Transmit Time: " + str(mostRecentIridiumData.transmit_time))
  
  modifiedSupData = {}
  for each in mostRecentSupData:
    newTypeString = each.type
    if newTypeString == 'Vbat+':
      newTypeString = 'VbatPlus'
    if newTypeString == 'Vbat-':
      newTypeString = 'VbatMinus'
    if newTypeString == '3.3V_I':
      newTypeString = '3V3_I'
    modifiedSupData[newTypeString] = each
  
  context={'IridiumData': mostRecentIridiumData, 'Packet': mostRecentPacket, 'Status': mostRecentStatus, 'SlowMeasurement': mostRecentSlowMeasurement, 'SupData': modifiedSupData}
  
  return render(request, 'groundstation/dashboard.html', context)
  
def dashboardV6(request):
  formFields = {}
  
  formFields['mcuID'] = {}
  formFields['mcuID']['label'] = 'Selected Packet MCU ID'
  formFields['mcuID']['options'] = ['ANY','1','2','3','4']
  formFields['mcuID']['selected'] = request.GET.get('mcuID', 'ANY')
  
  formFields['IMEI'] = {}
  formFields['IMEI']['label'] = 'Selected Iridium IMEI'
  formFields['IMEI']['options'] = ['ANY', '300234065252710', '300434063219840', '300434063839690', '300434063766960', '300434063560100', '300434063184090', '300434063383330', '300434063185070', '300434063382350', '300234063778640', '888888888888888']
  formFields['IMEI']['selected'] = request.GET.get('IMEI', 'ANY')


  
  mostRecentPacketList = models.PacketV6.objects.order_by('-time').prefetch_related('measurements_set').prefetch_related('measurements_set__child_measurements_units').select_related('parent_transmission').select_related('parent_transmission__parent_request').select_related('parent_transmission')
  filteredMostRecentPacketList = mostRecentPacketList
  if(formFields['mcuID']['selected'] != 'ANY'):
    filteredMostRecentPacketList = mostRecentPacketList.filter(mcu_id=int(formFields['mcuID']['selected']))
  if(formFields['IMEI']['selected'] != 'ANY'):
    filteredMostRecentPacketList = mostRecentPacketList.filter(parent_transmission__imei=int(formFields['IMEI']['selected']))
  #filteredMostRecentPacketList = mostRecentPacketList.filter(parent_transmission__imei=imei_constraint)
  mostRecentPacket = filteredMostRecentPacketList[0]
  mostRecentPacketUnits = None
  try:
    #mostRecentPacketUnits = models.PacketV6Units.objects.filter(parent_packet_v6=mostRecentPacket)[0]
    mostRecentPacketUnits = mostRecentPacket.child_packet_v6_units
  except: 
    mostRecentPacketUnits = mostRecentPacket
  
  mostRecentIridiumTransmission = mostRecentPacket.parent_transmission
  
  mostRecentRequest = mostRecentIridiumTransmission.parent_request
  
  mostRecentMeasurementsList = mostRecentPacket.measurements_set
  mostRecentMeasurementsMin = mostRecentMeasurementsList.aggregate(Min('vert1'),Min('vert2'),Min('vertD'),
                                                                   Min('compassX'),Min('compassY'),Min('compassZ'),
                                                                   Min('horiz1'),Min('horiz2'),Min('horizD')
                                                                   )
  mostRecentMeasurementsAvg = mostRecentMeasurementsList.aggregate(Avg('vert1'),Avg('vert2'),Avg('vertD'),
                                                                   Avg('compassX'),Avg('compassY'),Avg('compassZ'),
                                                                   Avg('horiz1'),Avg('horiz2'),Avg('horizD')
                                                                   )
  mostRecentMeasurementsMax = mostRecentMeasurementsList.aggregate(Max('vert1'),Max('vert2'),Max('vertD'),
                                                                   Max('compassX'),Max('compassY'),Max('compassZ'),
                                                                   Max('horiz1'),Max('horiz2'),Max('horizD')
                                                                   )
  mostRecentMeasurementsUnitsList = [x.child_measurements_units for x in mostRecentPacket.measurements_set.all()]
  mostRecentMeasurementsUnitsMin = mostRecentMeasurementsList.aggregate(Min('child_measurements_units__vert1'),Min('child_measurements_units__vert2'),Min('child_measurements_units__vertD'),
                                                                        Min('child_measurements_units__compassX'),Min('child_measurements_units__compassY'),Min('child_measurements_units__compassZ'),
                                                                        Min('child_measurements_units__horiz1'),Min('child_measurements_units__horiz2'),Min('child_measurements_units__horizD')
                                                                        )
  mostRecentMeasurementsUnitsAvg = mostRecentMeasurementsList.aggregate(Avg('child_measurements_units__vert1'),Avg('child_measurements_units__vert2'),Avg('child_measurements_units__vertD'),
                                                                        Avg('child_measurements_units__compassX'),Avg('child_measurements_units__compassY'),Avg('child_measurements_units__compassZ'),
                                                                        Avg('child_measurements_units__horiz1'),Avg('child_measurements_units__horiz2'),Avg('child_measurements_units__horizD')
                                                                        )
  mostRecentMeasurementsUnitsMax = mostRecentMeasurementsList.aggregate(Max('child_measurements_units__vert1'),Max('child_measurements_units__vert2'),Max('child_measurements_units__vertD'),
                                                                        Max('child_measurements_units__compassX'),Max('child_measurements_units__compassY'),Max('child_measurements_units__compassZ'),
                                                                        Max('child_measurements_units__horiz1'),Max('child_measurements_units__horiz2'),Max('child_measurements_units__horizD')
                                                                        )

  context={
           'FormFields': formFields,
           'Request': mostRecentRequest,
           'Transmission': mostRecentIridiumTransmission,
           'Packet': mostRecentPacket,
           'PacketUnits': mostRecentPacketUnits,
           'Measurements': {
                            'Min': mostRecentMeasurementsMin,
                            'Avg': mostRecentMeasurementsAvg,
                            'Max': mostRecentMeasurementsMax
                            },
           'MeasurementsUnits': {
                            'Min': mostRecentMeasurementsUnitsMin,
                            'Avg': mostRecentMeasurementsUnitsAvg,
                            'Max': mostRecentMeasurementsUnitsMax
                            }
           }
  
  return render(request, 'groundstation/dashboardV6.html', context)

def greyBalloon(request):
  return render(request, 'groundstation/GreyBalloon.png', content_type='image/png')
def redBalloon(request):
  return render(request, 'groundstation/RedBalloon.png', content_type='image/png')
def greyBalloonClicked(request):
  return render(request, 'groundstation/GreyBalloonClicked.png', content_type='image/png')
def redBalloonClicked(request):
  return render(request, 'groundstation/RedBalloonClicked.png', content_type='image/png')

def utf8js(request):
  return render(request, 'groundstation/utf8.js')
  
def theBest(request):
  return render(request, 'groundstation/TheBest.json')

def homepage(request):
  imei_list = ['None', '300234065252710', '300434063219840', '300434063839690', '300434063766960', '300434063560100', '300434063184090', '300434063383330', '300434063185070', '300434063382350', '300234063778640', '888888888888888']
  id_list = ['None', '1','2','3','4']
  context = {'serverType': secrets.serverType, 'currentTimeString': datetime.utcnow().strftime("%y-%m-%dT%H:%M:%S"), 'imei_list': imei_list,'id_list':id_list}
  return render(request, 'groundstation/homepage.html', context)

def gps(request):    # Change to google maps
  data = [
        ['Time', 'Latitude', 'Longitude']  # create a list to hold the column names and data for the axis names
       ]
  
  db = MySQLdb.connect(host="localhost", user=secrets.sqluser,passwd=secrets.sqlpassword, db="groundstation") # Access the database to get all the current data
  cur = db.cursor()
  cur.execute('SELECT i.transmit_time,d.gps_latitude,d.gps_longitude,gps_altitude FROM groundstation.groundstationapp_slowmeasurement AS d INNER JOIN groundstationapp_iridiumdata AS i on i.global_id_id = d.global_id_id' )
  for row in cur.fetchall(): # going through each row
    l = []
    l.append(row[0]) # append each row to the data, only get the columns that we want
    l.append(row[1])
    l.append(row[2])
    data.append(l)
    
  db.close()
  data_source = SimpleDataSource(data=data)
  chart = LineChart(data_source, options={'title': "Coordinates", 'pointSize': 20}) # Creating a line chart
  
  context = {'chart': chart}
  return render(request, 'groundstation/gps.html', context) # rendering the chart when a request has gone through for this page, and using the mapPlot.html to render it
  
@csrf_exempt
def dumpfunc(request):
  minPack = request.GET.get('minPack', '1')
  maxPack = request.GET.get('maxPack', '517')
  totalPack = int(request.GET.get('totalPack', '0'))
  reverseOrder = request.GET.get('reverse', 'False')
  binary = request.GET.get('binary', 'False')
  
  packetList = []
  
  sortOrder = 'global_id__global_id__id'
  if(reverseOrder == 'True'):
    sortOrder = '-global_id__global_id__id'
  
  
  ordered_raw_packets = models.RawData.objects
  if(totalPack == 0):
    ordered_raw_packets = ordered_raw_packets.filter(global_id__global_id__id__gte=minPack).filter(global_id__global_id__id__lte=maxPack).order_by(sortOrder)
  else:
    ordered_raw_packets = ordered_raw_packets.order_by(sortOrder)[:totalPack]
  
  if(binary == 'False'):
      for x in ordered_raw_packets:
        packet = {
        "imei": str(x.global_id.global_id.imei),
        "momsn": str(x.global_id.global_id.momsn),
        "transmit_time": (x.global_id.global_id.transmit_time).strftime("%y-%m-%d %H:%M:%S"),
        "iridium_latitude": str(x.global_id.global_id.iridium_latitude),
        "iridium_longitude": str(x.global_id.global_id.iridium_longitude),
        "iridium_cep": str(x.global_id.global_id.iridium_cep),
        "data": str(x.hexdata)
        }
        packetList.append(packet)
  elif(binary == 'True'):
    for x in ordered_raw_packets:
      packetList.append(x.hexdata)
   
  context = {'packetList': packetList, 'binary': binary}
  return render(request, 'groundstation/dump.json', context)
    
@csrf_exempt
def scrapefunc(request):
  minPack = request.GET.get('minPack', '1')
  maxPack = request.GET.get('maxPack', '517')
  scrapeURL = request.GET.get('scrapeURL', 'https://gec.codyanderson.net/dump.json')
  
  context = {
  "minPack" : minPack,
  "maxPack" : maxPack,
  "scrapeURL" : scrapeURL
  }
  
  return render(request, 'groundstation/scrape.html', context)


@csrf_exempt
def submitfunc(request):
  if request.method == 'POST':
    password = request.POST.get('password', '')
    imei = request.POST.get('imei', '')
    message = request.POST.get('message', '')
    messageEncoded = binascii.hexlify(bytearray(message,'utf-8'))
    if(imei == 'Flightboard2'):
      imei = '300434063185070'
    context={
      'serverType': secrets.serverType,
      'imei': imei,
    }
    print("IMEI: " + imei)
    print("MESSAGE: " + message)
    print("MESSAGE_ENCODED: " + str(messageEncoded))
    headers = {"Accept": "text/plain"}
    postData = {
      'imei': imei,
      'data': messageEncoded,
      'username': secrets.rock7username,
      'password': secrets.rock7password
    }
    
    r = None
    if(imei != '' and password == secrets.commandPassword):
      r = requests.post("https://core.rock7.com/rockblock/MT", headers=headers, data=postData)
      print(r.status_code)
      print(r.content)
      models.UplinkRequest.objects.create(imei = imei, time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), password=password,message=message, success=True)
      return JsonResponse({'status': r.status_code, 'time': datetime.utcnow().strftime("%B %d, %Y %I:%M %p UTC"), 'imei': imei, 'message': message})
    else:
      models.UplinkRequest.objects.create(imei = imei, time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), password=password,message=message, success=False)
      return JsonResponse({'status': 403, 'time': datetime.utcnow().strftime("%B %d, %Y %I:%M %p UTC"), 'imei': imei, 'message': message})
    
  else:
    password = request.GET.get('password', '')
    imei = request.GET.get('imei', '')
    message = request.GET.get('message', '')
    messageEncoded = bytearray(message, 'utf-8')
    if(imei == 'Flightboard2'):
      imei = '300434063185070'
    
    context={
    'serverType': secrets.serverType,
    'imei': imei,
    }
    print("IMEI: " + imei)
    print("MESSAGE: " + message)
    print("MESSAGE_ENCODED" + messageEncoded)
    headers = {"Accept": "text/plain"}
    postData = {
    'imei': imei,
    'data': message,
    'username': secrets.rock7username,
    'password': secrets.rock7password
    }
    if(imei != '' and password == secrets.commandPassword):
      r = requests.post("https://core.rock7.com/rockblock/MT", headers=headers, data=postData)
      print(r.status_code)
      print(r.content)
    return render(request, 'groundstation/submit.html', context)


@csrf_exempt
def fastPost(request):
  context = {'text': ''}
  print(("----"*4) + "BEGIN FASTPOST" + ("----"*4))
  if (request.POST):
    context = {'text': 'POST'}#Data}
  elif (request.GET):
    context = {'text': 'get'}
  else:
    context = {'text': 'none'}
    
  requestedRequest = {}
  requestedRequest["request.POST"] = True if request.POST else False
  requestedRequest["request.GET"] = True if request.GET else False
  requestedRequest["request.POST.get('data')"] = request.POST.get('data')
  requestedRequest["request.POST.get('transmit_time')"] = request.POST.get('transmit_time')
  requestedRequest["request.POST.get('imei')"] = request.POST.get('imei')
  requestedRequest["request.POST.get('momsn')"] = request.POST.get('momsn')
  
  requestedRequest["request.POST.get('iridium_latitude')"] = request.POST.get('iridium_latitude')
  requestedRequest["request.POST.get('iridium_longitude')"] = request.POST.get('iridium_longitude')
  requestedRequest["request.POST.get('iridium_cep')"] = request.POST.get('iridium_cep')
  requestedRequest["request.POST.get('transmitted_via_satellite')"] = request.POST.get('transmitted_via_satellite')
  
  requestedRequest["request.META.get('HTTP_X_FORWARDED_FOR')"] = request.META.get('HTTP_X_FORWARDED_FOR')   
  requestedRequest["request.META.get('HTTP_X_FORWARDED_HOST')"] = request.META.get('HTTP_X_FORWARDED_HOST')  
  requestedRequest["request.META.get('HTTP_X_FORWARDED_SERVER')"] = request.META.get('HTTP_X_FORWARDED_SERVER')
  requestedRequest["request.META.get('REMOTE_ADDR')"] = request.META.get('REMOTE_ADDR')            

    
  postfuncV6(requestedRequest)
  print(("----"*4) + "-END FASTPOST-" + ("----"*4))
  return render(request, 'groundstation/post.html', context)
  
@background(schedule=10)
def postfunc(requestedRequest):
  context = {'text': 'none'}
  try:
    if (requestedRequest["request.POST"]):
      packet_data = requestedRequest["request.POST.get('data')"]
      #if data exists
      if (packet_data is not None):
        if (True or (packet_data[0:2].upper() in ['00','01','02','03','04','05','06','07','08','FF','FE','FD','FC','FB','FA','F9','F8','F7'])):
          binary_packet_data = binascii.unhexlify(packet_data)
          packet_fields = structure.unpack_new(binary_packet_data)
          print(packet_fields['seq'])
          print(packet_fields['version'])
          datetimeString = datetime.strptime(requestedRequest["request.POST.get('transmit_time')"],"%y-%m-%d %H:%M:%S")
          filteredImei = requestedRequest["request.POST.get('imei')"]
          if(filteredImei == "CollinsLaptop"):
            filteredImei = "888888888888888"
          new_IridiumData = models.IridiumData.objects.create(transmit_time = datetimeString, iridium_latitude = requestedRequest["request.POST.get('iridium_latitude')"], iridium_longitude = requestedRequest["request.POST.get('iridium_longitude')"], iridium_cep = requestedRequest["request.POST.get('iridium_cep')"], momsn = requestedRequest["request.POST.get('momsn')"], imei = filteredImei, transmitted_via_satellite = True if requestedRequest["request.POST.get('transmitted_via_satellite')"] is None else requestedRequest["request.POST.get('transmitted_via_satellite')"])
          print(new_IridiumData.transmit_time)
          new_Packet = models.Packet.objects.create(global_id=new_IridiumData,packet_id=packet_fields['seq'],version=packet_fields['version'])
          new_RawData = models.RawData.objects.create(global_id=new_Packet,data=binary_packet_data,hexdata=packet_data)
          try:
            time_now = datetime.fromtimestamp(packet_fields['time'])
            
            cond_time_now = datetime.fromtimestamp(packet_fields['cond_time'])
            
            
            
            new_SlowMeasurement = models.SlowMeasurement.objects.create(global_id=new_Packet,gps_latitude=packet_fields['lat'],gps_longitude=packet_fields['lon'],gps_altitude=packet_fields['alt'],gps_time=time_now,cond_gps_time=cond_time_now)
            for i in range(0,12):
              new_FastMeasurement = models.FastMeasurement.objects.create(global_id=new_Packet,sub_id=i,vert1=packet_fields['vert1'][i],vert2=packet_fields['vert2'][i],vertD=packet_fields['vertD'][i],compassX=packet_fields['compassX'][i],compassY=packet_fields['compassY'][i],compassZ=packet_fields['compassZ'][i],horiz1=packet_fields['horiz1'][i],horiz2=packet_fields['horiz2'][i],horizD=packet_fields['horizD'][i])
            for i in range(0,15):
              new_ConductivityData = models.ConductivityData.objects.create(global_id=new_SlowMeasurement,sub_id=i*10+(packet_fields['seq']%10),vert1=packet_fields['cVert1'][i],vert2=packet_fields['cVert2'][i])
            labelList=["Temperature","Temperature","Pressure","Pressure","IL0","IL1","IL2","IH0","IH1","IH2","T0","T1","T2","Tmag","Tadc1","Tadc2","Text","TRB","UNUSED0","UNUSED1"]
            newSupDataList = []
            for fieldName in packet_fields['sup']:
              print('Fieldname: ' + str(fieldName))
              print('Value    : ' + str(packet_fields['sup'][fieldName]))
              newSupData = models.SupData.objects.create(global_id=new_Packet,sub_id=0 ,type=fieldName, value=packet_fields['sup'][fieldName])
              newSupDataList.append(newSupData)
            newTermstatData= models.Status.objects.create(global_id=new_Packet,yikes=packet_fields['yikes'],ballast=packet_fields['ballast'],cutdown=packet_fields['cutdown'])
          except Exception as err:
            print("\n\nTHERE WAS AN ERROR READING IN THE PACKET")
            print(str(err) + "\n\n")
          
  
        else:
          binary_packet_data = binascii.unhexlify(packet_data)
          packet_fields = structure.unpack_new(binary_packet_data)
          print(packet_fields['seq'])
          print(packet_fields['version'])
          datetimeString = datetime.strptime(requestedRequest["request.POST.get('transmit_time')"],"%y-%m-%d %H:%M:%S")
          filteredImei = requestedRequest["request.POST.get('imei')"]
          if(filteredImei == "CollinsLaptop"):
            filteredImei = "888888888888888"
          new_IridiumData = models.IridiumData.objects.create(transmit_time = datetimeString, iridium_latitude = requestedRequest["request.POST.get('iridium_latitude')"], iridium_longitude = requestedRequest["request.POST.get('iridium_longitude')"], iridium_cep = requestedRequest["request.POST.get('iridium_cep')"], momsn = requestedRequest["request.POST.get('momsn')"], imei = filteredImei, transmitted_via_satellite = True if requestedRequest["request.POST.get('transmitted_via_satellite')"] is None else requestedRequest["request.POST.get('transmitted_via_satellite')"])
          print(new_IridiumData.transmit_time)
          new_Packet = models.Packet.objects.create(global_id=new_IridiumData,packet_id=packet_fields['seq'],version=packet_fields['version'])
          new_RawData = models.RawData.objects.create(global_id=new_Packet,data=binary_packet_data,hexdata=packet_data)
      else:
        new_IridiumData = models.IridiumData.objects.create(transmit_time = datetimeString, iridium_latitude = requestedRequest["request.POST.get('iridium_latitude')"], iridium_longitude = requestedRequest["request.POST.get('iridium_longitude')"], iridium_cep = requestedRequest["request.POST.get('iridium_cep')"], momsn = requestedRequest["request.POST.get('momsn')"], imei = filteredImei, transmitted_via_satellite = True if requestedRequest["request.POST.get('transmitted_via_satellite')"] is None else requestedRequest["request.POST.get('transmitted_via_satellite')"])
        print(new_IridiumData.transmit_time)
          
      iridium_txtime = requestedRequest["request.POST.get('transmit_time')"]
      iridium_imei = requestedRequest["request.POST.get('imei')"]
      iridium_momsn = requestedRequest["request.POST.get('momsn')"]
      iridium_latitude = requestedRequest["request.POST.get('iridium_latitude')"]
      iridium_longitude = requestedRequest["request.POST.get('iridium_longitude')"]
      iridium_cep = requestedRequest["request.POST.get('iridium_cep')"]
      Data={'data':packet_data,'txtime':iridium_txtime,'imei':iridium_imei,'momsn':iridium_momsn,'lat':iridium_latitude,'lon':iridium_longitude,'cep':iridium_cep}
      
      print(packet_fields)
      context = {'text': Data}
    elif (requestedRequest["request.GET"]):
      context = {'text': 'get'}
    else:
      context = {'text': 'none'}
  except Exception as err:
    print("THERE WAS AN UH_OH ON A PRETTY BIG SCALE IN THIS CASE...")
    print(str(err))
  try:
    print('Proccessing the packet with the V6 parser.')
    postfuncV6(requestedRequest)
  except Exception as err:
    print("Whoops, looks like the new parsing function malfunctioned.")
    print(str(err))    
    
    
    
    
    
    
    
    
    
    
   
    
    
    
    
    
    
    
    
  
@background(schedule=10)
def postfuncV6(requestedRequest):
  if (requestedRequest["request.POST"]):
    
    #Build request object
    requestObject = models.Request.objects.create(time = datetime.utcnow(), forwarded_for_address = str(requestedRequest["request.META.get('HTTP_X_FORWARDED_FOR')"]), forwarded_host_address = str(requestedRequest["request.META.get('HTTP_X_FORWARDED_HOST')"]), forwarded_server_address = str(requestedRequest["request.META.get('HTTP_X_FORWARDED_SERVER')"]), remote_address = str(requestedRequest["request.META.get('REMOTE_ADDR')"]))
    print('Successfully created the request object.')
    
    #Build transmission object
    iridiumTime = datetime.strptime(requestedRequest["request.POST.get('transmit_time')"],"%y-%m-%d %H:%M:%S")
    iridiumLatitude = requestedRequest["request.POST.get('iridium_latitude')"]
    iridiumLongitude = requestedRequest["request.POST.get('iridium_longitude')"]
    iridiumCep = requestedRequest["request.POST.get('iridium_cep')"]
    iridiumMomsn = requestedRequest["request.POST.get('momsn')"]
    iridiumImei = requestedRequest["request.POST.get('imei')"]
    if(iridiumImei == "CollinsLaptop"):
      iridiumImei = "888888888888888"
    transViaSat = True if requestedRequest["request.POST.get('transmitted_via_satellite')"] is None else requestedRequest["request.POST.get('transmitted_via_satellite')"]
    transmissonObject = models.IridiumTransmission.objects.create( parent_request = requestObject, time = iridiumTime, latitude = iridiumLatitude, longitude = iridiumLongitude, cep = iridiumCep, momsn = iridiumMomsn, imei = iridiumImei, transmitted_via_satellite = transViaSat)
    print('Successfully created the transmission object.')
    
    #Build raw packet object
    hexRawPacketData = requestedRequest["request.POST.get('data')"]
    if(hexRawPacketData == None or hexRawPacketData == ''):
      print("No Payload Data")
      return
    binRawPacketData = binascii.unhexlify(hexRawPacketData)
    rawPacketObject = models.RawPacket.objects.create(parent_transmission = transmissonObject, data = binRawPacketData, hexdata = hexRawPacketData)
    print('Successfully created the raw packet object.')
    
    #Build packet object
    packetValues = structure.unpackV6(binRawPacketData)
    packetObject = models.PacketV6.objects.create(
                                                  parent_transmission = transmissonObject,
                                                  yikes_status = packetValues["yikes_status"],
                                                  mcu_id = packetValues["mcu_id"],
                                                  version = packetValues["version"],
                                                  sequence_id = packetValues["sequence_id"],
                                                  time = datetime.fromtimestamp(packetValues["time"]),
                                                  latitude = packetValues["latitude"],
                                                  longitude = packetValues["longitude"],
                                                  altitude = packetValues["altitude"],
                                                  ballast_status = packetValues["ballast_status"],
                                                  cutdown_status = packetValues["cutdown_status"],
                                                  conductivity_time = datetime.fromtimestamp(packetValues["conductivity_time"]),
                                                  satellites_count = packetValues["satellites_count"],
                                                  rockblock_signal_strength = packetValues["rockblock_signal_strength"],
                                                  commands_count = packetValues["commands_count"],
                                                  altimeter_temp = packetValues["altimeter_temp"],
                                                  altimeter_pressure = packetValues["altimeter_pressure"],
                                                  positive_7v_battery_voltage = packetValues["positive_7v_battery_voltage"],
                                                  negative_7v_battery_voltage = packetValues["negative_7v_battery_voltage"],
                                                  positive_3v6_battery_voltage = packetValues["positive_3v6_battery_voltage"],
                                                  current_draw_7v_rail = packetValues["current_draw_7v_rail"],
                                                  current_draw_3v3_rail = packetValues["current_draw_3v3_rail"],
                                                  battery_temp = packetValues["battery_temp"],
                                                  mcu_temp = packetValues["mcu_temp"],
                                                  compass_temp = packetValues["compass_temp"],
                                                  adc1_temp = packetValues["adc1_temp"],
                                                  adc2_temp = packetValues["adc2_temp"],
                                                  external_temp = packetValues["external_temp"],
                                                  rockblock_temp = packetValues["rockblock_temp"]
                                                  )
    print('Successfully created the packet object.')
    
    packetUnitsObject = models.PacketV6Units.objects.create(
                                                  parent_packet_v6 = packetObject,
                                                  yikes_status = uC.yikes_status_conv(packetValues["yikes_status"]),
                                                  mcu_id = uC.mcu_id_conv(packetValues["mcu_id"]),
                                                  version = uC.version_conv(packetValues["version"]),
                                                  sequence_id = uC.sequence_id_conv(packetValues["sequence_id"]),
                                                  time = datetime.fromtimestamp(packetValues["time"]),
                                                  latitude = uC.lat_lon_conv(packetValues["latitude"]),
                                                  longitude = uC.lat_lon_conv(packetValues["longitude"]),
                                                  altitude = uC.altitude_conv(packetValues["altitude"]),
                                                  ballast_status = uC.ballast_status_conv(packetValues["ballast_status"]),
                                                  cutdown_status = uC.cutdown_status_conv(packetValues["cutdown_status"]),
                                                  conductivity_time = datetime.fromtimestamp(packetValues["conductivity_time"]),
                                                  satellites_count = packetValues["satellites_count"],
                                                  rockblock_signal_strength = packetValues["rockblock_signal_strength"],
                                                  commands_count = packetValues["commands_count"],
                                                  altimeter_temp = uC.altimeter_temp_conv_C(packetValues["altimeter_temp"]),
                                                  altimeter_pressure = uC.altimeter_pressure_conv(packetValues["altimeter_pressure"]),
                                                  positive_7v_battery_voltage = uC.positive_7v_battery_voltage_conv(packetValues["positive_7v_battery_voltage"]),
                                                  negative_7v_battery_voltage = uC.negative_7v_battery_voltage_conv(packetValues["negative_7v_battery_voltage"]),
                                                  positive_3v6_battery_voltage = uC.positive_3v6_battery_voltage_conv(packetValues["positive_3v6_battery_voltage"]),
                                                  current_draw_7v_rail = uC.current_draw_7v_rail_conv(packetValues["current_draw_7v_rail"]),
                                                  current_draw_3v3_rail = uC.current_draw_3v3_rail_conv(packetValues["current_draw_3v3_rail"]),
                                                  battery_temp = uC.backplane_temp_conv_C(packetValues["battery_temp"]),
                                                  mcu_temp = uC.backplane_temp_conv_C(packetValues["mcu_temp"]),
                                                  compass_temp = uC.compass_temp_conv_C(packetValues["compass_temp"]),
                                                  adc1_temp = uC.adc_temp_conv_C(packetValues["adc1_temp"]),
                                                  adc2_temp = uC.adc_temp_conv_C(packetValues["adc2_temp"]),
                                                  external_temp = uC.harness_temp_conv_C(packetValues["external_temp"]),
                                                  rockblock_temp = uC.harness_temp_conv_C(packetValues["rockblock_temp"])
                                                  )
    print('Successfully created the packet units object.')
                                                  
    #Build measurement objects
    measurementObjectList = []
    for each in range(12):
      parent_packet = packetObject
      measurementTime = datetime.fromtimestamp(packetValues["time"]) + (each*timedelta(seconds=5))
      measurementVert1 = packetValues["vert1"][each]
      measurementVert2 = packetValues["vert2"][each]
      measurementVertD = packetValues["vertD"][each]
      measurementCompassX = packetValues["compassX"][each]
      measurementCompassY = packetValues["compassY"][each]
      measurementCompassZ = packetValues["compassZ"][each]
      measurementHoriz1 = packetValues["horiz1"][each]
      measurementHoriz2 = packetValues["horiz2"][each]
      measurementHorizD = packetValues["horizD"][each]
      measurementObject = models.Measurements.objects.create(parent_packet = parent_packet, time = measurementTime, vert1 = measurementVert1, vert2 = measurementVert2, vertD = measurementVertD, horiz1 = measurementHoriz1, horiz2 = measurementHoriz2, horizD = measurementHorizD, compassX = measurementCompassX, compassY = measurementCompassY, compassZ = measurementCompassZ)
      measurementObjectList.append(measurementObject)
      print('Successfully created ' + str(each+1) + '/12 measurement object(s).')
    print('Successfully created ALL measurement object(s).')
                                                  
    #Build measurement units objects
    measurementUnitsObjectList = []
    for each in range(12):
      parent_measurements = measurementObjectList[each]
      measurementUnitsTime = datetime.fromtimestamp(packetValues["time"]) + (each*timedelta(seconds=5))
      measurementUnitsVert1 = uC.adc_conv(packetValues["vert1"][each])
      measurementUnitsVert2 = uC.adc_conv(packetValues["vert2"][each])
      measurementUnitsVertD = uC.adc_conv(packetValues["vertD"][each])
      measurementUnitsCompassX = packetValues["compassX"][each]
      measurementUnitsCompassY = packetValues["compassY"][each]
      measurementUnitsCompassZ = packetValues["compassZ"][each]
      measurementUnitsHoriz1 = uC.adc_conv(packetValues["horiz1"][each])
      measurementUnitsHoriz2 = uC.adc_conv(packetValues["horiz2"][each])
      measurementUnitsHorizD = uC.adc_conv(packetValues["horizD"][each])
      measurementUnitsObject = models.MeasurementsUnits.objects.create(parent_measurements = parent_measurements, time = measurementUnitsTime, vert1 = measurementUnitsVert1, vert2 = measurementUnitsVert2, vertD = measurementUnitsVertD, horiz1 = measurementUnitsHoriz1, horiz2 = measurementUnitsHoriz2, horizD = measurementUnitsHorizD, compassX = measurementUnitsCompassX, compassY = measurementUnitsCompassY, compassZ = measurementUnitsCompassZ)
      measurementUnitsObjectList.append(measurementUnitsObject)
      print('Successfully created ' + str(each+1) + '/12 measurement units object(s).')
    print('Successfully created ALL measurement units object(s).')
    
    #Build conductivity measurement objects
    conductivityMeasurementObjectList = []
    for each in range(15):
      parent_packet = packetObject
      conductivityMeasurementTime = datetime.fromtimestamp(packetValues["conductivity_time"]) + ((each*10)+(packetValues["sequence_id"]%10))*timedelta(seconds=0.1)
      conductivityMeasurementVert1 = packetValues["conductivity_vert1"][each]
      conductivityMeasurementVert2 = packetValues["conductivity_vert2"][each]
      conductivityMeasurementObject = models.ConductivityMeasurements.objects.create(parent_packet = parent_packet, time = conductivityMeasurementTime, vert1 = conductivityMeasurementVert1, vert2 = conductivityMeasurementVert2)
      conductivityMeasurementObjectList.append(conductivityMeasurementObject)
      print('Successfully created ' + str(each+1) + '/15 conductivity measurement object(s).')
    print('Successfully created ALL conductivity measurement object(s).')
    
    #Build conductivity measurement units objects
    conductivityMeasurementUnitsObjectList = []
    for each in range(15):
      parent_conductivity_measurements = conductivityMeasurementObjectList[each]
      conductivityMeasurementUnitsTime = datetime.fromtimestamp(packetValues["conductivity_time"]) + ((each*10)+(packetValues["sequence_id"]%10))*timedelta(seconds=0.1)
      conductivityMeasurementUnitsVert1 = uC.adc_conv(packetValues["conductivity_vert1"][each])
      conductivityMeasurementUnitsVert2 = uC.adc_conv(packetValues["conductivity_vert2"][each])
      conductivityMeasurementUnitsObject = models.ConductivityMeasurementsUnits.objects.create(parent_conductivity_measurements = parent_conductivity_measurements, time = conductivityMeasurementUnitsTime, vert1 = conductivityMeasurementUnitsVert1, vert2 = conductivityMeasurementUnitsVert2)
      conductivityMeasurementUnitsObjectList.append(conductivityMeasurementUnitsObject)
      print('Successfully created ' + str(each+1) + '/15 conductivity measurement units object(s).')
    print('Successfully created ALL conductivity measurement units object(s).')
    
  else:
    errorMessage = "This was NOT a POST request. Please try again with a POST request."
    print(errorMessage)
    return #render(request, 'groundstation/post.html', {'text': errorMessage})
  return #render(request, 'groundstation/post.html', {'text': 'None'})
  
def horizontal(request):
  data = [
        ['Time', 'H1', 'H2', 'HD']   # create a list to hold the column names and data for the axis names
      ]
  minstringint = datetime.strptime(request.GET.get('min','2000-04-01T10:00:00'),"%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
  maxstringint = datetime.strptime(request.GET.get('max','2020-05-16T10:00:00'),"%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
  ordered_fastmeasurements = models.FastMeasurement.objects.filter(global_id__global_id__transmit_time__gte=minstringint).filter(global_id__global_id__transmit_time__lte=maxstringint).order_by('global_id', 'sub_id')
  #print(ordered_fastmeasurements.query)
  scalar = 0.000125 if request.GET.get('volts','') == 'True' else 1
  top = 99999 if not request.GET.get('top','') else float(request.GET.get('top',''))
  bottom = -99999 if not request.GET.get('bottom','') else float(request.GET.get('bottom',''))
  onlyWantedData = []
  wantedimei = request.GET.get('imei','*')
  if(wantedimei == "CollinsLaptop"):
    wantedimei = "888888888888888"
  for x in ordered_fastmeasurements:
    if(wantedimei == '*' or wantedimei == str(x.global_id.global_id.imei)):
      onlyWantedData.append([x.global_id.global_id.transmit_time+x.sub_id*timedelta(seconds=5),x.horiz1*scalar if x.horiz1*scalar <= top and x.horiz1*scalar >= bottom else top if x.horiz1*scalar > top else bottom,x.horiz2*scalar if x.horiz2*scalar <= top and x.horiz2*scalar >= bottom else top if x.horiz2*scalar > top else bottom,x.horizD*scalar if x.horizD*scalar <= top and x.horizD*scalar >= bottom else top if x.horizD*scalar > top else bottom])
  
  onlyReallyWantedData = []
  for x in onlyWantedData:
    if True: #if(x[0] >= minstringint and x[0] <= maxstringint):
      onlyReallyWantedData.append(x)
  data = data + onlyReallyWantedData
  
  chartTitle = "Horizontal Measurements"
  chartDescription = "This is a test graph generated from all of the fast measurement data.\n This is mostly for demonstration.\n Please enjoy."
  
  data_source = SimpleDataSource(data=data)
  chart = LineChart(data_source, options={'title': chartTitle, 'pointSize': 20}) # Creating a line chart
  
  context = {'chart': chart, 'title': chartTitle, 'description': chartDescription}

  return render(request, 'groundstation/graph.html', context)
  
def vertical(request):
  data = [
        ['Time', 'V1', 'V2', 'VD']   # create a list to hold the column names and data for the axis names
      ]
  minstringint = datetime.strptime(request.GET.get('min','2000-01-01T10:00:00'),"%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
  maxstringint = datetime.strptime(request.GET.get('max','2020-12-25T10:00:00'),"%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
  ordered_fastmeasurements = models.FastMeasurement.objects.filter(global_id__global_id__transmit_time__gte=minstringint).filter(global_id__global_id__transmit_time__lte=maxstringint).order_by('global_id', 'sub_id')
  #print(len(ordered_fastmeasurements))
  scalar = 0.000125 if request.GET.get('volts','') == 'True' else 1
  top = 99999 if not request.GET.get('top','') else float(request.GET.get('top',''))
  bottom = -99999 if not request.GET.get('bottom','') else float(request.GET.get('bottom',''))
  onlyWantedData = []
  wantedimei = request.GET.get('imei','*')
  if(wantedimei == "CollinsLaptop"):
    wantedimei = "888888888888888"
  for x in ordered_fastmeasurements:
    if(wantedimei == '*' or wantedimei == str(x.global_id.global_id.imei)):
      onlyWantedData.append([x.global_id.global_id.transmit_time+x.sub_id*timedelta(seconds=5),x.vert1*scalar if x.vert1*scalar <= top and x.vert1*scalar >= bottom else top if x.vert1*scalar > top else bottom,x.vert2*scalar if x.vert2*scalar <= top and x.vert2*scalar >= bottom else top if x.vert2*scalar > top else bottom,x.vertD*scalar if x.vertD*scalar <= top and x.vertD*scalar >= bottom else top if x.vertD*scalar > top else bottom])
  #minstringint = int(request.GET.get('min','0'))
  #maxstringint = int(request.GET.get('max','999999'))
  wantedimei = request.GET.get('imei','*')
  onlyReallyWantedData = []
  for x in onlyWantedData:
    if True: #if(x[0] >= minstringint and x[0] <= maxstringint):
      onlyReallyWantedData.append(x)
  data = data + onlyReallyWantedData
  
  chartTitle = "Vertical Measurements"
  chartDescription = "This is a test graph generated from all of the fast measurement data.\n This is mostly for demonstration.\n Please enjoy."
  
  data_source = SimpleDataSource(data=data)
  chart = LineChart(data_source, options={'title': chartTitle, 'pointSize': 20}) # Creating a line chart
  
  context = {'chart': chart, 'title': chartTitle, 'description': chartDescription}
  return render(request, 'groundstation/graph.html', context)

def conductivity(request):
  data = [
        ['Time', 'V1', 'V2' ]  # create a list to hold the column names and data for the axis names
      ]
  ordered_condmeasurements = models.ConductivityData.objects.order_by('global_id', 'sub_id')
  print(len(ordered_condmeasurements))
  onlyWantedData = [[x.global_id.id*12+x.sub_id,x.vert1,x.vert2] for x in ordered_condmeasurements]
  data = data + onlyWantedData
  
  chartTitle = "Conductivity Measurements"
  chartDescription = "This is a test graph generated from all of the conductivity measurement data.\n This is mostly for demonstration.\n Please enjoy."
  
  data_source = SimpleDataSource(data=data)
  chart = LineChart(data_source, options={'title': chartTitle, 'pointSize': 20}) # Creating a line chart
  
  context = {'chart': chart, 'title': chartTitle, 'description': chartDescription}
  return render(request, 'groundstation/graph.html',context)
