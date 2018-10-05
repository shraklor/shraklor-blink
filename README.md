# Blink
Module to handle communication with the Blink REST API


## Documentation
Coming once I finish the make file to generate using sphinx, should end up in github pages

## Work in progress, the goal is to create an API class that only holds the REST endpoints, as well as manages the identity token for me


## TODO
#### rate limiting - what to do if exceeded? queue calls???
#### wrapper for the API to handle any business logic (ie. make sure network is armed before arming camera)
#### wrap regions in case the system allows multiple regions (default to region[0] if only 1)
#### wrapper should handle saving files (thumbnails, videos)


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
            blink.arm_network(network)
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
            blink.disarm_network(network)
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
        devices = blink.get_network_devices(network)

        for device in devices:
            if not isinstance(device, BlinkCamera):
                continue

            camera_config = blink.get_camera_config(network['id'], device['device_id'])

            if device['name'] == 'upstairs-master':
                if camera_config['enabled']:
                    blink.disarm_camera(network, device)
            else:
                if not camera_config['enabled']:
                    blink.arm_camera(network, device)

    blink = None
```

### get details about a specific network
```python
from shraklor.blink import BlinkRestApi, BlinkCamera, BlinkCameraXt, BlinkSyncModule
import json

    blink = BlinkRestApi(config['user_id'], config['password'])
    networks = blink.get_networks()

    for network in networks:
        response = blink.get_network(network)
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
        response = blink.get_sync_modules(network)
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
        response = blink.get_events(network)
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
