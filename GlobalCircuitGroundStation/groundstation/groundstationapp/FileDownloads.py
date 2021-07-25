#Functions used for organizing data and packaging for download

from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render
from . import models
from .imeiNames import imeiNames
import super_secrets as secrets

import csv
import datetime as dt
from datetime import datetime
from datetime import timedelta

from django.http import StreamingHttpResponse

#psuedo buffer used to stream csv files
class CSVBuffer:
    def write(self, value):
        return value

#iterates through a set of items using a given:
# serializer
# psuedo buffer
# and header row info for the csv file
def iter_items(items, serializer, pseudo_buffer,header):
    writer = csv.DictWriter(pseudo_buffer, fieldnames=header)
    yield writer.writerow(dict(zip(header,header)))

    for item in items:
        yield writer.writerow(serializer(item))

# All the query sets sorted by time
modelQuerySets = {
    'Request':models.Request.objects.all().order_by("time"),
    'IridiumTransmission':models.IridiumTransmission.objects.all().order_by("time"),
    'RawPacket':models.RawPacket.objects.all().order_by("parent_transmission_id"),
    'PacketV6':models.PacketV6.objects.all().order_by("time"),
    'PacketV6Units':models.PacketV6Units.objects.all().order_by("time"),
    'Measurements':models.Measurements.objects.all().order_by("time"),
    'MeasurementsUnits':models.MeasurementsUnits.objects.all().order_by("time"),
    'ConductivityMeasurements':models.ConductivityMeasurements.objects.all().order_by("time"),
    'ConductivityMeasurementsUnits':models.ConductivityMeasurementsUnits.objects.all().order_by("time"),
    'UplinkRequest':models.UplinkRequest.objects.all().order_by("time"),
}

#Class used for streaming csv files
class CSVStream:
    def export(self, filename, requestedTable, serializer, header, mcuID, use_time_frame, startTime, endTime):
        Qset = modelQuerySets[requestedTable]
        #filter by mcuID if one given
        if(mcuID != 'ALL'):
            if(requestedTable=='Request'):
                Qset = Qset.filter(child_transmission__child_packet__mcu_id=int(mcuID)).select_related('child_transmission__child_packet')
            if(requestedTable=='IridiumTransmission'):
                Qset = Qset.filter(child_packet__mcu_id=int(mcuID)).select_related('child_packet')
            if(requestedTable=='RawPacket'):
                Qset = Qset.filter(parent_transmission__child_packet__mcu_id=int(mcuID))
            if(requestedTable=='PacketV6'):
                Qset = Qset.filter(mcu_id=int(mcuID))
            if(requestedTable=='PacketV6Units'):
                Qset = Qset.filter(parent_packet_v6__mcu_id=int(mcuID)).select_related('parent_packet_v6')
            if(requestedTable=='Measurements'):
                Qset = Qset.filter(parent_packet__mcu_id=int(mcuID)).select_related('parent_packet')
            if(requestedTable=='MeasurementsUnits'):
                Qset = Qset.filter(parent_measurements__parent_packet__mcu_id=int(mcuID)).select_related('parent_measurements__parent_packet')
            if(requestedTable=='ConductivityMeasurements'):
                Qset = Qset.filter(parent_packet__mcu_id=int(mcuID)).select_related('parent_packet')
            if(requestedTable=='ConductivityMeasurementsUnits'):
                Qset = Qset.filter(parent_conductivity_measurements__parent_packet__mcu_id=int(mcuID)).select_related('parent_conductivity_measurements__parent_packet')
        #filter to specific time frame if one given
        if(use_time_frame):
            Qset = Qset.filter(time__gte=startTime).filter(time__lte=endTime)
        #creating streaming http response for streaming the csv file
        response = StreamingHttpResponse(streaming_content=(iter_items(Qset,serializer,CSVBuffer(),header)),
                                         content_type="text/csv")
        response['Content-Disposition'] = f"attachment; filename={filename}.csv"
        return response

# Server Request Serializer
def csv_serializer_Request(data):
    mcuID = 'None'
    try:
        mcuID = data.child_transmission.child_packet.mcu_id
    except:
        pass
    return {
        'id':data.id,
        'mcu_id':mcuID,
        'request_time':data.time,
        'processing_duration':data.processing_duration,
        'forwarded_for_address':data.forwarded_for_address,
        'forwarded_host_address':data.forwarded_host_address,
        'forwarded_server_address':data.forwarded_server_address,
        'remote_address':data.remote_address,
        'raw_request_data':data.raw_request_data,
        'response_duration':data.response_duration,
        'response_errors':data.response_errors,
        'response_status_code':data.response_status_code,
    }

