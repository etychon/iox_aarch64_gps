# iox_aarch64_gps
Cisco IOx application that gathers GPS information and publishes it on an MQTT server. Uses multi-threaded producer/consumer and a queue system to as a store-and-forward when network is not available.

This code is based on an initial work by Kevin Holcomb. 

## List of changes
* Using /dev/NMEA0 device as a normal file and not a serial device with pySerial.
* Split the monolithic main code into two threads - the producer gets the GPS data and add it to the queue, the consumer watch the queue and publishes the data to MQTT 
* Added support for local router timestamp as well as GPS-sourced timestamped
* Added a build process that will automatically increate the IOx app version number for each build (build.sh)

## Todo or unfinished
* Queue system will store the last position fix while unable to send data (store and forward)
