//When Document is loaded set up necessary functions
$(document).ready(function(){
    //uplink function
    $('#uplink_form').on('submit', function(e){
        e.preventDefault();
        console.log("uplink message sent")
        send_uplink();
    })
    //auto_refresh selection function
    $('#auto_fresh_check').click(function() {

        localStorage.setItem('auto_refresh',$('#auto_fresh_check').prop('checked'))
    
       });
    prepareCharts();
    if(localStorage.getItem('auto_refresh')=='true'){
        $("#auto_fresh_check").prop("checked", true);
    }
    //auto refresh
    setInterval(function(){ if($('#auto_fresh_check').prop('checked')){window.location.reload();} }, 60000);
})

//draw chart dictionary
drawChartFunctions = {
    "Main" : drawMainCharts,
    "HCD" : drawHCDCharts,
    "Probes" : drawProbeCharts,
    "Location" : drawLocationCharts,
    "Temperature" : drawTemperatureCharts,
    "Voltage_Current" : drawVoltage_CurrentCharts
}

//uplink function
function send_uplink(){
    console.log($('#utf8id').val())
    $.ajax({
        url : "/submit/",
        type : "POST",
        data : {
            imei : $('#imei').val(),
            message : $('#utf8id').val(),
            password : $('#password').val()
        },

        success : function(json){
            $('#password').val('');
            $('#utf8id').val('');
            successString = ""
            if(json.status != 403){
                successString = "SUCCESS"
            }
            else
            {
                successString = "FAILED"
            }
            $('#Command_Hist_Window').append("<span>["+json.time+"]("+json.imei+")"+json.message+" | SEND " +successString+" |</span><br>")
            $('#Command_Hist_Window').scrollTop($('#Command_Hist_Window')[0].scrollHeight);
        },

        error : function(xhr,errmsg,err){
            
        }
    });
}

//tab functionallity
function openTab(evt, tabName){
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i=0; i<tabcontent.length; i++){
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i=0; i<tablinks.length; i++){
        tablinks[i].className = tablinks[i].className.replace(" active","");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    var lastOpen = JSON.parse(localStorage.getItem("LastOpen"))
    lastOpen[mcuID-1]=tabName+"Tab"
    localStorage.setItem("LastOpen", JSON.stringify(lastOpen))

    if(tabName == "Uplink")
        $('#Command_Hist_Window').scrollTop($('#Command_Hist_Window')[0].scrollHeight);

    if(tabName in drawChartFunctions)
        drawChartFunctions[tabName]();
}

//draw the main chart (Legacy)
function drawMainCharts(){
    // var main_chart = new google.visualization.LineChart(document.getElementById('chart_main'))
    // main_chart.draw(chart_main_data, chart_main_options)
}

//draw the horizontal and compas data charts
function drawHCDCharts(){
    var H1_chart = new google.visualization.LineChart(document.getElementById('chart_H1'))
    var H2_chart = new google.visualization.LineChart(document.getElementById('chart_H2'))
    var HD_chart = new google.visualization.LineChart(document.getElementById('chart_HD'))
    var CX_chart = new google.visualization.LineChart(document.getElementById('chart_CX'))
    var CY_chart = new google.visualization.LineChart(document.getElementById('chart_CY'))
    var CZ_chart = new google.visualization.LineChart(document.getElementById('chart_CZ'))
    H1_chart.draw(chart_H1_data, chart_H1_options)
    H2_chart.draw(chart_H2_data, chart_H2_options)
    HD_chart.draw(chart_HD_data, chart_HD_options)
    CX_chart.draw(chart_CX_data, chart_CX_options)
    CY_chart.draw(chart_CY_data, chart_CY_options)
    CZ_chart.draw(chart_CZ_data, chart_CZ_options)
}