# Iridium Transmission Serializer
def csv_serializer_IridiumTransmission(data):
    mcuID = 'None'
    try:
        mcuID = data.child_packet.mcu_id
    except:
        pass
    return {
        'parent_request_id':data.parent_request_id,
        'mcu_id':mcuID,
        'irium_transmission_time':data.time,
        'latitude':data.latitude,
        'longitude':data.longitude,
        'cep':data.cep,
        'momsn':data.momsn,
        'imei':data.imei,
        'device_type':data.device_type,
        'serial':data.serial,
        'iridium_session_status':data.iridium_session_status,
        'transmitted_via_satellite':data.transmitted_via_satellite,
    }

# Raw Packet Data Serializer
def csv_serializer_RawPacket(data):
    mcuID = 'None'
    try:
        mcuID = data.parent_transmission.child_packet.mcu_id
    except:
        pass
    return {
        'parent_transmission_id':data.parent_transmission_id,
        'gps_time':data.parent_transmission.child_packet.time,
        'iridium_time':data.parent_transmission.time,
        'mcu_id':mcuID,
        'data':data.data,
        'hexdata':data.hexdata,
    }

# Packet Data Serializer
def csv_serializer_PacketV6(data):
    return {
        'parent_transmission_id':data.parent_transmission_id,
        'yikes_status':data.yikes_status,
        'mcu_id':data.mcu_id,
        'version':data.version,
        'sequence_id':data.sequence_id,
        'gps_time':data.time,
        'iridium_time':data.parent_transmission.time,
        'latitude':data.latitude,
        'longitude':data.longitude,
        'altitude':data.altitude,
        'ballast_status':data.ballast_status,
        'cutdown_status':data.cutdown_status,
        'conductivity_time':data.conductivity_time,
        'satellites_count':data.satellites_count,
        'rockblock_signal_strength':data.rockblock_signal_strength,
        'commands_count':data.commands_count,
        'altimeter_temp':data.altimeter_temp,
        'altimeter_pressure':data.altimeter_pressure,
        'positive_7v_battery_voltage':data.positive_7v_battery_voltage,
        'negative_7v_battery_voltage':data.negative_7v_battery_voltage,
        'positive_3v6_battery_voltage':data.positive_3v6_battery_voltage,
        'current_draw_7v_rail':data.current_draw_7v_rail,
        'current_draw_3v3_rail':data.current_draw_3v3_rail,
        'battery_temp':data.battery_temp,
        'mcu_temp':data.mcu_temp,
        'compass_temp':data.compass_temp,
        'adc1_temp':data.adc1_temp,
        'adc2_temp':data.adc2_temp,
        'external_temp':data.external_temp,
        'rockblock_temp':data.rockblock_temp,
    }

# Unit Converted Packet Data Serializer
def csv_serializer_PacketV6Units(data):
    return {
        'parent_packet_v6_id':data.parent_packet_v6_id,
        'yikes_status':data.yikes_status,
        'mcu_id':data.mcu_id,
        'version':data.version,
        'sequence_id':data.sequence_id,
        'gps_time':data.time,
        'iridium_time':data.parent_packet_v6.parent_transmission.time,
        'latitude':data.latitude,
        'longitude':data.longitude,
        'altitude':data.altitude,
        'ballast_status':data.ballast_status,
        'cutdown_status':data.cutdown_status,
        'conductivity_time':data.conductivity_time,
        'satellites_count':data.satellites_count,
        'rockblock_signal_strength':data.rockblock_signal_strength,
        'commands_count':data.commands_count,
        'altimeter_temp':data.altimeter_temp,
        'altimeter_pressure':data.altimeter_pressure,
        'positive_7v_battery_voltage':data.positive_7v_battery_voltage,
        'negative_7v_battery_voltage':data.negative_7v_battery_voltage,
        'positive_3v6_battery_voltage':data.positive_3v6_battery_voltage,
        'current_draw_7v_rail':data.current_draw_7v_rail,
        'current_draw_3v3_rail':data.current_draw_3v3_rail,
        'battery_temp':data.battery_temp,
        'mcu_temp':data.mcu_temp,
        'compass_temp':data.compass_temp,
        'adc1_temp':data.adc1_temp,
        'adc2_temp':data.adc2_temp,
        'external_temp':data.external_temp,
        'rockblock_temp':data.rockblock_temp,
    }

