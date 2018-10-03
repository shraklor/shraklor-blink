'''
help with controllering blink cameras and other blink related tasks

Author:  shraklor

Target:  python3
'''
import logging
import json
from datetime import datetime, timedelta
import time         # testing...take out

from shraklor.http import Http


class BlinkRateLimitExceededException(Exception):
    '''
    used to raise an exception when too many calls are made within
    a specified time limit
    '''
    pass



def rate_limit_check():
    EXCEPTION_EXCEED_MSG = 'Exceeded calls to Blink REST API ({0}) of ({1}) within 60 seconds.'

    def wrapper():

        if 1 == 2:
            raise BlinkRateLimitExceededException()








class BlinkUnknownDevice(Exception):
    ''' informs us of unknown devices '''

    def __init__(self, device, specific):
        ''' init '''
        super().__init__('Unknown device type {0}.{1}'.format(device, specific))



class BlinkUrls():
    '''
    helper class to manage URLs
    '''
    domain = 'immedia-semi.com'
    fqdn = 'prod.{0}'.format(domain)
    full = 'https://rest.{0}'.format(fqdn)
    login = 'https://rest.{0}/login'.format(fqdn)
    base = 'https://{0}'.format(fqdn)



class BlinkAuthService():
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
        #self.logger.setLevel(logging.DEBUG)

        self._email = email
        self._password = password
        self._client = getattr(kwargs, 'client', self._CLIENT)
        self._header = getattr(kwargs, 'header', self._HEADER)
        self._proxy = getattr(kwargs, 'proxy', None)
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


