'''
help with controllering blink cameras and other blink related tasks

Author:  shraklor

Target:  python3
'''
import logging
import json
from datetime import datetime, timedelta
import warnings

from shraklor.http import Http


class BlinkRateLimitExceededException(Exception):
    '''
    used to raise an exception when too many calls are made within
    a specified time limit
    '''
    pass


class BlinkUnknownDevice(Exception):
    ''' informs us of unknown devices '''

    def __init__(self, device, specific):
        ''' init '''
        super().__init__('Unknown device type {0}.{1}'.format(device, specific))


class BlinkUrls():  # pylint: disable=too-few-public-methods
    '''
    helper class to manage URLs
    '''
    scheme = 'https'
    domain = 'immedia-semi.com'
    fqdn = 'prod.{0}'.format(domain)
    login = '{0}://rest.{1}/login'.format(scheme, fqdn)

    @staticmethod
    def root_url(region):
        '''
        generates the root URL with the region in it
        '''
        return '{0}://rest.{1}.{2}'.format(BlinkUrls.scheme,
                                           region,
                                           BlinkUrls.domain)


class BlinkAuthService(): #pylint: disable=too-many-instance-attributes
    '''
    manages getting the Blink auth token
    '''
    _HEADER = {'Content-Type': 'application/json', 'Host': BlinkUrls.fqdn}
    _CLIENT = 'iPhone 9.2 | 2.2 | 222'
    _TOKEN_EXPIRATION = 60 * 5      # 5 minutes
    _TOKEN_NEAR_EXPIRATION = 10     # seconds
    _HTTP_TIMEOUT = 5
    LOG_FORMAT = '%(asctime)-15s [%(levelname)-8s] %(module)-32s %(message)s'

    def __init__(self, email, password, **kwargs):
        '''
        init
        '''
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format=self.LOG_FORMAT)
        self.logger.setLevel(logging.WARNING)

        self._email = email
        self._password = password
        self._client = kwargs.get('client', self._CLIENT)
        self._header = kwargs.get('header', self._HEADER)
        self._proxy = kwargs.get('proxy', None)
        self._token = None
        self._expires = datetime.now()
        self.logger.debug(self._header)
        self._region = None


    def _renew(self):
        '''
        renews for new token
        '''
        expired = (self._expires - datetime.now()).total_seconds() < self._TOKEN_NEAR_EXPIRATION

        if self._token is None or expired:
            data = {}
            data['email'] = self._email
            data['password'] = self._password
            data['client_specifier'] = self._client

            response = Http.call('POST',
                                 url=BlinkUrls.login,
                                 data=data,
                                 header=self._header,
                                 proxy=self._proxy,
                                 timeout=self._HTTP_TIMEOUT)

            response = response.json()

            if 'message' in response:
                raise Exception(response['message'])

            self.logger.debug(response)
            self._token = response['authtoken']['authtoken']
            self._expires = datetime.now() + timedelta(seconds=self._TOKEN_EXPIRATION)
            self._region = response['region']


    @property
    def region(self):
        '''
        returns the region from the login response
        '''
        self._renew()

        return self._region


    def token(self):
        '''
        checks to see if current token valid, else renews
        '''
        self._renew()

        return self._token


class BlinkData(dict):
    ''' device that represents a Blink Data Class '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        dict.__init__(self)
        self.update(*args, **kwargs)


class BlinkNetwork(BlinkData):
    ''' class to track the data corresponding to a network '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkData.__init__(self, *args, **kwargs)


class BlinkCamera(BlinkData):
    ''' device that represents a Blink XT Camera '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkData.__init__(self, *args, **kwargs)


class BlinkCameraXt(BlinkCamera):
    ''' device that represents a Blink XT Camera '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkCamera.__init__(self, *args, **kwargs)


class BlinkCameraWhite(BlinkCamera):
    ''' device that represents a Blink Camera '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkCamera.__init__(self, *args, **kwargs)


class BlinkSyncModule(BlinkData):
    ''' device that represents a Blink Sync Module '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkData.__init__(self, *args, **kwargs)