# Measurement Data Serializer
def csv_serializer_Measurements(data):
    return {
        'parent_packet_id':data.parent_packet_id,
        'mcu_id': data.parent_packet.mcu_id,
        'gps_time':data.time,
        'iridium_time':data.parent_packet.parent_transmission.time,
        'vert1':data.vert1,
        'vert2':data.vert2,
        'vertD':data.vertD,
        'compassX':data.compassX,
        'compassY':data.compassY,
        'compassZ':data.compassZ,
        'horiz1':data.horiz1,
        'horiz2':data.horiz2,
        'horizD':data.horizD,
    }

# Unit Converted Measurement Data Serializer
def csv_serializer_MeasurementsUnits(data):
    return {
        'parent_measurements_id':data.parent_measurements_id,
        'mcu_id': data.parent_measurements.parent_packet.mcu_id,
        'gps_time':data.time,
        'iridium_time':data.parent_measurements.parent_packet.parent_transmission.time,
        'vert1':data.vert1,
        'vert2':data.vert2,
        'vertD':data.vertD,
        'compassX':data.compassX,
        'compassY':data.compassY,
        'compassZ':data.compassZ,
        'horiz1':data.horiz1,
        'horiz2':data.horiz2,
        'horizD':data.horizD,
    }

# Conductivity Measurement Data Serializer
def csv_serializer_ConductivityMeasurements(data):
    return {
        'parent_packet_id':data.parent_packet_id,
        'mcu_id': data.parent_packet.mcu_id,
        'iridium_time':data.parent_packet.parent_transmission.time,
        'gps_time':data.time,
        'vert1':data.vert1,
        'vert2':data.vert2,
    }

# Unit Converted Conductivity Measurement Data Serializer
def csv_serializer_ConductivityMeasurementsUnits(data):
    return {
        'parent_conductivity_measurements_id':data.parent_conductivity_measurements_id,
        'mcu_id': data.parent_conductivity_measurements.parent_packet.mcu_id,
        'gps_time':data.time,
        'iridium_time':data.parent_conductivity_measurements.parent_packet.parent_transmission.time,
        'vert1':data.vert1,
        'vert2':data.vert2,
    }

# Uplink Request Serializer
def csv_serializer_UplinkRequest(data):
    return{
        'id':data.id,
        'imei':data.imei,
        'request_time':data.time,
        'password':data.password,
        'message':data.message,
        'success':data.success,
    }

# A dictionary of the serialization functions
serialzerFunctions = {
    'Request':csv_serializer_Request,
    'IridiumTransmission':csv_serializer_IridiumTransmission,
    'RawPacket':csv_serializer_RawPacket,
    'PacketV6':csv_serializer_PacketV6,
    'PacketV6Units':csv_serializer_PacketV6Units,
    'Measurements':csv_serializer_Measurements,
    'MeasurementsUnits':csv_serializer_MeasurementsUnits,
    'ConductivityMeasurements':csv_serializer_ConductivityMeasurements,
    'ConductivityMeasurementsUnits':csv_serializer_ConductivityMeasurementsUnits,
    'UplinkRequest':csv_serializer_UplinkRequest,
}

# Headers for each csv file data type
modelHeaders = {
    'Request':['id','mcu_id','request_time','processing_duration','forwarded_for_address',
                'forwarded_host_address','forwarded_server_address','remote_address',
                'raw_request_data','response_duration','response_errors','response_status_code'],
    'IridiumTransmission':['parent_request_id','mcu_id','irium_transmission_time','latitude','longitude',
                'cep','momsn','imei','device_type','serial',
                'iridium_session_status','transmitted_via_satellite'],
    'RawPacket':['parent_transmission_id','mcu_id','gps_time','iridium_time','data','hexdata'],
    'PacketV6':['parent_transmission_id','yikes_status','mcu_id','version',
                'sequence_id','gps_time','iridium_time','latitude','longitude','altitude',
                'ballast_status','cutdown_status','conductivity_time','satellites_count',
                'rockblock_signal_strength','commands_count','altimeter_temp',
                'altimeter_pressure','positive_7v_battery_voltage','negative_7v_battery_voltage',
                'positive_3v6_battery_voltage','current_draw_7v_rail','current_draw_3v3_rail',
                'battery_temp','mcu_temp','compass_temp','adc1_temp','adc2_temp',
                'external_temp','rockblock_temp'],
    'PacketV6Units':['parent_packet_v6_id','yikes_status','mcu_id','version',
                'sequence_id','gps_time','iridium_time','latitude','longitude','altitude',
                'ballast_status','cutdown_status','conductivity_time','satellites_count',
                'rockblock_signal_strength','commands_count','altimeter_temp',
                'altimeter_pressure','positive_7v_battery_voltage','negative_7v_battery_voltage',
                'positive_3v6_battery_voltage','current_draw_7v_rail','current_draw_3v3_rail',
                'battery_temp','mcu_temp','compass_temp','adc1_temp','adc2_temp',
                'external_temp','rockblock_temp'],
    'Measurements':['parent_packet_id','mcu_id','gps_time','iridium_time','vert1','vert2',
                'vertD','compassX','compassY','compassZ','horiz1',
                'horiz2','horizD'],
    'MeasurementsUnits':['parent_measurements_id','mcu_id','gps_time','iridium_time','vert1','vert2',
                'vertD','compassX','compassY','compassZ','horiz1',
                'horiz2','horizD'],
    'ConductivityMeasurements':['parent_packet_id','mcu_id','gps_time','iridium_time','vert1','vert2'],
    'ConductivityMeasurementsUnits':['parent_conductivity_measurements_id', 'mcu_id','gps_time','iridium_time','vert1','vert2'],
    'UplinkRequest':['id','imei','request_time','password',
                'message','success'],
}

