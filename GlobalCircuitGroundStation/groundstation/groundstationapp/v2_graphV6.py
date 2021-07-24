from django.shortcuts import render
from django.db.models import aggregates, Avg, Max, Min
from django.http.response import JsonResponse
from django.core import serializers

from graphos.sources.simple import SimpleDataSource
from graphos.sources.model import ModelDataSource
from graphos.renderers.gchart import LineChart

from . import models
from .imeiNames import imeiNames
import super_secrets as secrets
from . import unitConversions as uc

import datetime as dt
from datetime import datetime
from datetime import timedelta

import copy

signalList = [
              'NONE'                                        ,
              'Request___processing_duration'               ,
              'Request___forwarded_for_address'             ,
              'Request___remote_address'                    ,
              'Request___response_duration'                 ,
              'Request___response_status_code'              ,
              
              
              
              'IridiumTransmission___latitude'              ,
              'IridiumTransmission___longitude'             ,
              'IridiumTransmission___cep'                   ,
              'IridiumTransmission___momsn'                 ,
              'IridiumTransmission___imei'                  ,
              'IridiumTransmission___device_type'           ,
              'IridiumTransmission___serial'                ,
              'IridiumTransmission___iridium_session_status',
              
              
              
              'PacketV6___yikes_status'                     ,
              'PacketV6___mcu_id'                           ,
              'PacketV6___version'                          ,
              'PacketV6___sequence_id'                      ,
              'PacketV6___latitude'                         ,
              'PacketV6___longitude'                        ,
              'PacketV6___altitude'                         ,
              'PacketV6___ballast_status'                   ,
              'PacketV6___cutdown_status'                   ,
              'PacketV6___conductivity_time'                ,
              'PacketV6___satellites_count'                 ,
              'PacketV6___rockblock_signal_strength'        ,
              'PacketV6___commands_count'                   ,
              'PacketV6___altimeter_temp'                   ,
              'PacketV6___altimeter_pressure'               ,
              'PacketV6___positive_7v_battery_voltage'      ,
              'PacketV6___negative_7v_battery_voltage'      ,
              'PacketV6___positive_3v6_battery_voltage'     ,
              'PacketV6___current_draw_7v_rail'             ,
              'PacketV6___current_draw_3v3_rail'            ,
              'PacketV6___battery_temp'                     ,
              'PacketV6___mcu_temp'                         ,
              'PacketV6___compass_temp'                     ,
              'PacketV6___adc1_temp'                        ,
              'PacketV6___adc2_temp'                        ,
              'PacketV6___external_temp'                    ,
              'PacketV6___rockblock_temp'                   ,
              
              'PacketV6Units___latitude'                    ,
              'PacketV6Units___longitude'                   ,
              'PacketV6Units___altitude'                    ,
              'PacketV6Units___conductivity_time'           ,
              'PacketV6Units___satellites_count'            ,
              'PacketV6Units___rockblock_signal_strength'   ,
              'PacketV6Units___commands_count'              ,
              'PacketV6Units___altimeter_temp'              ,
              'PacketV6Units___altimeter_pressure'          ,
              'PacketV6Units___positive_7v_battery_voltage' ,
              'PacketV6Units___negative_7v_battery_voltage' ,
              'PacketV6Units___positive_3v6_battery_voltage',
              'PacketV6Units___current_draw_7v_rail'        ,
              'PacketV6Units___current_draw_3v3_rail'       ,
              'PacketV6Units___battery_temp'                ,
              'PacketV6Units___mcu_temp'                    ,
              'PacketV6Units___compass_temp'                ,
              'PacketV6Units___adc1_temp'                   ,
              'PacketV6Units___adc2_temp'                   ,
              'PacketV6Units___external_temp'               ,
              'PacketV6Units___rockblock_temp'              ,
              
              
              
              'Measurements___vert1'                        ,
              'Measurements___vert2'                        ,
              'Measurements___vertD'                        ,
              'Measurements___compassX'                     ,
              'Measurements___compassY'                     ,
              'Measurements___compassZ'                     ,
              'Measurements___horiz1'                       ,
              'Measurements___horiz2'                       ,
              'Measurements___horizD'                       ,
              
              'MeasurementsUnits___vert1'                   ,
              'MeasurementsUnits___vert2'                   ,
              'MeasurementsUnits___vertD'                   ,
              'MeasurementsUnits___compassX'                ,
              'MeasurementsUnits___compassY'                ,
              'MeasurementsUnits___compassZ'                ,
              'MeasurementsUnits___horiz1'                  ,
              'MeasurementsUnits___horiz2'                  ,
              'MeasurementsUnits___horizD'                  ,
              
              
              
              'ConductivityMeasurements___vert1'            ,
              'ConductivityMeasurements___vert2'            ,
              
              'ConductivityMeasurementsUnits___vert1'       ,
              'ConductivityMeasurementsUnits___vert2'       ,
              ]