//draw the probe data charts
function drawProbeCharts(){
    var V1C_chart = new google.visualization.LineChart(document.getElementById('chart_V1C'))
    var V2C_chart = new google.visualization.LineChart(document.getElementById('chart_V2C'))
    var V1_chart = new google.visualization.LineChart(document.getElementById('chart_V1'))
    var V2_chart = new google.visualization.LineChart(document.getElementById('chart_V2'))
    var VD_chart = new google.visualization.LineChart(document.getElementById('chart_VD'))
    V1C_chart.draw(chart_V1C_data, chart_V1C_options)
    V2C_chart.draw(chart_V2C_data, chart_V2C_options)
    V1_chart.draw(chart_V1_data, chart_V1_options)
    V2_chart.draw(chart_V2_data, chart_V2_options)
    VD_chart.draw(chart_VD_data, chart_VD_options)
}

//draw the locaiton information charts
function drawLocationCharts(){
    var lat_chart = new google.visualization.LineChart(document.getElementById('chart_lat'))
    var long_chart = new google.visualization.LineChart(document.getElementById('chart_long'))
    var alt_chart = new google.visualization.LineChart(document.getElementById('chart_alt'))
    var alt_press_chart = new google.visualization.LineChart(document.getElementById('chart_alt_press'))
    var vert_vel_chart = new google.visualization.LineChart(document.getElementById('chart_vertical_velocity'))
    var seqID_chart = new google.visualization.LineChart(document.getElementById('chart_sequenceID'))
    lat_chart.draw(chart_lat_data, chart_lat_options)
    long_chart.draw(chart_long_data, chart_long_options)
    alt_chart.draw(chart_alt_data, chart_alt_options)
    alt_press_chart.draw(chart_alt_press_data, chart_alt_press_options)
    vert_vel_chart.draw(chart_vertical_velocity_data, chart_vertical_velocity_options)
    seqID_chart.draw(chart_sequenceID_data, chart_sequenceID_options)

}

//draw the temperature data charts
function drawTemperatureCharts(){
    var alt_temp_chart = new google.visualization.LineChart(document.getElementById('chart_alt_temp'))
    var batt_temp_chart = new google.visualization.LineChart(document.getElementById('chart_batt_temp'))
    var mcu_temp_chart = new google.visualization.LineChart(document.getElementById('chart_mcu_temp'))
    var compass_temp_chart = new google.visualization.LineChart(document.getElementById('chart_compass_temp'))
    var adc1_temp_chart = new google.visualization.LineChart(document.getElementById('chart_adc1_temp'))
    var adc2_temp_chart = new google.visualization.LineChart(document.getElementById('chart_adc2_temp'))
    var ext_temp_chart = new google.visualization.LineChart(document.getElementById('chart_ext_temp'))
    var RB_temp_chart = new google.visualization.LineChart(document.getElementById('chart_RB_temp'))
    alt_temp_chart.draw(chart_alt_temp_data, chart_alt_temp_options)
    batt_temp_chart.draw(chart_batt_temp_data, chart_batt_temp_options)
    mcu_temp_chart.draw(chart_mcu_temp_data, chart_mcu_temp_options)
    compass_temp_chart.draw(chart_compass_temp_data, chart_compass_temp_options)
    adc1_temp_chart.draw(chart_adc1_temp_data, chart_adc1_temp_options)
    adc2_temp_chart.draw(chart_adc2_temp_data, chart_adc2_temp_options)
    ext_temp_chart.draw(chart_ext_temp_data, chart_ext_temp_options)
    RB_temp_chart.draw(chart_RB_temp_data, chart_RB_temp_options)
}

//draw the voltage and current charts
function drawVoltage_CurrentCharts(){
    var positive_7V_Volts_chart = new google.visualization.LineChart(document.getElementById('chart_positive_7V_volts'))
    var negative_7V_Volts_chart = new google.visualization.LineChart(document.getElementById('chart_negative_7V_volts'))
    var postive_3V6_Volts_chart = new google.visualization.LineChart(document.getElementById('chart_3V6_volts'))
    var current_7V_chart = new google.visualization.LineChart(document.getElementById('chart_7V_current'))
    var current_3V3_chart = new google.visualization.LineChart(document.getElementById('chart_3V3_current'))
    positive_7V_Volts_chart.draw(chart_positive_7V_volts_data, chart_positive_7V_volts_options)
    negative_7V_Volts_chart.draw(chart_negative_7V_volts_data, chart_negative_7V_volts_options)
    postive_3V6_Volts_chart.draw(chart_3V6_volts_data, chart_3V6_volts_options)
    current_7V_chart.draw(chart_7V_current_data, chart_7V_current_options)
    current_3V3_chart.draw(chart_3V3_current_data, chart_3V3_current_options)
}