# Dictionary of File Names
fileNames = {
    'Request':'gec_groundstation_requests',
    'IridiumTransmission':'gec_iridium_transmissions',
    'RawPacket':'gec_binary_packet_data',
    'PacketV6':'gec_raw_packet_data',
    'PacketV6Units':'gec_packet_data',
    'Measurements':'gec_raw_measurement_data',
    'MeasurementsUnits':'gec_measurement_data',
    'ConductivityMeasurements':'gec_raw_conductivity_measurement_data',
    'ConductivityMeasurementsUnits':'gec_conductivity_measurement_data',
    'UplinkRequest':'gec_uplink_requests',
}

# Download Card information for template
downloadCards = [
    {
        'name':'groundstation_requests',
        'description':'all requests made to this groundstation',
        'items':modelHeaders['Request'],
        'table':'Request'
    },
    {
        'name':'iridium_transmissions',
        'description':'all iridium transmissions received at this groundstation',
        'items':modelHeaders['IridiumTransmission'],
        'table':'IridiumTransmission'
    },
    {
        'name':'binary_packet_data',
        'description':'the raw binary packet data',
        'items':modelHeaders['RawPacket'],
        'table':'RawPacket'
    },
    {
        'name':'raw_packet_data',
        'description':'the unconverted packet data',
        'items':modelHeaders['PacketV6'],
        'table':'PacketV6'
    },
    {
        'name':'packet_data',
        'description':'the converted packet data',
        'items':modelHeaders['PacketV6Units'],
        'table':'PacketV6Units'
    },
    {
        'name':'raw_measurement_data',
        'description':'the unconverted measurement data',
        'items':modelHeaders['Measurements'],
        'table':'Measurements'
    },
    {
        'name':'measurement_data',
        'description':'the convereted measurement data',
        'items':modelHeaders['MeasurementsUnits'],
        'table':'MeasurementsUnits'
    },
    {
        'name':'raw_conductivity_measurement_data',
        'description':'the unconverted conductivity measurement data',
        'items':modelHeaders['ConductivityMeasurements'],
        'table':'ConductivityMeasurements'
    },
    {
        'name':'conductivity_measurement_data',
        'description':'the converted conductivity measurement data',
        'items':modelHeaders['ConductivityMeasurementsUnits'],
        'table':'ConductivityMeasurementsUnits'
    },
    {
        'name':'uplink_requests',
        'description':'all uplink requests attempted from this groundstation',
        'items':modelHeaders['UplinkRequest'],
        'table':'UplinkRequest'
    },
]

