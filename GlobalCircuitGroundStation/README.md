# GlobalCircuitGroundStation

[Groundstation Site](gec.evanhiggins.net)

[Backup Site](gec.codyanderson.net)

The groundstation was used to monitor, communicate with, and collect data on launched research devices.
The site layout consists of a homepage, dashboard, location map, and a set of utility tools.

---

## Homepage
The homepage is simple but offers navigation to necessary functionalities.

### Features
#### Dashboard Navigation
Select the desired mcuID and the dashboard buttons will bring you to the cooresponding dashboard.
The secondary dashboard link acts as a backup in case gps time data is lost.

#### GPS Map
The GPS map offers a way to monitor the location of devices in flight.
The GPS map has controls within it to filter data.

### Info & Utilities
#### Uplink Command Instructions
[Uplink Instructions](https://github.com/keleuk/GlobalCircuit/wiki/Uplink-Commands)

This link takes you to to the instructions for sending uplink commands to devices in flight.
Allows volunteers to assist in sending commands if primary research members are unavailable.

#### Packet Structure
[Packete Structure](https://github.com/keleuk/GlobalCircuit/wiki/Packet)

This link takes you to the breakdown of the packet structure.

#### Google Earth Balloon Path .kml File
This download link is no longer functional.

#### CSV Files
This link takes the user to the options to download the collected data in csv format.

---

## Dashboard
This dashboard is the main way to monitor and communicate with devices in flight based on stored data

### Device Identifier Banner
The device identifier banner at the top and bottom of the page are color coded to help identify the device at a glance.
The banner also auto fills the device IMEI based on the most recent received packet.

### Time Frame Controls
The time frame controls allow for the user to choose what time frame of data the user would like to retrieve from the database.

### Auto Refresh Functionality
While asynchronous updating was under development, this option allowed users to tell the page to automatically refresh itself.

### Tabs
The tab layout allows for multiple sets of data tables to be on the same page without extensive scrolling.
#### Main
The main tab shows the most recent packet information.
#### Horizontal & Compass Graphs
The horizontal & compass tab contains graphs showing the horizontal probe measurements and compass data.
This data is paired due to the close connection to the two as the devices spins.
#### Vertical Probe Graphs
The vertical probe tab contains graphs showing the data measurements.
#### Location Graphs
The location tab contains graphs showing information regarding the device's longitude, latitude, altitude, and some book keeping information
#### Temperature Graphs
The temperature tab contains graphs showing the temperatures of various on board sensors and components. 
#### Voltage & Current Graphs
The voltage and current tab contains graphs showing book keeping values regaring voltage and current draw onboard the device in flight.
#### Advanced
The advanced tab is very similar to the main tab but contains agregate data in place of some other informaiton.
#### Uplink
The uplink tab is the main way of sending commands to the device in flight in order to drop ballasts or cutdown the device.

---

## GPS Map
The GPS map offers a more visual way to track the location of the device in flight.
On the right of the map are some controls.
The map is limited to 400 datapoints to avoid timeout issues.

### Time Frame Control
The time frame control allows the user to choose what time to start from.

### Packet MCU ID
The packet mcuID control allows the user to filter by mcuID

### Iridium IMEI
The iridium IMEI controll allows the user to filter by IMEI