class BlinkEvent(BlinkData):
    ''' device that represents a Blink Sync Module '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkData.__init__(self, *args, **kwargs)


class BlinkVideo(BlinkData):
    ''' device that represents a Blink Sync Module '''

    def __init__(self, *args, **kwargs):
        ''' init '''
        BlinkData.__init__i(self, *args, **kwargs)




class BlinkFactory():
    ''' class to track the data corresponding to a homescreen '''

    @staticmethod
    def load_data(data):
        '''
        loops through response to load new instances of BlinkData
        '''
        if not data:
            return None

        return BlinkData(**data)


    @staticmethod
    def load_camera_config(data):
        '''
        loops through response to load new instances of BlinkData
        '''
        if not data:
            return None

        return BlinkData(**data['camera'][0])


    @staticmethod
    def load_videos(data):
        '''
        loops through response to load new instances of BlinkData
        '''
        results = []
        if not data:
            return None

        for record in data:
            results.append(BlinkVideo(**record))

        return results


    @staticmethod
    def load_events(data):
        '''
        loops through response to load new instances of BlinkData
        '''
        results = []
        if not data:
            return None

        for record in data['event']:
            results.append(BlinkEvent(**record))

        return results


    @staticmethod
    def load_network(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkData
        '''
        results = []
        if not data:
            return None

        key = 'network'
        if 'networks' in data:
            key = 'networks'

        for record in data[key]:
            results.append(BlinkNetwork(**record))

        return results


    @staticmethod
    def load_sync_modules(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkData
        '''
        results = []
        if not data:
            return None

        if 'devices' not in data:
            return None

        for record in data['syncmodule']:
            results.append(BlinkSyncModule(**record))

        return results


    @staticmethod
    def load_devices(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkData
        '''
        results = []
        if not data:
            return None

        if 'devices' not in data:
            return None

        for record in data['devices']:
            if 'device_type' in record:
                device_type = record['device_type']

                if device_type == 'camera':
                    typ = record['type']
                    if typ == 'xt':
                        results.append(BlinkCameraXt(**record))
                    elif typ == 'white':
                        results.append(BlinkCameraWhite(**record))
                    else:
                        raise BlinkUnknownDevice(device_type, typ)
                elif device_type == 'sync_module':
                    results.append(BlinkSyncModule(**record))
                else:
                    raise BlinkUnknownDevice(device_type, None)
            else:
                raise BlinkUnknownDevice('Unknown', None)

        return results







class BlinkRestApi():
    '''
    handles calls to Rest API
    '''

    _DEFAULT_HEADER = {'Content-Type': 'application/json'}
    MAXIMUM_CALLS_PER_MINUTE = 10
    LOG_FORMAT = '%(asctime)-15s [%(levelname)-8s] %(funcName)-32s %(lineno)3d %(message)s'

    def __init__(self, user_id, password, **kwargs):
        '''
        init
            user_id (str): user email address for Blink
            password (str): password for blink account
            kwargs can contain:
                header, client, or HTTP proxy
        '''
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format=self.LOG_FORMAT)
        self.logger.setLevel(logging.DEBUG)

        client = kwargs.get('client', None)
        if client:
            self._blink_auth = BlinkAuthService(user_id, password, client=client)
        else:
            self._blink_auth = BlinkAuthService(user_id, password)


        self._header = kwargs.get('header', self._DEFAULT_HEADER)
        proxy = kwargs.get('proxy', {})

        self._http = Http(header=self._header, proxy=proxy)

        self._auth_token = None
        self._http_rates = {'calls': [], 'max': self.MAXIMUM_CALLS_PER_MINUTE}


    def _build_header(self):
        '''
        creates the HTTP header with latest token info
            from the BlinkAuthService
        '''
        header = self._header.copy()
        token = self._blink_auth.token()
        header.update({'TOKEN_AUTH': token})
        header.update({'HOST': '{0}.{1}'.format(self._region, BlinkUrls.domain)})

        return header


    def _call(self, method, url, data=None):
        '''
        make HTTP call using to Url, always return back the JSON
        '''
        header = self._build_header()
        self.logger.debug(header)
        self.logger.info('%s %s', method, url)
        response = self._http.send(method, url, data=data, header=header)

        if not response:
            warnings.warn('no response from HTTP call')

        if response.status_code != 200:
            print(response)

        return response.json()


    @property
    def _region(self):
        '''
        returns the region from the login service
        '''
        region = self._blink_auth.region
        key = next(iter(region.keys()))
        return key


    def get_networks(self):
        '''
        get Blink network information for token accounts region
        '''
        url = '{0}/networks'.format(BlinkUrls.root_url(self._region))
        response = self._call('GET', url)

        return BlinkFactory.load_network(response)


    def get_devices(self):
        '''
        comment goes here
        '''
        url = '{0}/homescreen'.format(BlinkUrls.root_url(self._region))
        response = self._call('GET', url)

        return BlinkFactory.load_devices(response)


    def get_network(self, network):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}'.format(BlinkUrls.root_url(self._region), network)
        response = self._call('GET', url)

        return BlinkNetwork(response)


    def get_sync_modules(self, network):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/syncmodules'.format(BlinkUrls.root_url(self._region), network)
        response = self._call('GET', url)

        return BlinkFactory.load_sync_modules(response)


    def get_video_count(self):
        '''
        comment goes here
        '''
        url = '{0}/api/v2/videos/count'.format(BlinkUrls.root_url(self._region))
        response = self._call('GET', url)

        return response


    def get_videos(self, page):
        '''
        comment goes here
        '''
        url = '{0}/api/v2/videos/page/{1}'.format(BlinkUrls.root_url(self._region), page)
        response = self._call('GET', url)

        return BlinkFactory.load_videos(response)


    def get_events(self, network):
        '''
        comment goes here
        '''
        url = '{0}/events/network/{1}'.format(BlinkUrls.root_url(self._region), network)
        response = self._call('GET', url)

        return BlinkFactory.load_events(response)


    def get_camera_config(self, network, camera):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/camera/{2}/config'.format(BlinkUrls.root_url(self._region),
                                                         network,
                                                         camera)
        response = self._call('GET', url)

        return BlinkFactory.load_camera_config(response)


    def arm_camera(self, network, camera):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/camera/{2}/enable'.format(BlinkUrls.root_url(self._region),
                                                         network,
                                                         camera)
        response = self._call('POST', url)

        return BlinkFactory.load_data(response)


    def disarm_camera(self, network, camera):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/camera/{2}/disable'.format(BlinkUrls.root_url(self._region),
                                                          network,
                                                          camera)
        response = self._call('POST', url)

        return BlinkFactory.load_data(response)


    def arm_network(self, network):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/arm'.format(BlinkUrls.root_url(self._region),
                                           network)
        response = self._call('POST', url)

        return BlinkFactory.load_data(response)


    def disarm_network(self, network):
        '''
        comment goes here
        '''
        url = '{0}/network/{1}/disarm'.format(BlinkUrls.root_url(self._region),
                                              network)
        response = self._call('POST', url)

        return BlinkFactory.load_data(response)