# Function to get the time window to filter
def getTimeWindow(request):
    utcTimeNow = datetime.utcnow()
    windowStartAtDate = request.GET.get('windowStartAtDate',(utcTimeNow-(timedelta(hours=1))).strftime("%Y-%m-%d"))
    if windowStartAtDate == '':
        windowStartAtDate = utcTimeNow.strftime("%Y-%m-%d") (utcTimeNow-(timedelta(hours=1))).strftime("%Y-%m-%d")
    windowStartAtHour = request.GET.get('windowStartAtHour', str((utcTimeNow-(timedelta(hours=1))).hour))
    windowStartAtMinute = request.GET.get('windowStartAtMinute', str((utcTimeNow-(timedelta(hours=1))).minute))
    windowStartAtSecond = request.GET.get('windowStartAtSecond', str((utcTimeNow-(timedelta(hours=1))).second))
    windowStartTimeString = windowStartAtDate + ' '
    windowStartTimeString = windowStartTimeString + windowStartAtHour + ':'
    windowStartTimeString = windowStartTimeString + windowStartAtMinute + ':'
    windowStartTimeString = windowStartTimeString + windowStartAtSecond
    
    windowEndAtDate = request.GET.get('windowEndAtDate', datetime.today().strftime("%Y-%m-%d"))
    if windowEndAtDate == '':
        windowEndAtDate = datetime.today().strftime("%Y-%m-%d")
    windowEndAtHour = request.GET.get('windowEndAtHour', '23')
    windowEndAtMinute = request.GET.get('windowEndAtMinute', '59')
    windowEndAtSecond = request.GET.get('windowEndAtSecond', '59')
    
    windowEndTimeString = windowEndAtDate + ' '
    windowEndTimeString = windowEndTimeString + windowEndAtHour + ':'
    windowEndTimeString = windowEndTimeString + windowEndAtMinute + ':'
    windowEndTimeString = windowEndTimeString + windowEndAtSecond

    return datetime.strptime(windowStartTimeString, "%Y-%m-%d %H:%M:%S"), datetime.strptime(windowEndTimeString, "%Y-%m-%d %H:%M:%S")

# Actual File Download function
def downloadFile(request):
    if request.method == 'GET':
        requestedData = request.GET.get('requestedData', 'ALL')
        if requestedData in serialzerFunctions:
            csv_stream = CSVStream()
            mcuID = request.GET.get('mcu_id', 'ALL')
            use_time_frame = ('use_time_frame' in request.GET)
            startTime = None
            endTime = None
            if(use_time_frame):
                startTime, endTime = getTimeWindow(request)
            return csv_stream.export(fileNames[requestedData],requestedData,serialzerFunctions[requestedData],modelHeaders[requestedData],
                                     mcuID, use_time_frame, startTime, endTime)
        else:
            print("Table Not Found: " + requestedData)
            return(HttpResponseNotFound())
    else:
        print("This is not a GET request.")
        return(HttpResponseBadRequest())

# Download File View
def fileDownloadView(request):
    utcTimeNow =datetime.utcnow()

    filterOptions = {}

    filterOptions['windowStartAtDate'] = request.GET.get('windowStartAtDate',(utcTimeNow-(timedelta(hours=1))).strftime("%Y-%m-%d"))
    if filterOptions['windowStartAtDate'] == '':
        filterOptions['windowStartAtDate'] = utcTimeNow.strftime("%Y-%m-%d") (utcTimeNow-(timedelta(hours=1))).strftime("%Y-%m-%d")
    filterOptions['windowStartAtHour'] = request.GET.get('windowStartAtHour', str((utcTimeNow-(timedelta(hours=1))).hour))
    filterOptions['windowStartAtMinute'] = request.GET.get('windowStartAtMinute', str((utcTimeNow-(timedelta(hours=1))).minute))
    filterOptions['windowStartAtSecond'] = request.GET.get('windowStartAtSecond', str((utcTimeNow-(timedelta(hours=1))).second))
    
    windowStartTimeString = filterOptions['windowStartAtDate'] + ' '
    windowStartTimeString = windowStartTimeString + filterOptions['windowStartAtHour'] + ':'
    windowStartTimeString = windowStartTimeString + filterOptions['windowStartAtMinute'] + ':'
    windowStartTimeString = windowStartTimeString + filterOptions['windowStartAtSecond']

    filterOptions['windowEndAtDate'] = request.GET.get('windowEndAtDate', datetime.utcnow().strftime("%Y-%m-%d"))
    if filterOptions['windowEndAtDate'] == '':
        filterOptions['windowEndAtDate'] = datetime.utcnow().strftime("%Y-%m-%d")
    filterOptions['windowEndAtHour'] = request.GET.get('windowEndAtHour', '23')
    filterOptions['windowEndAtMinute'] = request.GET.get('windowEndAtMinute', '59')
    filterOptions['windowEndAtSecond'] = request.GET.get('windowEndAtSecond', '59')
    
    windowEndTimeString = filterOptions['windowEndAtDate'] + ' '
    windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtHour'] + ':'
    windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtMinute'] + ':'
    windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtSecond']

    context = {
        'tableCards': downloadCards,
        'hours': [str(x).zfill(2) for x in range(24)],
        'minutes': [str(x).zfill(2) for x in range(60)],
        'seconds': [str(x).zfill(2) for x in range(60)],
        'mcuIDs' : ['ALL', '1', '2', '3', '4'],
        'filterOptions' : filterOptions,
    }
    return(render(request, 'groundstation/CSVDownload.html',context))


