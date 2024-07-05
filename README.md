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

## IOx app installation with CLI

For example on a Cisco IR1800 one can use this app in CLI mode. First download the IOx app on the router bootflash using your favourite method.

For example using SCP:

`router# copy scp://user@192.168.2.3/cisco/iox_aarch64_gps/iox_aarch64_gps-0.7.tar.gz bootflash:`

Install the app in exec mode:

`router# app-hosting install appid gps package flash:iox_aarch64_gps-0.7.tar.gz`

In configuration mode enter the app parameters:

```sh
app-hosting appid gps
  app-vnic gateway0 virtualportgroup 0 guest-interface 0
  app-resource docker
    run-opts 1 "-e DEBUG_VERBOSE=1"
    run-opts 2 "-e IR_GPS=/dev/NMEA0"
    run-opts 3 "--device /dev/ttyNMEA0:/dev/ttyNMEA0"
```

Lastly in exec mode, activate, and start the app:

```sh
router# app-hosting activate appid gps
router# app-hosting start appid gps
```

Verify if the app is running, should be like this:

```sh
router# sh app-hosting list
App id                                   State
---------------------------------------------------------
gps                                      RUNNING
```

## IOx app installation with Local Manager

TBD