signalDefinitions = {
                    'NONE'                                        : None,
                    'Request___processing_duration'               :{
                                                                   'name' : 'Request Processing Duration',
                                                                   'units' : 's',
                                                                   'description' : '',
                                                                   },
                    'Request___forwarded_for_address'             :{
                                                                   'name' : 'Request Forwarded For Address',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Request___remote_address'                    :{
                                                                   'name' : 'Request Remote Address',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Request___response_duration'                 :{
                                                                   'name' : 'Request Response Duration',
                                                                   'units' : 's',
                                                                   'description' : '',
                                                                   },
                    'Request___response_status_code'              :{
                                                                   'name' : 'Request Response Status Code',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___latitude'              :{
                                                                   'name' : 'Iridium Latitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___longitude'             :{
                                                                   'name' : 'Iridium Longitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___cep'                   :{
                                                                   'name' : 'CEP',
                                                                   'units' : 'km',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___momsn'                 :{
                                                                   'name' : 'RB Mobal Originated Message Serial Number',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___imei'                  :{
                                                                   'name' : 'Rockblock IMEI',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___device_type'           :{
                                                                   'name' : 'Iridium Device Type',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___serial'                :{
                                                                   'name' : 'Iridium Serial',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'IridiumTransmission___iridium_session_status':{
                                                                   'name' : 'Iridium Session status',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___yikes_status'                     :{
                                                                   'name' : 'Yikes Status',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___mcu_id'                           :{
                                                                   'name' : 'MCU ID',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___version'                          :{
                                                                   'name' : 'Packet Version',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___sequence_id'                      :{
                                                                   'name' : 'Sequence ID',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___latitude'                         :{
                                                                   'name' : 'Latitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___longitude'                        :{
                                                                   'name' : 'Longitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___altitude'                         :{
                                                                   'name' : 'Altitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___ballast_status'                   :{
                                                                   'name' : 'Ballast Status',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___cutdown_status'                   :{
                                                                   'name' : 'Cutdown Status',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___conductivity_time'                :{
                                                                   'name' : 'Condductivity Time',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___satellites_count'                 :{
                                                                   'name' : 'Satellite Count',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___rockblock_signal_strength'        :{
                                                                   'name' : 'RockBlock Signal Strength',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___commands_count'                   :{
                                                                   'name' : 'Command Count',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___altimeter_temp'                   :{
                                                                   'name' : 'Altimeter Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___altimeter_pressure'               :{
                                                                   'name' : 'Altimeter Pressure',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___positive_7v_battery_voltage'      :{
                                                                   'name' : '+7v Battery Voltage',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___negative_7v_battery_voltage'      :{
                                                                   'name' : '-7v Battery Voltage',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___positive_3v6_battery_voltage'     :{
                                                                   'name' : '+3v6 Battery Voltage',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___current_draw_7v_rail'             :{
                                                                   'name' : 'Current Draw 7v Rail',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___current_draw_3v3_rail'            :{
                                                                   'name' : 'Current Draw 3v3 Rail',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___battery_temp'                     :{
                                                                   'name' : 'Battery Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___mcu_temp'                         :{
                                                                   'name' : 'MCU Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___compass_temp'                     :{
                                                                   'name' : 'Compass Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___adc1_temp'                        :{
                                                                   'name' : 'ADC1 Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___adc2_temp'                        :{
                                                                   'name' : 'ADC2 Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___external_temp'                    :{
                                                                   'name' : 'External Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6___rockblock_temp'                   :{
                                                                   'name' : 'Rockblock Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___latitude'                    :{
                                                                   'name' : '(Units) Latitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___longitude'                   :{
                                                                   'name' : '(Units) Longitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___altitude'                    :{
                                                                   'name' : '(Units) Altitude',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___conductivity_time'           :{
                                                                   'name' : '(Units) Conductivity Time',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___satellites_count'            :{
                                                                   'name' : '(Units) Satellites Count',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___rockblock_signal_strength'   :{
                                                                   'name' : '(Units) Rockblock Signal Strength',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___commands_count'              :{
                                                                   'name' : '(Units) Commands Count',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___altimeter_temp'              :{
                                                                   'name' : '(Units) Altimeter Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___altimeter_pressure'          :{
                                                                   'name' : '(Units) Altimeter Pressure',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___positive_7v_battery_voltage' :{
                                                                   'name' : '(Units) Volts +7V',
                                                                   'units' : 'V',
                                                                   'description' : 'The measured voltage of the +7V battery.',
                                                                   },
                    'PacketV6Units___negative_7v_battery_voltage' :{
                                                                   'name' : '(Units) Volts -7V',
                                                                   'units' : 'V',
                                                                   'description' : 'The measured voltage of the -7V battery.',
                                                                   },
                    'PacketV6Units___positive_3v6_battery_voltage':{
                                                                   'name' : '(Units) Volts +3V6',
                                                                   'units' : 'V',
                                                                   'description' : 'The measured voltage of the +3V6 battery.',
                                                                   },
                    'PacketV6Units___current_draw_7v_rail'        :{
                                                                   'name' : '(Units) Current +7V',
                                                                   'units' : 'mA',
                                                                   'description' : 'The current draw on the +7V rail.',
                                                                   },
                    'PacketV6Units___current_draw_3v3_rail'       :{
                                                                   'name' : '(Units) Current +3V3',
                                                                   'units' : 'mA',
                                                                   'description' : 'The current draw on the +3V3 rail.',
                                                                   },
                    'PacketV6Units___battery_temp'                :{
                                                                   'name' : '(Units) Battery Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___mcu_temp'                    :{
                                                                   'name' : '(Units) MCU Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___compass_temp'                :{
                                                                   'name' : '(Units) Compass Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___adc1_temp'                   :{
                                                                   'name' : '(Units) ADC1 Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___adc2_temp'                   :{
                                                                   'name' : '(Units) ADC2 Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___external_temp'               :{
                                                                   'name' : '(Units) External Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'PacketV6Units___rockblock_temp'              :{
                                                                   'name' : '(Units) Rockblock Temperature',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___vert1'                        :{
                                                                   'name' : 'Vertical Probe 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___vert2'                        :{
                                                                   'name' : 'Vertical Probe 2',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___vertD'                        :{
                                                                   'name' : 'Vertical Difference',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___compassX'                     :{
                                                                   'name' : 'CompassX',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___compassY'                     :{
                                                                   'name' : 'CompassY',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___compassZ'                     :{
                                                                   'name' : 'CompassZ',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___horiz1'                       :{
                                                                   'name' : 'Horizontal Probe 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___horiz2'                       :{
                                                                   'name' : 'Horizontal Probe 2',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'Measurements___horizD'                       :{
                                                                   'name' : 'Horizontal Difference',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___vert1'                   :{
                                                                   'name' : '(Units) Vertical Probe 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___vert2'                   :{
                                                                   'name' : '(Units) Vertical Probe 2 ',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___vertD'                   :{
                                                                   'name' : '(Units) Vertical Difference',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___compassX'                :{
                                                                   'name' : '(Units) Compass X',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___compassY'                :{
                                                                   'name' : '(Units) Compass Y',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___compassZ'                :{
                                                                   'name' : '(Units) Compass Z',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___horiz1'                  :{
                                                                   'name' : '(Units) Horizontal Probe 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___horiz2'                  :{
                                                                   'name' : '(Units) Horizontal Probe 2',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'MeasurementsUnits___horizD'                  :{
                                                                   'name' : '(Units) Horizontal Difference',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'ConductivityMeasurements___vert1'            :{
                                                                   'name' : 'Vertical Conductivity 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'ConductivityMeasurements___vert2'            :{
                                                                   'name' : 'Vertical Conductivity 2',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'ConductivityMeasurementsUnits___vert1'       :{
                                                                   'name' : '(Units) Vertical Conductivity 1',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    'ConductivityMeasurementsUnits___vert2'       :{
                                                                   'name' : '(Units) Vertical Conductivity 2',
                                                                   'units' : '',
                                                                   'description' : '',
                                                                   },
                    }
                    
def sillyJavascriptDatetimeString(datetimeObject):
  tDTS = datetimeObject.strftime("Date(%Y, %m, %d, %H, %M, %S, %f)")
  tempDateString = tDTS[:11] + '{0:02d}'.format(int(tDTS[11:13])-1) + tDTS[13:31] + '{0:03d}'.format(int(tDTS[31:37])//1000) + tDTS[37:]
  return tempDateString

sJDS = sillyJavascriptDatetimeString

def signalValue(dataRow, signalId):
  if signalId == 'IridiumTransmission___cep':
    return dataRow.cep
  elif signalId == 'PacketV6___rockblock_signal_strength':
    return dataRow.rockblock_signal_strength
  elif signalId == 'PacketV6Units___rockblock_signal_strength':
    return dataRow.rockblock_signal_strength
  elif signalId == 'PacketV6Units___positive_7v_battery_voltage':
    return dataRow.positive_7v_battery_voltage
  elif signalId == 'PacketV6Units___negative_7v_battery_voltage':
    return dataRow.negative_7v_battery_voltage
  elif signalId == 'PacketV6Units___positive_3v6_battery_voltage':
    return dataRow.positive_3v6_battery_voltage
  else:
    return getattr(dataRow, signalId.split('___')[1])
  
  return None

def createDataFromTime(sigID, filteredDataRows, tableName, chartOptions):
  toolTipColumn = {'type': 'string', 'role':'tooltip', 'p':{'html': True}}
  dataHeader = [[{'type': 'datetime', 'label': 'Time'}]]
  
  sigDef = signalDefinitions[sigID]
  dataHeader[0].append(sigDef['name'])
  dataHeader[0].append(toolTipColumn)

  dataArray = []
  for x in filteredDataRows[tableName]:
    time=x.time
    # if(tableName=='PacketV6'):
    #   time=x.parent_transmission.time
    # if(tableName=='PacketV6Units'):
    #   time=x.parent_packet_v6.parent_transmission.time
    # if(tableName=='Measurements'):
    #   time=x.parent_packet.parent_transmission.time
    # if(tableName=='MeasurementsUnits'):
    #   time=x.parent_measurements.parent_packet.parent_transmission.time
    # if(tableName=='ConductivityMeasurements'):
    #   time=x.parent_packet.parent_transmission.time
    # if(tableName=='ConductivityMeasurementsUnits'):
    #   time=x.parent_conductivity_measurements.parent_packet.parent_transmission.time
    data = [sJDS(time)]
    sigValue = signalValue(x,sigID)
    data.append(sigValue)
    toolTipString = time.strftime("%b. %d, %Y, %H:%M:%S %Z\n" + sigDef['name'] + ": "+str(sigValue))
    if(sigDef['units']):
      toolTipString = toolTipString + ' ' + sigDef['units']
    data.append(toolTipString)
    dataArray.append(data)
  dataList = dataHeader + dataArray

  chartOptions['title'] = sigDef['name']
  chartOptions['vAxes'] = {0: {"title": sigDef['name']}}

  return SimpleDataSource(data=dataList)

def createDataFromIridiumTime(sigID, filteredDataRows, tableName, chartOptions):
  toolTipColumn = {'type': 'string', 'role':'tooltip', 'p':{'html': True}}
  dataHeader = [[{'type': 'datetime', 'label': 'Time'}]]
  
  sigDef = signalDefinitions[sigID]
  dataHeader[0].append(sigDef['name'])
  dataHeader[0].append(toolTipColumn)

  joinedData=filteredDataRows[tableName]
  if(tableName=='PacketV6'):
    joinedData=joinedData.select_related('parent_transmission')
  if(tableName=='PacketV6Units'):
    joinedData=joinedData.select_related('parent_packet_v6').select_related('parent_packet_v6__parent_transmission')
  if(tableName=='Measurements'):
    joinedData=joinedData.select_related('parent_packet').select_related('parent_packet__parent_transmission')
  if(tableName=='MeasurementsUnits'):
    joinedData=joinedData.select_related('parent_measurements').select_related('parent_measurements__parent_packet__parent_transmission')
  if(tableName=='ConductivityMeasurements'):
    joinedData=joinedData.select_related('parent_packet').select_related('parent_packet__parent_transmission')
  if(tableName=='ConductivityMeasurementsUnits'):
    joinedData=joinedData.select_related('parent_conductivity_measurements').select_related('parent_conductivity_measurements__parent_packet').select_related('parent_conductivity_measurements__parent_packet__parent_transmission')

  dataArray = []
  for x in joinedData:
    time=x.time
    if(tableName=='PacketV6'):
      time=x.parent_transmission.time
    if(tableName=='PacketV6Units'):
      time=x.parent_packet_v6.parent_transmission.time
    if(tableName=='Measurements'):
      time=x.parent_packet.parent_transmission.time
    if(tableName=='MeasurementsUnits'):
      time=x.parent_measurements.parent_packet.parent_transmission.time
    if(tableName=='ConductivityMeasurements'):
      time=x.parent_packet.parent_transmission.time
    if(tableName=='ConductivityMeasurementsUnits'):
      time=x.parent_conductivity_measurements.parent_packet.parent_transmission.time
    data = [sJDS(time)]
    sigValue = signalValue(x,sigID)
    data.append(sigValue)
    toolTipString = time.strftime("%b. %d, %Y, %H:%M:%S %Z\n" + sigDef['name'] + ": "+str(sigValue))
    if(sigDef['units']):
      toolTipString = toolTipString + ' ' + sigDef['units']
    data.append(toolTipString)
    dataArray.append(data)
  dataList = dataHeader + dataArray

  chartOptions['title'] = sigDef['name']
  chartOptions['vAxes'] = {0: {"title": sigDef['name']}}

  return SimpleDataSource(data=dataList)

def createDataFromSequence(sigID, filteredDataRows, tableName, chartOptions):
  toolTipColumn = {'type': 'string', 'role':'tooltip', 'p':{'html': True}}
  dataHeader = [[{'type': 'number', 'label': 'Sequence'}]]
  
  sigDef = signalDefinitions[sigID]
  dataHeader[0].append(sigDef['name'])
  dataHeader[0].append(toolTipColumn)
  i = len(filteredDataRows[tableName])
  dataArray = []
  for x in filteredDataRows[tableName]:
    data = [i]
    
    sigValue = signalValue(x,sigID)
    data.append(sigValue)
    toolTipString = "Sequence: "+ str(i) +" | "+ sigDef['name'] + ": "+str(sigValue)
    i-=1
    if(sigDef['units']):
      toolTipString = toolTipString + ' ' + sigDef['units']
    data.append(toolTipString)
    dataArray.append(data)
  dataList = dataHeader + dataArray

  chartOptions['title'] = sigDef['name']
  chartOptions['vAxes'] = {0: {"title": sigDef['name']}}
  chartOptions['hAxis'] = {}

  return SimpleDataSource(data=dataList)

def createUpdateData(sigID, filteredDataRows, tableName):
  
  sigDef = signalDefinitions[sigID]

  dataArray = []
  for x in filteredDataRows[tableName]:
    data = [x.time]
    sigValue = signalValue(x,sigID)
    data.append(sigValue)
    toolTipString = x.time.strftime("%b. %d, %Y, %H:%M:%S\n" + sigDef['name'] + ": "+str(sigValue))
    if(sigDef['units']):
      toolTipString = toolTipString + ' ' + sigDef['units']
    data.append(toolTipString)
    dataArray.append(data)
  dataList = dataArray

  return dataList
  
createData=createDataFromIridiumTime

def v2_graphV6(request):
  data = []
  onlyWantedData = []
  
  chart_main = None
  
  chartOptions = {}
  
  formFields = {}
  
  # formFields['mcuID'] = {}
  # formFields['mcuID']['label'] = 'Packet MCU ID'
  # formFields['mcuID']['options'] = ['ANY','1','2','3','4']
  # formFields['mcuID']['selected'] = request.GET.get('mcuID', 'ANY')
  
  mcuID = request.GET.get('mcuID', 'None')
  IMEI = request.GET.get('IMEI', 'None')

  

  # formFields['IMEI'] = {}
  # formFields['IMEI']['label'] = 'Iridium IMEI'
  # formFields['IMEI']['options'] = ['ANY', '300234065252710', '300434063219840', '300434063839690', '300434063766960', '300434063560100', '300434063184090', '300434063383330', '300434063185070', '300434063382350', '300234063778640', '888888888888888']
  # formFields['IMEI']['selected'] = request.GET.get('IMEI', 'ANY')
  
  formFields['leftAxisSignal_A'] = {}
  formFields['leftAxisSignal_A']['label'] = 'Left Axis Signal A'
  formFields['leftAxisSignal_A']['options'] = signalList
  formFields['leftAxisSignal_A']['selected'] = request.GET.get('leftAxisSignal_A', 'NONE')
  
  formFields['leftAxisSignal_B'] = {}
  formFields['leftAxisSignal_B']['label'] = 'Left Axis Signal B'
  formFields['leftAxisSignal_B']['options'] = signalList
  formFields['leftAxisSignal_B']['selected'] = request.GET.get('leftAxisSignal_B', 'NONE')
  
  formFields['leftAxisSignal_C'] = {}
  formFields['leftAxisSignal_C']['label'] = 'Left Axis Signal C'
  formFields['leftAxisSignal_C']['options'] = signalList
  formFields['leftAxisSignal_C']['selected'] = request.GET.get('leftAxisSignal_C', 'NONE')
  
  formFields['rightAxisSignal_A'] = {}
  formFields['rightAxisSignal_A']['label'] = 'Right Axis Signal A'
  formFields['rightAxisSignal_A']['options'] = signalList
  formFields['rightAxisSignal_A']['selected'] = request.GET.get('rightAxisSignal_A', 'NONE')
  
  formFields['rightAxisSignal_B'] = {}
  formFields['rightAxisSignal_B']['label'] = 'Right Axis Signal B'
  formFields['rightAxisSignal_B']['options'] = signalList
  formFields['rightAxisSignal_B']['selected'] = request.GET.get('rightAxisSignal_B', 'NONE')
  
  formFields['rightAxisSignal_C'] = {}
  formFields['rightAxisSignal_C']['label'] = 'Right Axis Signal C'
  formFields['rightAxisSignal_C']['options'] = signalList
  formFields['rightAxisSignal_C']['selected'] = request.GET.get('rightAxisSignal_C', 'NONE')
  
  filterOptions = {}
  
  filterOptions['windowStartRelative'] = request.GET.get('windowStartRelative', 'false')

  utcTimeNow =datetime.utcnow()

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
  
  windowStartTime = datetime.strptime(windowStartTimeString, "%Y-%m-%d %H:%M:%S")
  
  

  filterOptions['windowEndAtDate'] = request.GET.get('windowEndAtDate', utcTimeNow.strftime("%Y-%m-%d"))
  if filterOptions['windowEndAtDate'] == '':
    filterOptions['windowEndAtDate'] = utcTimeNow.strftime("%Y-%m-%d")
  filterOptions['windowEndAtHour'] = request.GET.get('windowEndAtHour', '23')
  filterOptions['windowEndAtMinute'] = request.GET.get('windowEndAtMinute', '59')
  filterOptions['windowEndAtSecond'] = request.GET.get('windowEndAtSecond', '59')
  
  windowEndTimeString = filterOptions['windowEndAtDate'] + ' '
  windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtHour'] + ':'
  windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtMinute'] + ':'
  windowEndTimeString = windowEndTimeString + filterOptions['windowEndAtSecond']
  
  windowEndTime = datetime.strptime(windowEndTimeString, "%Y-%m-%d %H:%M:%S")
  
  # chartTitle = "Battery Voltage"
  # chartDescription = "Measured voltages of the batteries."
  
  filteredDataRows = {}
  
  filteredDataRows['Request'] = models.Request.objects.all()
  filteredDataRows['IridiumTransmission'] = models.IridiumTransmission.objects.all()
  filteredDataRows['PacketV6'] = models.PacketV6.objects.all()
  filteredDataRows['PacketV6Units'] = models.PacketV6Units.objects.all()
  filteredDataRows['Measurements'] = models.Measurements.objects.all()
  filteredDataRows['MeasurementsUnits'] = models.MeasurementsUnits.objects.all()
  filteredDataRows['ConductivityMeasurements'] = models.ConductivityMeasurements.objects.all()
  filteredDataRows['ConductivityMeasurementsUnits'] = models.ConductivityMeasurementsUnits.objects.all()
  CommandHistory = models.UplinkRequest.objects.all()
  
  if(mcuID != 'None'):
    filteredDataRows['Request'] = filteredDataRows['Request'].filter(child_transmission__child_packet__mcu_id=int(mcuID))
    filteredDataRows['IridiumTransmission'] = filteredDataRows['IridiumTransmission'].filter(child_packet__mcu_id=int(mcuID))
    filteredDataRows['PacketV6'] = filteredDataRows['PacketV6'].filter(mcu_id=int(mcuID))
    filteredDataRows['PacketV6Units'] = filteredDataRows['PacketV6Units'].filter(parent_packet_v6__mcu_id=int(mcuID))
    filteredDataRows['Measurements'] = filteredDataRows['Measurements'].filter(parent_packet__mcu_id=int(mcuID))
    filteredDataRows['MeasurementsUnits'] = filteredDataRows['MeasurementsUnits'].filter(parent_measurements__parent_packet__mcu_id=int(mcuID))
    filteredDataRows['ConductivityMeasurements'] = filteredDataRows['ConductivityMeasurements'].filter(parent_packet__mcu_id=int(mcuID))
    filteredDataRows['ConductivityMeasurementsUnits'] = filteredDataRows['ConductivityMeasurementsUnits'].filter(parent_conductivity_measurements__parent_packet__mcu_id=int(mcuID))
    
  if(IMEI != 'None'):
    filteredDataRows['Request'] = filteredDataRows['Request'].filter(child_transmission__imei=int(IMEI))
    filteredDataRows['IridiumTransmission'] = filteredDataRows['IridiumTransmission'].filter(imei=int(IMEI))
    filteredDataRows['PacketV6'] = filteredDataRows['PacketV6'].filter(parent_transmission__imei=int(IMEI))
    filteredDataRows['PacketV6Units'] = filteredDataRows['PacketV6Units'].filter(parent_packet_v6__parent_transmission__imei=int(IMEI))
    filteredDataRows['Measurements'] = filteredDataRows['Measurements'].filter(parent_packet__parent_transmission__imei=int(IMEI))
    filteredDataRows['MeasurementsUnits'] = filteredDataRows['MeasurementsUnits'].filter(parent_measurements__parent_packet__parent_transmission__imei=int(IMEI))
    filteredDataRows['ConductivityMeasurements'] = filteredDataRows['ConductivityMeasurements'].filter(parent_packet__parent_transmission__imei=int(IMEI))
    filteredDataRows['ConductivityMeasurementsUnits'] = filteredDataRows['ConductivityMeasurementsUnits'].filter(parent_conductivity_measurements__parent_packet__parent_transmission__imei=int(IMEI))
  
  filteredDataRows_Iridium = copy.deepcopy(filteredDataRows)

  for key in filteredDataRows.keys():
    filteredDataRows[key] = filteredDataRows[key].filter(time__gte=windowStartTime).filter(time__lte=windowEndTime).order_by('-time')

  filteredDataRows_Iridium['Request'] = filteredDataRows_Iridium['Request'].filter(child_transmission__time__gte=windowStartTime).filter(child_transmission__time__lte=windowStartTime).order_by('-child_transmission__time')
  filteredDataRows_Iridium['IridiumTransmission'] = filteredDataRows_Iridium['IridiumTransmission'].filter(time__gte=windowStartTime).filter(time__lte=windowEndTime).order_by('-time')
  filteredDataRows_Iridium['PacketV6'] = filteredDataRows_Iridium['PacketV6'].filter(parent_transmission__time__gte=windowStartTime).filter(parent_transmission__time__lte=windowEndTime).order_by('-parent_transmission__time')
  filteredDataRows_Iridium['PacketV6Units'] = filteredDataRows_Iridium['PacketV6Units'].filter(parent_packet_v6__parent_transmission__time__gte=windowStartTime).filter(parent_packet_v6__parent_transmission__time__lte=windowEndTime).order_by('-parent_packet_v6__parent_transmission__time')
  filteredDataRows_Iridium['Measurements']=filteredDataRows_Iridium['Measurements'].filter(parent_packet__parent_transmission__time__gte=windowStartTime).filter(parent_packet__parent_transmission__time__lte=windowEndTime).order_by('-parent_packet__parent_transmission__time')
  filteredDataRows_Iridium['MeasurementsUnits'] = filteredDataRows_Iridium['MeasurementsUnits'].filter(parent_measurements__parent_packet__parent_transmission__time__gte=windowStartTime).filter(parent_measurements__parent_packet__parent_transmission__time__lte=windowEndTime).order_by('-parent_measurements__parent_packet__parent_transmission__time')
  filteredDataRows_Iridium['ConductivityMeasurements'] = filteredDataRows_Iridium['ConductivityMeasurements'].filter(parent_packet__parent_transmission__time__gte=windowStartTime).filter(parent_packet__parent_transmission__time__lte=windowEndTime).order_by('-parent_packet__parent_transmission__time')
  filteredDataRows_Iridium['ConductivityMeasurementsUnits'] = filteredDataRows_Iridium['ConductivityMeasurementsUnits'].filter(parent_conductivity_measurements__parent_packet__parent_transmission__time__gte=windowStartTime).filter(parent_conductivity_measurements__parent_packet__parent_transmission__time__lte=windowEndTime).order_by('-parent_conductivity_measurements__parent_packet__parent_transmission__time')


  
  for row in filteredDataRows['MeasurementsUnits']:
    row.vert1 = (row.vert1 - 2.048)    / (-0.5)
    row.vert2 = (row.vert2 - 2.048)    / (-0.5)
    row.vertD = (row.vertD - 2.048)    / (1/7)
    row.horiz1 = (row.horiz1 - 2.048)  / (-1.5)
    row.horiz2 = (row.horiz2 -  2.048) / (-1.5)
    row.horizD = (row.horizD - 2.048)  / (15)
  # uncutData = models.PacketV6Units.objects.filter(time__gte=datetime(2019, 8, 29)).all()

  # unfilteredData = models.PacketV6.objects.all()
  # filteredData = unfilteredData
  # if(formFields['mcuID']['selected'] != 'ANY'):
    # filteredData = filteredData.filter(mcu_id=int(formFields['mcuID']['selected']))
  # if(formFields['IMEI']['selected'] != 'ANY'):
    # filteredData = filteredData.filter(parent_transmission__imei=int(formFields['IMEI']['selected']))
  
  charts = {}

  chartOptions['tooltip'] = {
    'isHtml': True,
    'textStyle':{
      'fontSize': 24
    }
  }
  chartOptions['hAxis'] = {'format': 'MMM. dd, yyyy, HH:mm:ss'}
  chartOptions["pointSize"] = 3
  chartOptions['explorer'] = {
    'actions': ['dragToZoom', 'rightClickToReset'],
    'axis': 'horizontal',
    'keepInBounds': True,
    'maxZoomIn': 0.0
  }
  chartOptions['chartArea'] = {
    'width' : '80%',
    'heigth' : '80%'
  }

  chartOptions['height'] = '450px'

  toolTipColumn = {'type': 'string', 'role':'tooltip', 'p':{'html': True}}
  
  
  dataHeader = [[{'type': 'datetime', 'label': 'Time'}]]
  
  chartTitle = ""
  chartTitleList = []
  chartDescription = ""
  chartDescriptionList = []
  
  seriesIndex = 0
  
  chartOptions["series"] = {}
  
  leftAxisTitle = ""
  leftAxisTitleList = []
  rightAxisTitle = ""
  rightAxisTitleList = []
  
  #Loop through all the selected signals to create the dataHeader
  for signal in ['leftAxisSignal_A', 'leftAxisSignal_B', 'leftAxisSignal_C', 'rightAxisSignal_A', 'rightAxisSignal_B', 'rightAxisSignal_C']:
    signalId = formFields[signal]['selected']
    if( signalId == 'NONE'):
      continue
    sigDef = signalDefinitions[signalId]
    
    signalAxisTitle = sigDef['name'] + ' (' + sigDef['units'] + ') '
    targetAxisIndex = 0
    
    if(signal.split('Axis')[0] == 'left'):
      leftAxisTitleList.append(signalAxisTitle)
      targetAxisIndex = 0
    elif(signal.split('Axis')[0] == 'right'):
      rightAxisTitleList.append(signalAxisTitle)
      targetAxisIndex = 1
    else:
      raise ValueError
    
    chartOptions["series"][seriesIndex] = {"targetAxisIndex": targetAxisIndex}
    seriesIndex = seriesIndex + 1
    
    dataHeader[0].append(sigDef['name'])
    dataHeader[0].append(toolTipColumn)
    
    chartTitleList.append(sigDef['name']) 
    chartDescriptionList.append(sigDef['name'] + " (" + sigDef['description'] + ") " )
  
  chartTitle = ', '.join(chartTitleList)
  chartDescription = "A graph comprised of  the signals " + ', '.join(chartDescriptionList) + '.'
  
  leftAxisTitle = ', '.join(leftAxisTitleList)
  rightAxisTitle = ', '.join(rightAxisTitleList)
  
  
  chartOptions["vAxes"] = {0: {"title": leftAxisTitle}, 1: {"title": rightAxisTitle}}
  
  dataArray = []
  
  #Loop through all of the POTENTIAL tables of data
  for tableName in filteredDataRows.keys():
    #See if any of the chosen signals come from that table
      #If not, skip this one and look at the next one
    inThere = False
    for signal in ['leftAxisSignal_A', 'leftAxisSignal_B', 'leftAxisSignal_C', 'rightAxisSignal_A', 'rightAxisSignal_B', 'rightAxisSignal_C']:
      signalId = formFields[signal]['selected']
      if( signalId == 'NONE'):
        continue
      if signalId.split('___')[0] == tableName:
        inThere = True
    if(inThere):
      #If so, loop through each data row from that table
      for x in filteredDataRows[tableName]:
        #For each data row, append the timestamp to the current output data row
        data = [sJDS(x.time)]
        #Loop through the chosen signals
        for signal in ['leftAxisSignal_A', 'leftAxisSignal_B', 'leftAxisSignal_C', 'rightAxisSignal_A', 'rightAxisSignal_B', 'rightAxisSignal_C']:
          #Check if the current chosen signal is from the current table
          signalId = formFields[signal]['selected']
          if( signalId == 'NONE'):
            continue
          if signalId.split('___')[0] == tableName:
          #If so, append the data point to the current output data row
            #Then append the tooltip to the current output data row
            sigDef = signalDefinitions[signalId]
            sigName = sigDef['name']
            sigUnits = sigDef['units']
            sigValue = signalValue(x,signalId)
            data.append(sigValue)
            toolTipString = x.time.strftime("%b. %d, %Y, %H:%M:%S %Z\n" + sigName + ": "+str(sigValue))
            if(sigUnits):
              toolTipString = toolTipString + ' ' + sigUnits
            data.append(toolTipString)
          else:
          #If not, append None to the current output data row
            #Then append None (as the tooltip) to the current output data row
            data.append(None)
            data.append(None)
        dataArray.append(data)
  dataList = dataHeader + dataArray
  
  data_source_main = SimpleDataSource(data=dataList)
  chartOptions['title'] = chartTitle

  # charts['chart_main'] = LineChart(data_source_main, 'chart_main', options=chartOptions)


  chartOptions['series'] = {0:{"targetAxisIndex": 0}}
  data_source_V1C = createData('ConductivityMeasurementsUnits___vert1', filteredDataRows, 'ConductivityMeasurementsUnits',chartOptions)
  charts['chart_V1C'] = LineChart(data_source_V1C, 'chart_V1C', options=copy.deepcopy(chartOptions))

  data_source_V2C = createData('ConductivityMeasurementsUnits___vert2', filteredDataRows, 'ConductivityMeasurementsUnits', chartOptions)
  charts['chart_V2C'] = LineChart(data_source_V2C, 'chart_V2C', options=copy.deepcopy(chartOptions))

  data_source_V1 = createData('MeasurementsUnits___vert1', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_V1'] = LineChart(data_source_V1, 'chart_V1', options=copy.deepcopy(chartOptions))

  data_source_V2 = createData('MeasurementsUnits___vert2', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_V2'] = LineChart(data_source_V2, 'chart_V2', options=copy.deepcopy(chartOptions))

  data_source_VD = createData('MeasurementsUnits___vertD', filteredDataRows, 'MeasurementsUnits',chartOptions)  
  charts['chart_VD'] = LineChart(data_source_VD, 'chart_VD', options=copy.deepcopy(chartOptions))

  data_source_H1 = createData('MeasurementsUnits___horiz1', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_H1'] = LineChart(data_source_H1, 'chart_H1', options=copy.deepcopy(chartOptions))
  
  data_source_H2 = createData('MeasurementsUnits___horiz2', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_H2'] = LineChart(data_source_H2, 'chart_H2', options=copy.deepcopy(chartOptions))

  data_source_HD = createData('MeasurementsUnits___horizD', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_HD'] = LineChart(data_source_HD, 'chart_HD', options=copy.deepcopy(chartOptions))

  data_source_CX = createData('MeasurementsUnits___compassX', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_CX'] = LineChart(data_source_CX, 'chart_CX', options=copy.deepcopy(chartOptions))

  data_source_CY = createData('MeasurementsUnits___compassY', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_CY'] = LineChart(data_source_CY, 'chart_CY', options=copy.deepcopy(chartOptions))

  data_source_CZ = createData('MeasurementsUnits___compassZ', filteredDataRows, 'MeasurementsUnits',chartOptions)
  charts['chart_CZ'] = LineChart(data_source_CZ, 'chart_CZ', options=copy.deepcopy(chartOptions))

  data_source_lat = createData('PacketV6Units___latitude', filteredDataRows, 'PacketV6Units',chartOptions)
  charts['chart_lat'] = LineChart(data_source_lat, 'chart_lat', options=copy.deepcopy(chartOptions))

  data_source_long = createData('PacketV6Units___longitude', filteredDataRows, 'PacketV6Units',chartOptions)
  charts['chart_long'] = LineChart(data_source_long, 'chart_long', options=copy.deepcopy(chartOptions))

  data_source_alt = createData('PacketV6Units___altitude', filteredDataRows, 'PacketV6Units',chartOptions)
  charts['chart_alt'] = LineChart(data_source_alt, 'chart_alt', options=copy.deepcopy(chartOptions))

  data_source_alt_press = createData('PacketV6Units___altimeter_pressure', filteredDataRows, 'PacketV6Units',chartOptions)
  charts['chart_alt_press'] = LineChart(data_source_alt_press, 'chart_alt_press', options=copy.deepcopy(chartOptions))

  data_source_alt_temp = createData('PacketV6Units___altimeter_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_alt_temp'] = LineChart(data_source_alt_temp, 'chart_alt_temp', options=copy.deepcopy(chartOptions))

  data_source_batt_temp = createData('PacketV6Units___battery_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_batt_temp'] = LineChart(data_source_batt_temp, 'chart_batt_temp', options=copy.deepcopy(chartOptions))
  
  data_source_mcu_temp = createData('PacketV6Units___mcu_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_mcu_temp'] = LineChart(data_source_mcu_temp, 'chart_mcu_temp', options=copy.deepcopy(chartOptions))
  
  data_source_compass_temp = createData('PacketV6Units___compass_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_compass_temp'] = LineChart(data_source_compass_temp, 'chart_compass_temp', options=copy.deepcopy(chartOptions))

  data_source_adc1_temp = createData('PacketV6Units___adc1_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_adc1_temp'] = LineChart(data_source_adc1_temp, 'chart_adc1_temp', options=copy.deepcopy(chartOptions))

  data_source_adc2_temp = createData('PacketV6Units___adc2_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_adc2_temp'] = LineChart(data_source_adc2_temp, 'chart_adc2_temp', options=copy.deepcopy(chartOptions))
  
  data_source_ext_temp = createData('PacketV6Units___external_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_ext_temp'] = LineChart(data_source_ext_temp, 'chart_ext_temp', options=copy.deepcopy(chartOptions))

  data_source_RB_temp = createData('PacketV6Units___rockblock_temp', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_RB_temp'] = LineChart(data_source_RB_temp, 'chart_RB_temp', options=copy.deepcopy(chartOptions))

  data_source_positive_7V_volts = createData('PacketV6Units___positive_7v_battery_voltage', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_positive_7V_volts'] = LineChart(data_source_positive_7V_volts, 'chart_positive_7V_volts', options=copy.deepcopy(chartOptions))

  data_source_negative_7V_volts = createData('PacketV6Units___negative_7v_battery_voltage', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_negative_7V_volts'] = LineChart(data_source_negative_7V_volts, 'chart_negative_7V_volts', options=copy.deepcopy(chartOptions))

  data_source_positive_3V6_volts = createData('PacketV6Units___positive_3v6_battery_voltage', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_3V6_volts'] = LineChart(data_source_positive_3V6_volts, 'chart_3V6_volts', options=copy.deepcopy(chartOptions))

  data_source_current_7V = createData('PacketV6Units___current_draw_7v_rail', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_7V_current'] = LineChart(data_source_current_7V, 'chart_7V_current', options=copy.deepcopy(chartOptions))

  data_source_current_3V6 = createData('PacketV6Units___current_draw_3v3_rail', filteredDataRows, 'PacketV6Units', chartOptions)
  charts['chart_3V3_current'] = LineChart(data_source_current_3V6, 'chart_3V3_current', options=copy.deepcopy(chartOptions))

  data_source_packet_sequence = createData('PacketV6___sequence_id', filteredDataRows, 'PacketV6', chartOptions)
  charts['chart_sequenceID'] = LineChart(data_source_packet_sequence, 'chart_sequenceID', options=copy.deepcopy(chartOptions))

  data_aggregates = {}
  data_aggregates['Min'] = filteredDataRows['Measurements'].aggregate(Min('vert1'),Min('vert2'),Min('vertD'),
                                                                   Min('compassX'),Min('compassY'),Min('compassZ'),
                                                                   Min('horiz1'),Min('horiz2'),Min('horizD'))
  data_aggregates['Avg'] = filteredDataRows['Measurements'].aggregate(Avg('vert1'),Avg('vert2'),Avg('vertD'),
                                                                   Avg('compassX'),Avg('compassY'),Avg('compassZ'),
                                                                   Avg('horiz1'),Avg('horiz2'),Avg('horizD'))
  data_aggregates['Max'] = filteredDataRows['Measurements'].aggregate(Max('vert1'),Max('vert2'),Max('vertD'),
                                                                   Max('compassX'),Max('compassY'),Max('compassZ'),
                                                                   Max('horiz1'),Max('horiz2'),Max('horizD'))
  data_aggregates['MinUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Min('vert1'),Min('vert2'),Min('vertD'),
                                                                   Min('compassX'),Min('compassY'),Min('compassZ'),
                                                                   Min('horiz1'),Min('horiz2'),Min('horizD'))
  data_aggregates['AvgUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Avg('vert1'),Avg('vert2'),Avg('vertD'),
                                                                   Avg('compassX'),Avg('compassY'),Avg('compassZ'),
                                                                   Avg('horiz1'),Avg('horiz2'),Avg('horizD'))
  data_aggregates['MaxUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Max('vert1'),Max('vert2'),Max('vertD'),
                                                                   Max('compassX'),Max('compassY'),Max('compassZ'),
                                                                   Max('horiz1'),Max('horiz2'),Max('horizD'))

  dataHeader = [[{'type': 'datetime', 'label': 'Time'},
                  {'name' : 'Vertical Velocity', 'units' : 'm/s', 'description' : ''},
                  {'type': 'string', 'role':'tooltip', 'p':{'html': True}}]]  
  
  vertical_velocity_array = []
  for index in range(len(filteredDataRows['PacketV6'])-1):
    row1 = filteredDataRows['PacketV6'][index]
    row2 = filteredDataRows['PacketV6'][index+1]
    data = [sJDS(row1.time)]
    sigValue1 = signalValue(row1,'PacketV6___altitude')
    sigValue2 = signalValue(row2,'PacketV6___altitude')
    if(row1.time != row2.time):
      sigVal=(sigValue1-sigValue2)/((row1.time-row2.time).total_seconds())
    else:
        sigVal=0
    data.append(sigVal)
    toolTipString = row1.time.strftime("%b. %d, %Y, %H:%M:%S") + ' - ' + row2.time.strftime("%b. %d, %Y, %H:%M:%S\n Vertical Velocity: " + str(sigVal) +'m/s')
    data.append(toolTipString)
    vertical_velocity_array.append(data)
  vertical_velocity_data = dataHeader + vertical_velocity_array
  chartOptions['title'] = 'Vertical Velocity'
  chartOptions['vAxes'] = {0: {"title": 'Vertical Velocity'}}
  data_source_vertical_velocity = SimpleDataSource(data=vertical_velocity_data)
  charts['chart_vertical_velocity'] = LineChart(data_source_vertical_velocity,'chart_vertical_velocity', options=copy.deepcopy(chartOptions))

  last_vertical_velocity = None
  if (vertical_velocity_array):
    last_vertical_velocity = vertical_velocity_array[0][1] 

  color = 'grey'

  if(IMEI != 'None'):
    color = '#'+str(IMEI[-6:])

  if(mcuID == '1'):
    color = 'red'

  if(mcuID == '2'):
    color = 'green'

  if (mcuID == '3'):
    color = 'blue'

  if (mcuID == '4'):
    color = 'purple'

  
  last_packet_time='None'
  for key in filteredDataRows_Iridium:
    if(filteredDataRows_Iridium[key]):
      filteredDataRows_Iridium[key] = filteredDataRows_Iridium[key][0]
    if(filteredDataRows[key]):
      filteredDataRows[key] = filteredDataRows[key][0]
      

  if(filteredDataRows['PacketV6']):
    if(IMEI == 'None'):
      IMEI = filteredDataRows['IridiumTransmission'].imei
    if(mcuID == 'None'):
      mcuID = filteredDataRows['PacketV6'].mcu_id
    CommandHistory = CommandHistory.filter(imei=int(IMEI))
    last_packet_time = sJDS(filteredDataRows['PacketV6'].time)

  context = {
    'charts': charts,
    'title': chartTitle,
    'description': chartDescription,
    'hours': [str(x).zfill(2) for x in range(24)],
    'minutes': [str(x).zfill(2) for x in range(60)],
    'seconds': [str(x).zfill(2) for x in range(60)],
    'FormFields': formFields,
    'filterOptions' : filterOptions,
    'data' : filteredDataRows_Iridium,
    'aggregate_data' : data_aggregates,
    'IMEI' : IMEI,
    'mcuID': mcuID,
    'identifier_color': color,
    'command_history' : CommandHistory,
    'last_vert_vel' : last_vertical_velocity,
    'last_packet_time' : last_packet_time
    }
  #if request.GET.get('maxTime',None):
  # context['maxTime'] = request.GET.get('maxTime',None)
  #if request.GET.get('minTime',None):
  # context['minTime'] = request.GET.get('minTime',None)

  return render(request, 'groundstation/v2_newGraph.html', context)

def getNewPackets(request):
  
  lastDateTime = request.GET.get('lastDateTime', None)
  if(lastDateTime !=None):
    mcuID = request.GET.get('mcuID', None)

    if(mcuID != None):
      dateTimeObj = datetime.strptime(lastDateTime, "%a, %d %b %Y %H:%M:%S")
      filteredDataRows = {}

      filteredDataRows['Request'] = models.Request.objects.all()
      filteredDataRows['IridiumTransmission'] = models.IridiumTransmission.objects.all()
      filteredDataRows['PacketV6'] = models.PacketV6.objects.all()
      filteredDataRows['PacketV6Units'] = models.PacketV6Units.objects.all()
      filteredDataRows['Measurements'] = models.Measurements.objects.all()
      filteredDataRows['MeasurementsUnits'] = models.MeasurementsUnits.objects.all()
      filteredDataRows['ConductivityMeasurements'] = models.ConductivityMeasurements.objects.all()
      filteredDataRows['ConductivityMeasurementsUnits'] = models.ConductivityMeasurementsUnits.objects.all()
      
      filteredDataRows['Request'] = filteredDataRows['Request'].filter(child_transmission__child_packet__mcu_id=int(mcuID))
      filteredDataRows['IridiumTransmission'] = filteredDataRows['IridiumTransmission'].filter(child_packet__mcu_id=int(mcuID))
      filteredDataRows['PacketV6'] = filteredDataRows['PacketV6'].filter(mcu_id=int(mcuID))
      filteredDataRows['PacketV6Units'] = filteredDataRows['PacketV6Units'].filter(parent_packet_v6__mcu_id=int(mcuID))
      filteredDataRows['Measurements'] = filteredDataRows['Measurements'].filter(parent_packet__mcu_id=int(mcuID))
      filteredDataRows['MeasurementsUnits'] = filteredDataRows['MeasurementsUnits'].filter(parent_measurements__parent_packet__mcu_id=int(mcuID))
      filteredDataRows['ConductivityMeasurements'] = filteredDataRows['ConductivityMeasurements'].filter(parent_packet__mcu_id=int(mcuID))
      filteredDataRows['ConductivityMeasurementsUnits'] = filteredDataRows['ConductivityMeasurementsUnits'].filter(parent_conductivity_measurements__parent_packet__mcu_id=int(mcuID))

      for key in filteredDataRows.keys():
        filteredDataRows[key] = filteredDataRows[key].filter(time__gt=dateTimeObj).order_by('-time')

      data={}

      data['chart_V1C'] = createUpdateData('ConductivityMeasurements___vert1', filteredDataRows, 'ConductivityMeasurements')
      
      data['chart_V2C'] = createUpdateData('ConductivityMeasurements___vert2', filteredDataRows, 'ConductivityMeasurements')

      data['chart_V1'] = createUpdateData('Measurements___vert1', filteredDataRows, 'Measurements')

      data['chart_V2'] = createUpdateData('Measurements___vert2', filteredDataRows, 'Measurements')

      data['chart_VD'] = createUpdateData('Measurements___vertD', filteredDataRows, 'Measurements')  

      data['chart_H1'] = createUpdateData('Measurements___horiz1', filteredDataRows, 'Measurements')
      
      data['chart_H2'] = createUpdateData('Measurements___horiz2', filteredDataRows, 'Measurements')

      data['chart_HD'] = createUpdateData('Measurements___horizD', filteredDataRows, 'Measurements')

      data['chart_CX'] = createUpdateData('Measurements___compassX', filteredDataRows, 'Measurements')

      data['chart_CY'] = createUpdateData('Measurements___compassY', filteredDataRows, 'Measurements')

      data['chart_CZ'] = createUpdateData('Measurements___compassZ', filteredDataRows, 'Measurements')

      data['chart_lat'] = createUpdateData('PacketV6___latitude', filteredDataRows, 'PacketV6')

      data['chart_long'] = createUpdateData('PacketV6___longitude', filteredDataRows, 'PacketV6')

      data['chart_alt'] = createUpdateData('PacketV6___altitude', filteredDataRows, 'PacketV6')

      data['chart_alt_press'] = createUpdateData('PacketV6___altimeter_pressure', filteredDataRows, 'PacketV6')

      data['chart_alt_temp'] = createUpdateData('PacketV6Units___altimeter_temp', filteredDataRows, 'PacketV6')

      data['chart_batt_temp'] = createUpdateData('PacketV6Units___battery_temp', filteredDataRows, 'PacketV6')
      
      data['chart_mcu_temp'] = createUpdateData('PacketV6Units___mcu_temp', filteredDataRows, 'PacketV6')

      
      data['chart_compass_temp'] = createUpdateData('PacketV6Units___compass_temp', filteredDataRows, 'PacketV6')

      data['chart_adc1_temp'] = createUpdateData('PacketV6Units___adc1_temp', filteredDataRows, 'PacketV6')


      data['chart_adc2_temp'] = createUpdateData('PacketV6Units___adc2_temp', filteredDataRows, 'PacketV6')

      
      data['chart_ext_temp'] = createUpdateData('PacketV6Units___external_temp', filteredDataRows, 'PacketV6')

      data['chart_RB_temp'] = createUpdateData('PacketV6Units___rockblock_temp', filteredDataRows, 'PacketV6')

      data_aggregates = {}
      data_aggregates['Min'] = filteredDataRows['Measurements'].aggregate(Min('vert1'),Min('vert2'),Min('vertD'),
                                                                      Min('compassX'),Min('compassY'),Min('compassZ'),
                                                                      Min('horiz1'),Min('horiz2'),Min('horizD'))
      data_aggregates['Avg'] = filteredDataRows['Measurements'].aggregate(Avg('vert1'),Avg('vert2'),Avg('vertD'),
                                                                      Avg('compassX'),Avg('compassY'),Avg('compassZ'),
                                                                      Avg('horiz1'),Avg('horiz2'),Avg('horizD'))
      data_aggregates['Max'] = filteredDataRows['Measurements'].aggregate(Max('vert1'),Max('vert2'),Max('vertD'),
                                                                      Max('compassX'),Max('compassY'),Max('compassZ'),
                                                                      Max('horiz1'),Max('horiz2'),Max('horizD'))
      data_aggregates['MinUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Min('vert1'),Min('vert2'),Min('vertD'),
                                                                      Min('compassX'),Min('compassY'),Min('compassZ'),
                                                                      Min('horiz1'),Min('horiz2'),Min('horizD'))
      data_aggregates['AvgUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Avg('vert1'),Avg('vert2'),Avg('vertD'),
                                                                      Avg('compassX'),Avg('compassY'),Avg('compassZ'),
                                                                      Avg('horiz1'),Avg('horiz2'),Avg('horizD'))
      data_aggregates['MaxUnits'] = filteredDataRows['MeasurementsUnits'].aggregate(Max('vert1'),Max('vert2'),Max('vertD'),
                                                                      Max('compassX'),Max('compassY'),Max('compassZ'),
                                                                      Max('horiz1'),Max('horiz2'),Max('horizD'))
      
      last_vert_vel = 0
      if(len(filteredDataRows['PacketV6'])>1):
        vertical_velocity_array = []
        for index in range(len(filteredDataRows['PacketV6'])-1):
          row1 = filteredDataRows['PacketV6'][index]
          row2 = filteredDataRows['PacketV6'][index+1]
          data = [sJDS(row1.time)]
          sigValue1 = signalValue(row1,'PacketV6___altitude')
          sigValue2 = signalValue(row2,'PacketV6___altitude')
          sigVal=(sigValue1-sigValue2)/((row1.time-row2.time).total_seconds())
          data.append(sigVal)
          toolTipString = row1.time.strftime("%b. %d, %Y, %H:%M:%S") + ' - ' + row2.time.strftime("%b. %d, %Y, %H:%M:%S\n Vertical Velocity: " + sigVal +'m/s')
          data.append(toolTipString)
          vertical_velocity_array.append(data)
        last_vert_vel = vertical_velocity_array[0][1]
        data['Vert_vel'] = vertical_velocity_array

      jsonData = {}

      for key in filteredDataRows:
          if(filteredDataRows[key]):
            jsonData[key] = serializers.serialize('json',filteredDataRows[key])

      dataContext = {
        'data': jsonData,
        'chartData': data,
        'dataAggs': data_aggregates,
        'last_vertVel': last_vert_vel
      }

      
      if(len(filteredDataRows['PacketV6'])>0):
        return JsonResponse({'status': 'SUCCESS','isNewData': True, 'newData': dataContext}, safe=False)
      else:
        return JsonResponse({'status': 'SUCCESS', 'isNewData': False})
    else:
      return JsonResponse({'status': 'FAIL', 'reason': 'need_mcuID'})
  else:
    return JsonResponse({'status': 'FAIL', 'reason': 'need_last_packet_time'})