if __name__ == '__main__':
    config = {}
    with open('./config.json', 'r') as f:
        config = json.load(f)

    # ideally I would use the security module to encrypt
    #   the user/password and store in config
    blink = BlinkRestApi(config['user_id'], config['password'])

    networks = blink.get_networks()
    #print(json.dumps(networks, indent=4, sort_keys=True))

    devices = blink.get_devices()
    #print(json.dumps(devices, indent=4, sort_keys=True))

    for device in devices:
        print(json.dumps(device, indent=4, sort_keys=True))
        break

    for network in networks:
        if network['armed']:
            #response = blink.disarm_network(network['id'])
            #print(json.dumps(response, indent=4, sort_keys=True))
            print('disarmed network {}'.format(network['name']))
            pass
        else:
            #response = blink.arm_network(network['id'])
            #print(json.dumps(response, indent=4, sort_keys=True))
            print('armed network {}'.format(network['name']))
            pass


        for device in devices:
            if isinstance(device, BlinkCamera):
                camera_config = blink.get_camera_config(network['id'], device['device_id'])
                #print(json.dumps(camera_config, indent=4, sort_keys=True))

                if camera_config['enabled']:
                    #response = blink.disarm_camera(network['id'], device['device_id'])
                    #print(json.dumps(response, indent=4, sort_keys=True))
                    print('disarmed camera {}'.format(device['name']))
                    pass
                else:
                    #response = blink.arm_camera(network['id'], device['device_id'])
                    #print(json.dumps(response, indent=4, sort_keys=True))
                    print('armed camera {}'.format(device['name']))
                    pass
            else:
                #print(json.dumps(device, indent=4, sort_keys=True))
                pass


        # more details about the network
        #response = blink.get_network(network['id'])
        #print(json.dumps(response, indent=4, sort_keys=True))

        # more details about network then the 'devices' version
        #response = blink.get_sync_modules(network['id'])
        #print(json.dumps(response, indent=4, sort_keys=True))

        #response = blink.get_events(network['id'])
        #print(json.dumps(response, indent=4, sort_keys=True))


    page = 0
    response = blink.get_video_count()
    #print(json.dumps(response, indent=4, sort_keys=True))

    total = response['count']
    page = 0
    count = 0
    while count < total:
        videos = blink.get_videos(page)
        count += len(videos)
        #print(json.dumps(videos, indent=4, sort_keys=True))
        page += 1
        print('count: {}/ page: {}'.format(count, page))

    blink = None