class BlinkNetwork(dict):
    ''' class to track the data corresponding to a network '''

    def __init__(self, data):
        ''' init '''
        #print(json.dumps(data, indent=4, sort_keys=True))
        dict.__init__(self, account_id=data['account_id'],
                            armed=data['armed'],
                            created_on=data['created_at'],
                            description=data['description'],
                            id=data['id'],
                            name=data['name'],
                            origin=data['network_origin'],
                            ping=data['ping_interval'],
                            timez=data['time_zone'],
                            last_update_on=data['updated_at'])


    @staticmethod
    def load(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkNetwork
        '''
        results = []
        if not data:
            return None

        if 'networks' not in data:
            return None

        for network in data['networks']:
            results.append(BlinkNetwork(network))

        return results

    '''
    def __repr__(self):
        '' make serializable ''
        return json.dumps(self.__dict__)
    '''



class BlinkDeviceCameraXt(dict):
    ''' device that represents a Blink XT Camera '''

    def __init__(self, data):
        ''' init '''
        #print(json.dumps(data, indent=4, sort_keys=True))
        dict.__init__(self, state=data['active'],
                            armed=data['armed'],
                            device_type=data['device_type'],
                            model=data['type'],
                            id=data['device_id'],
                            name=data['name'],
                            enabled=data['enabled'],
                            temperature=data['temp'],
                            battery=data['battery'],
                            battery_state=data['battery_state'],
                            warning=data['warning'],
                            errors=data['errors'],
                            error_msg=data['error_msg'],
                            last_update_on=data['updated_at'])


class BlinkDeviceCameraWhite(dict):
    ''' device that represents a Blink Camera '''

    def __init__(self, data):
        ''' init '''
        #print(json.dumps(data, indent=4, sort_keys=True))
        dict.__init__(self, state=data['active'],
                            armed=data['armed'],
                            device_type=data['device_type'],
                            model=data['type'],
                            id=data['device_id'],
                            name=data['name'],
                            enabled=data['enabled'],
                            temperature=data['temp'],
                            battery=data['battery'],
                            battery_state=data['battery_state'],
                            warning=data['warning'],
                            errors=data['errors'],
                            error_msg=data['error_msg'],
                            last_update_on=data['updated_at'])


class BlinkDeviceSyncModule(dict):
    ''' device that represents a Blink Sync Module '''

    def __init__(self, data):
        ''' init '''
        #print(json.dumps(data, indent=4, sort_keys=True))
        dict.__init__(self, device_type=data['device_type'],
                            id=data['device_id'],
                            status=data['status'],
                            last_hb=data['last_hb'],
                            warning=data['warning'],
                            errors=data['errors'],
                            error_msg=data['error_msg'],
                            last_update_on=data['updated_at'])



class BlinkSyncModule(dict):
    ''' device that represents a Blink Sync Module '''

    def __init__(self, data):
        ''' init '''
        #print(json.dumps(data, indent=4, sort_keys=True))
        dict.__init__(self, account_id=data['account_id'],
                            created_on=data['created_at'],
                            firmware=data['fw_version'],
                            id=data['id'],
                            ip_address=data['ip_address'],
                            last_activity=data['last_activity'],
                            name=data['name'],
                            network_id=data['network_id'],
                            os_version=data['os_version'],
                            serial=data['serial'],
                            status=data['status'],
                            last_hb=data['last_hb'],
                            wifi_strength=data['wifi_strength'],
                            last_update_on=data['updated_at'])



class BlinkFactory():
    ''' class to track the data corresponding to a homescreen '''

    @staticmethod
    def load_sync_modules(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkDevices
        '''
        results = []
        if not data:
            return None

        if 'devices' not in data:
            return None

        for module in data['syncmodule']:
            results.append(BlinkSyncModule(module))

        return results

    @staticmethod
    def load_devices(data):
        '''
        loops through response from get_networks to load new instances
            of BlinkDevices
        '''
        results = []
        if not data:
            return None

        if 'devices' not in data:
            return None

        for device in data['devices']:
            if 'device_type' in device:
                device_type = device['device_type']

                if device_type == 'camera':
                    typ = device['type']
                    if typ == 'xt':
                        results.append(BlinkDeviceCameraXt(device))
                    elif typ == 'white':
                        results.append(BlinkDeviceCameraWhite(device))
                    else:
                        raise BlinkUnknownDevice(device_type, typ)
                elif device_type == 'sync_module':
                    results.append(BlinkDeviceSyncModule(device))
                else:
                    raise BlinkUnknownDevice(device_type, None)

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


    def _call(self, method, url, data=None):
        '''
        '''
        header = self._get_header()
        self.logger.debug(header)
        self.logger.info('{0} {1}'.format(method, url))
        response = self._http.send(method, url, data=data, header=header)

        if not response:
            raise Exception('no response from HTTP call')

        response = response.json()

        return response


    def _get_header(self):
        '''
        creates the HTTP header with latest token info
            from the BlinkAuthService
        '''
        header = self._header.copy()
        token = self._blink_auth.token()
        header.update({'TOKEN_AUTH': token})
        header.update({'HOST': BlinkUrls.fqdn})

        return header
    
    @property
    def _region(self):
        '''
        returns the regions from the login service
        '''
        region = self._blink_auth.region
        key = next(iter(region.keys()))
        return key


    def get_networks(self):
        '''
        get Blink network information for token accounts region
        '''
        url = 'https://rest.{0}.{1}/networks'.format(self._region, BlinkUrls.domain)
        response = self._call('GET', url)

        self.logger.debug(json.dumps(response, indent=4, sort_keys=True))
        return BlinkNetwork.load(response)


    def get_homescreens(self):
        '''
        get Blink network information for token account
        '''
        self.logger.debug('called get_homescreens()')
        url = 'https://rest.{0}.{1}/homescreen'.format(self._region, BlinkUrls.domain)
        response = self._call('GET', url)

        self.logger.debug(json.dumps(response, indent=4, sort_keys=True))

        return BlinkFactory.load_devices(response)


    def get_network(self, network_id):
        '''
        get Blink network information for token account
        '''
        self.logger.debug('called get_network({0})'.format(network_id))
        url = 'https://rest.{0}.{1}/network/{2}'.format(self._region, BlinkUrls.domain, network_id)
        response = self._call('GET', url)
        self.logger.debug(json.dumps(response, indent=4, sort_keys=True))

        return BlinkNetwork(response['network'])


    def get_sync_modules(self, network_id):
        '''
        get Blink network information for token account
        '''
        self.logger.debug('called get_sync_modules({0})'.format(network_id))
        url = 'https://rest.{0}.{1}/network/{2}/syncmodules'.format(self._region, BlinkUrls.domain, network_id)
        response = self._call('GET', url)

        self.logger.debug(json.dumps(response, indent=4, sort_keys=True))

        return BlinkFactory.load_sync_modules(response)


    def arm_network(self, region_id, network_id):
        '''
        get Blink network information for token account
        '''
        self.logger.debug('called arm({0}, {1})'.format(region_id, network_id))
        url = 'https://rest.{0}.{1}/network/{2}/arm'.format(region_id, BlinkUrls.domain, network_id)
        # url = '{0}/network/{1}/syncmodules'.format(BlinkUrls.full, network_id)
        response = self._call('GET', url)

        self.logger.debug(json.dumps(response, indent=4, sort_keys=True))

        return None







if __name__ == '__main__':
    config = {}
    with open('./config.json', 'r') as f:
        config = json.load(f)

    blink = BlinkRestApi(config['user_id'], config['password'])
    
    networks = blink.get_networks()
    #print(json.dumps(networks, indent=4, sort_keys=True))

    home_screens = blink.get_homescreens()
    # print(json.dumps(home_screens, indent=4, sort_keys=True))

    for network in networks:
        response = blink.get_network(network['id'])
        print(json.dumps(response, indent=4, sort_keys=True))

        response = blink.get_sync_modules(network['id'])
        print(json.dumps(response, indent=4, sort_keys=True))

        # blink.arm_network(key, network['id'])

    blink = None



































class HomeDevice():
    ''' class to track the data corresponding to a network '''

    def __init__(self, data):
        ''' init '''
        self.name = data['name']
        self.wifi_strength = data['wifi_strength']
        self.armed = data['armed']
        self.device_type = data['device_type']
        self.type = data['type']
        self.enabled = data['enabled']
        self.temp = data['temp']
        self.battery = data['battery']

    def __repr__(self):
        ''' make serializable '''
        return json.dumps(self.__dict__)

















class BlinkRegion():
    ''' class to track the data corresponding to a region '''

    def __init__(self, id, name):
        ''' init '''
        self.id = id
        self.name = name
        self.blink_networks = []    # BlinkNetwork
        self.home_networks = []     # HomeNetwork
        self.home_devices = []      # HomeDevice


    def __repr__(self):
        ''' make serializable '''
        return json.dumps(self.__dict__)



class BlinkCamera():
    ''' class to track the data corresponding to a camera '''

    def __init__(self, data):
        ''' init '''
        pass

    def __repr__(self):
        ''' make serializable '''
        return json.dumps(self.__dict__)











class BlinkRestApiX():
    '''
    handles calls to Rest API
    '''

    MAXIMUM_CALLS_PER_MINUTE = 10

    DEFAULT_CLIENT = 'iPhone 9.2 | 2.2 | 222'

    DEFAULT_HEADER = {'Content-Type': 'application/json'}
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
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(format=self.LOG_FORMAT)

        client = kwargs.get('client', self.DEFAULT_CLIENT)
        self._blink_auth = BlinkAuthService(user_id, password, client=client)

        self.header = getattr(kwargs, 'header', self.DEFAULT_HEADER)
        self.proxy = getattr(kwargs, 'proxy', None)

        self.http = Http(header=header, proxy=proxy)

        self._auth_token = None
        self._http_rates = {'calls': [], 'max': self.MAXIMUM_CALLS_PER_MINUTE}

        # i dont like the idea of storing these
        # but since we will expire the token we
        # will keep for convience to auto-login
        # when needed
        self._user_id = user_id
        self._password = password


    def __del__(self):
        ''' cleanup '''
        del self._user_id
        del self._password
        _LOGGER.info('clean up of BlinkRestApi')


    


    @property
    def regions(self):
        return self._regions


    @property
    def networks(self):
        return self._networks


    def _get_header(self, region):
        '''
        populates header with latest token and needed region info
        Inputs:
            region(BlinkRegion): the region we want to get information from
        Returns:
            (dict): Http header dictionary
        '''
        headers = self.headers

        headers['Host'] = '{0}.{1}'.format(region.id, self.BLINK_DOMAIN)
        headers['TOKEN_AUTH'] = self._auth_token['token']

        return headers


    def _check_rate_limits(self):
        '''
        checks to see if user has made too many calls to the Blink REST API
            within the allowable limit.

        Raises:
            BlinkRateLimitExceededException
        '''
        _LOGGER.info('_check_rate_limits')
        now = datetime.now()
        self._http_rates['calls'].append(now)
        expired = now - timedelta(seconds=60)

        #rebuild the list with only the not expired ones
        self._http_rates['calls'] = [tim for tim in self._http_rates['calls'] if tim > expired]

        count = len(self._http_rates['calls'])
        _LOGGER.info('rate count: %s of %s', count, self._http_rates['max'])

        if count > self._http_rates['max']:
            msg = EXCEPTION_EXCEED_MSG.format(count, self._http_rates['max'])
            raise BlinkRateLimitExceededException(msg)


    def _check_expired_token(self):
        '''
        checks for an expiring token and refreshes as needed
        '''
        _LOGGER.info('_check_expired_token')
        now = datetime.now()

        _LOGGER.info('Token expires: %s', self._auth_token['expires'])
        if now >= self._auth_token['expires']:
            _LOGGER.warning('Token expired')
            self._login()


    def _validate_response(self, http_response):
        '''
        '''
        _LOGGER.info('_validate_response')
        if 'message' in http_response:
            _LOGGER.error(http_response)



    def _make_http_call(self, region, method, url, data=None, stream=False):
        '''
        this will handle all calls to the REST API except for 
            logging in
            this is so we can track expiration of token and 
            rate limiting
        '''
        self._check_rate_limits()
        self._check_expired_token()

        proxy = self.proxy
        header = self._get_header(region)

        _LOGGER.info('_make_http_call')
        _LOGGER.info('url    :%s %s', method, url)
        _LOGGER.info('header :%s', header)
        if data is not None:
            _LOGGER.info('data   :%s', data)

        #response = Http.call(method, url, data=data, header=header, proxy=proxy, stream=stream)
        response = self.http_get(url=url, header=header, stream=stream)

        self._validate_response(response)
        return response


    def _login(self):
        '''
        logs in
        '''
        self.logger.info('BlinkRestApi._login()')
        data = {}
        data['email'] = self._user_id
        data['password'] = self._password
        data['client_specifier'] = self._client
        data = json.dumps(data)

        header = self.headers.copy()
        header.update(self.LOGIN_HEADER)

        response = self.http.post(url=self.LOGIN_URL, data=data, header=header)

        if 'message' in response:
            raise Exception(response['message'])

        token_expire = datetime.now() + timedelta(seconds=self.TOKEN_EXPIRATION_SECONDS)
        self._auth_token = {'expires': token_expire, 'token': response['authtoken']['authtoken']}

        regions = []
        for key in response['region']:
            region = BlinkRegion(key, response['region'][key])
            _LOGGER.info('Region: %s', region)
            regions.append(region)

        _LOGGER.debug(self._auth_token)
        self._regions = regions




    def get_regions(self):
        pass


    def get_region_networks(self, region):
        '''
        gets networks for a given region

        Inputs:
            region (BlinkRegion): the region to get network information of

        Returns:
            (List<BlinkNetwork>)
        '''
        url = 'https://rest.{0}.{1}/networks'.format(region.id, self.BLINK_DOMAIN)
        response = self._make_http_call(region, 'GET', url)

        if 'message' in response:
            raise Exception(response['message'])

        # load response into BlinkNetwork object
        for rcv_net in response['networks']:
            network = BlinkNetwork(rcv_net)
            _LOGGER.debug('region.network: %s', network)
            region.blink_networks.append(network)



    def get_home_networks(self, region):
        '''
        gets listing of home networks given a region

        Inputs:
            region (BlinkRegion): the region to get information from

        Returns:
            (List<HomeNetwork>)
        '''
        results = []
        url = 'https://rest.{0}.{1}/homescreen'.format(region.id, self.BLINK_DOMAIN)
        response = self._make_http_call(region, 'GET', url)

        if 'message' in response:
            raise Exception(response['message'])

        # this is info about the home network (not blink network)
        if 'network' in response:
            home = HomeNetwork(response['network'])
            _LOGGER.info('region.home_net: %s', home)
            results.append(home)

        return results


    def get_devices(self, region):
        '''
        gets listing of blink devices within a given region

        Inputs:
            region (BlinkRegion): the region to get information from

        Returns:
            (List<HomeDevice>)
        '''
        results = []
        url = 'https://rest.{0}.{1}/homescreen'.format(region.id, self.BLINK_DOMAIN)
        response = self._make_http_call(region, 'GET', url)

        if 'message' in response:
            raise Exception(response['message'])

        for index in response['devices']:
            device = HomeDevice(response['devices'][index])
            _LOGGER.info('region.home_device: %s', device)
            results.append(device)

        return results




class Blink():
    '''
    helper class to organize getting/updateing Blink device information
    '''

    def __init__(self, user_id, password):
        '''
        init
        '''
        self.loaded = False
        self._rest_api = BlinkRestApi(user_id=user_id, password=password)

        self.loaded = True

    def __del__(self):
        '''
        cleanup
        '''
        if self.loaded:
            del self._rest_api
        _LOGGER.info('clean up of Blink')



    def arm(self, value=None):
        '''
        set/gets arm state of cameras
        '''
        if value is not None:
            #TODO: call to arm/disarm
            pass

        pass


    def get_cameras(self):
        '''
        gets listing of any cameras
        '''
        pass


    def get_videos(self):
        '''
        gets listing of any videos
        '''
        pass