//async update
function getNewPackets(){
    $.ajax({
        url : "/getUpdate/",
        type : "GET",
        data : {
            mcuID : mcuID,
            lastDateTime : newestPacketTime.toGMTString().replace(' GMT','')
        },

        success : function(json){
            console.log(json)
            if(json.status=='SUCCESS'){
                if(json.isNewData == true){
                    newData = json.newData.data
                    newChartData = json.newData.chartData
                    newAggs = json.newData.dataAggs
                    lastVertVel = json.newData.last_vertVel
                    for(key in newData){
                        newData[key] = JSON.parse(newData[key])
                    }
                    console.log(newData)
                    //update vals
                    $("[name='yikes_status']").text(newData.PacketV6.yikes_status)
                    $("[name='yikes_status_units']").text(newData.PacketV6Units.yikes_status)
                    $("[name='mcu_id']").text(newData.PacketV6.mcu_id)
                    $("[name='mcu_id_units']").text(newData.PacketV6Units.mcu_id)
                    $("[name='packet_version']").text(newData.PacketV6.version)
                    $("[name='packet_version_units']").text(newData.PacketV6Units.version)
                    $("[name='sequence_id']").text(newData.PacketV6.sequence_id)
                    $("[name='sequence_id_units']").text(newData.PacketV6Units.sequence_id)
                    $("[name='packet_time']").text(newData.PacketV6.time)
                    $("[name='packet_time_units']").text(newData.PacketV6Units.time)
                    $("[name='lat']").text(newData.PacketV6.latitude)
                    $("[name='lat_units']").text(newData.PacketV6Units.latitude)
                    $("[name='long']").text(newData.PacketV6.longitude)
                    $("[name='long_units']").text(newData.PacketV6Units.longitude)
                    $("[name='altitude']").text(newData.PacketV6.altitude)
                    $("[name='altitude_units']").text(newData.PacketV6Units.altitude)
                    $("[name='ball_status']").text(newData.PacketV6.ballast_status)
                    $("[name='ball_status_units']").text(newData.PacketV6Units.ballast_status)
                    $("[name='cutd_status']").text(newData.PacketV6.cutdown_status)
                    $("[name='cutd_status_units']").text(newData.PacketV6Units.cutdown_status)
                    $("[name='conductivity_time']").text(newData.PacketV6.conductivity_time)
                    $("[name='conductivity_time_units']").text(newData.PacketV6Units.conductivity_time)
                    $("[name='sat_count']").text(newData.PacketV6.satellites_count)
                    $("[name='sat_count_units']").text(newData.PacketV6Units.satellites_count)
                    $("[name='command_count']").text(newData.PacketV6.commands_count)
                    $("[name='command_count_units']").text(newData.PacketV6Units.commands_count)
                    $("[name='altimeter_temp']").text(newData.PacketV6.altimeter_temp)
                    $("[name='altimeter_temp_units']").text(newData.PacketV6Units.altimeter_temp)
                    $("[name='altimeter_pressure']").text(newData.PacketV6.altimeter_pressure)
                    $("[name='altimeter_pressure_units']").text(newData.PacketV6Units.altimeter_pressure)
                    $("[name='positive_7v_batt_V']").text(newData.PacketV6.positive_7v_battery_voltage)
                    $("[name='positive_7v_batt_V_units']").text(newData.PacketV6Units.positive_7v_battery_voltage)
                    $("[name='negative_7v_vatt_V']").text(newData.PacketV6.negative_7v_battery_voltage)
                    $("[name='negative_7v_vatt_V_units']").text(newData.PacketV6Units.negative_7v_battery_voltage)
                    $("[name='3v6_batt_V']").text(newData.PacketV6.positive_3v6_battery_voltage)
                    $("[name='3v6_batt_V_units']").text(newData.PacketV6Units.positive_3v6_battery_voltage)
                    $("[name='7v_current']").text(newData.PacketV6.current_draw_7v_rail)
                    $("[name='7v_current_units']").text(newData.PacketV6Units.current_draw_7v_rail)
                    $("[name='3v3_current']").text(newData.PacketV6.current_draw_3v3_rail)
                    $("[name='3v3_current_units']").text(newData.PacketV6Units.current_draw_3v3_rail)
                    $("[name='batt_temp']").text(newData.PacketV6.battery_temp)
                    $("[name='batt_temp_units']").text(newData.PacketV6Units.battery_temp)
                    $("[name='mcu_temp']").text(newData.PacketV6.mcu_temp)
                    $("[name='mcu_temp_units']").text(newData.PacketV6Units.mcu_temp)
                    $("[name='compass_temp']").text(newData.PacketV6.compass_temp)
                    $("[name='compass_temp_units']").text(newData.PacketV6Units.compass_temp)
                    $("[name='adc1_temp']").text(newData.PacketV6.adc1_temp)
                    $("[name='adc1_temp_units']").text(newData.PacketV6Units.adc1_temp)
                    $("[name='adc2_temp']").text(newData.PacketV6.adc2_temp)
                    $("[name='adc2_temp_units']").text(newData.PacketV6Units.adc2_temp)
                    $("[name='external_temp']").text(newData.PacketV6.external_temp)
                    $("[name='external_temp_units']").text(newData.PacketV6Units.external_temp)
                    $("[name='RB_temp']").text(newData.PacketV6.rockblock_temp)
                    $("[name='RB_temp_units']").text(newData.PacketV6Units.rockblock_temp)
                    $("[name='vert_vel']").text(lastVertVel)
                    $("[name='horiz1_units']").text(newData.MeasurementsUnits.horiz1)
                    $("[name='horiz2_units']").text(newData.MeasurementsUnits.horiz2)
                    $("[name='horizD_units']").text(newData.MeasurementsUnits.horizD)
                    $("[name='vert1_units']").text(newData.MeasurementsUnits.vert1)
                    $("[name='vert2_units']").text(newData.MeasurementsUnits.vert2)
                    $("[name='vertD_units']").text(newData.MeasurementsUnits.vertD)
                    if(newData.ConductivityMeasurementsUnits){
                        $("[name='V1_Probe_Cond_units']").text(newData.ConductivityMeasurementsUnits.vert1)
                        $("[name='V2_Probe_Cond_units']").text(newData.ConductivityMeasurementsUnits.vert2)
                    }
                    $("[name='compass_X_units']").text(newData.MeasurementsUnits.compassX)
                    $("[name='compass_Y_units']").text(newData.MeasurementsUnits.compassY)
                    $("[name='compass_Z_units']").text(newData.MeasurementsUnits.compassZ)
                    $("[name='iridium_time']").text(newData.IridiumTransmission.time)
                    $("[name='iridium_lat']").text(newData.IridiumTransmission.latitude)
                    $("[name='iridium_long']").text(newData.IridiumTransmission.longitude)
                    $("[name='iridium_cep']").text(newData.IridiumTransmission.cep)
                    $("[name='iridium_momsn']").text(newData.IridiumTransmission.momsn)
                    $("[name='iridium_imei']").text(newData.IridiumTransmission.imei)
                    $("[name='device_type']").text(newData.IridiumTransmission.device_type)
                    $("[name='serial']").text(newData.IridiumTransmission.serial)
                    $("[name='session_status']").text(newData.IridiumTransmission.iridium_session_status)
                    $("[name='via_sat']").text(newData.IridiumTransmission.transmitted_via_satellite)
                    $("[name='vert1_agg_min']").text(newAggs.Min.vert1__min)
                    $("[name='vert1_agg_avg']").text(newAggs.Avg.vert1__avg)
                    $("[name='vert1_agg_max']").text(newAggs.Max.vert1__max)
                    $("[name='vert1_units_agg_min']").text(newAggs.MinUnits.vert1__min)
                    $("[name='vert1_units_agg_avg']").text(newAggs.AvgUnits.vert1__avg)
                    $("[name='vert1_units_agg_max']").text(newAggs.MaxUnits.vert1__max)
                    $("[name='vert2_agg_min']").text(newAggs.Min.vert2__min)
                    $("[name='vert2_agg_avg']").text(newAggs.Avg.vert2__avg)
                    $("[name='vert2_agg_max']").text(newAggs.Max.vert2__max)
                    $("[name='vert2_units_agg_min']").text(newAggs.MinUnits.vert2__min)
                    $("[name='vert2_units_agg_avg']").text(newAggs.AvgUnits.vert2__avg)
                    $("[name='vert2_units_agg_max']").text(newAggs.MaxUnits.vert2__max)
                    $("[name='horiz1_agg_min']").text(newAggs.Min.horiz1__min)
                    $("[name='horiz1_agg_avg']").text(newAggs.Avg.horiz1__avg)
                    $("[name='horiz1_agg_max']").text(newAggs.Max.horiz1__max)
                    $("[name='horiz1_units_agg_min']").text(newAggs.MinUnits.horiz1__min)
                    $("[name='horiz1_units_agg_avg']").text(newAggs.AvgUnits.horiz1__avg)
                    $("[name='horiz1_units_agg_max']").text(newAggs.MaxUnits.horiz1__max)
                    $("[name='horiz2_agg_min']").text(newAggs.Min.horiz2__min)
                    $("[name='horiz2_agg_avg']").text(newAggs.Avg.horiz2__avg)
                    $("[name='horiz2_agg_max']").text(newAggs.Max.horiz2__max)
                    $("[name='horiz2_units_agg_min']").text(newAggs.MinUnits.horiz2__min)
                    $("[name='horiz2_units_agg_avg']").text(newAggs.AvgUnits.horiz2__avg)
                    $("[name='horiz2_units_agg_max']").text(newAggs.MaxUnits.horiz2__max)
                    $("[name='horizd_agg_min']").text(newAggs.Min.horizD__min)
                    $("[name='horizd_agg_avg']").text(newAggs.Avg.horizD__avg)
                    $("[name='horizd_agg_max']").text(newAggs.Max.horizD__max)
                    $("[name='horizd_units_agg_min']").text(newAggs.MinUnits.horizD__min)
                    $("[name='horizd_units_agg_avg']").text(newAggs.AvgUnits.horizD__avg)
                    $("[name='horizd_units_agg_max']").text(newAggs.MaxUnits.horizD__max)
                    $("[name='compassX_agg_min']").text(newAggs.Min.compassX__min)
                    $("[name='compassX_agg_avg']").text(newAggs.Avg.compassX__avg)
                    $("[name='compassX_agg_max']").text(newAggs.Max.compassX__max)
                    $("[name='compassX_units_agg_min']").text(newAggs.MinUnits.compassX__min)
                    $("[name='compassX_units_agg_avg']").text(newAggs.AvgUnits.compassX__avg)
                    $("[name='compassX_units_agg_max']").text(newAggs.MaxUnits.compassX__max)
                    $("[name='compassY_agg_min']").text(newAggs.Min.compassY__min)
                    $("[name='compassY_agg_avg']").text(newAggs.Avg.compassY__avg)
                    $("[name='compassY_agg_max']").text(newAggs.Max.compassY__max)
                    $("[name='compassY_units_agg_min']").text(newAggs.MinUnits.compassY__min)
                    $("[name='compassY_units_agg_avg']").text(newAggs.AvgUnits.compassY__avg)
                    $("[name='compassY_units_agg_max']").text(newAggs.MaxUnits.compassY__max)
                    $("[name='compassZ_agg_min']").text(newAggs.Min.compassZ__min)
                    $("[name='compassZ_agg_avg']").text(newAggs.Avg.compassZ__avg)
                    $("[name='compassZ_agg_max']").text(newAggs.Max.compassZ__max)
                    $("[name='compassZ_units_agg_min']").text(newAggs.MinUnits.compassZ__min)
                    $("[name='compassZ_units_agg_avg']").text(newAggs.AvgUnits.compassZ__avg)
                    $("[name='compassZ_units_agg_max']").text(newAggs.MaxUnits.compassZ__max)

                    //update chartData
                }
            }
        },

        error : function(xhr,errmsg,err){
            
        }
    });
}
