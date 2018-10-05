# Blink
Module to handle communication with the Blink REST API


## Documentation
Coming once I finish the make file to generate using sphinx, should end up in github pages

## Work in progress, the goal is to create an API class that only holds the REST endpoints, as well as manages the identity token for me
after that then I will create a wrapper class to handle the work load, and it will manage any business logic that is needed
### not sure if there is such a thing as multiple regions....if there is it would just expose the regions and I would have to handle passing in region for most calls


## Examples
### get list of networks for a given account
```python
from shraklor.blink import BlinkRestApi

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        print(network)

    blink = None
```


### get devices and print if camera, but not BlinkCameraXt
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule

    blink = BlinkRestApi(config['user_id'], config['password'])
    devices = blink.get_devices()

    for device in devices:
        if isinstance(device, BlinkCameraXt):
            pass
        elif isinstance(device, BlinkCamera):   # only print specific camera
            print(device)
        elif isinstance(device, BlinkSyncModule):
            pass

    blink = None
```


### arm all networks, not already armed
```python
from shraklor.blink import BlinkRestApi

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        if not network['armed']:
            blink.arm_network(network['id'])
            print('armed network {}'.format(network['name']))

    blink = None
```

### disarm all networks
```python
from shraklor.blink import BlinkRestApi

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        if network['armed']:
            blink.disarm_network(network['id'])
            print('disarmed network {}'.format(network['name']))

    blink = None
```


### get devices and print if camera, but not BlinkCameraXt
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule

    blink = BlinkRestApi(config['user_id'], config['password'])
    devices = blink.get_devices()

    for device in devices:
        if isinstance(device, BlinkCameraXt):
            pass
        elif isinstance(device, BlinkCamera):   # only print specific camera
            print(device)
        elif isinstance(device, BlinkSyncModule):
            pass

    blink = None
```


### go through all cameras and dis-arm if name matches something
```python
from shraklor.blink import BlinkRestApi, BlinkCamera

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        devices = blink.get_network_devices(network['id'])  #TODO: needs to be written still

        for device in devices:
            if not isinstance(device, BlinkCamera):
                continue

            camera_config = blink.get_camera_config(network['id'], device['device_id'])

            if device['name'] == 'upstairs-master':
                if camera_config['enabled']:
                    blink.disarm_camera(network['id'], device['device_id'])
            else:
                if not camera_config['enabled']:
                    blink.arm_camera(network['id'], device['device_id'])

    blink = None
```

### get details about a specific network
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule
import json

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        response = blink.get_network(network['id'])
        print(json.dumps(response, indent=4, sort_keys=True))

    blink = None
```

### get sync module for a network for details
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule
import json

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        response = blink.get_sync_modules(network['id'])
        print(json.dumps(response, indent=4, sort_keys=True))

    blink = None
```

### get events for a specific network
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule
import json

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        response = blink.get_events(network['id'])
        print(json.dumps(response, indent=4, sort_keys=True))

    blink = None
```


### get all the videos
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule
import json

    blink = BlinkRestApi(config['user_id'], config['password'])

    video_counts = blink.get_video_count()

    total = video_counts['count']
    page = 0
    count = 0
    while count < total:
        videos = blink.get_videos(page)
        count += len(videos)
        print(json.dumps(videos, indent=4, sort_keys=True))
        page += 1
        print('count: {}/ page: {}'.format(count, page))


    blink = None
```
