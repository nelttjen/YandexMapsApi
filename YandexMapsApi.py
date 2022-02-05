import requests


class ResponseError(Exception):
    def __init__(self, string):
        super().__init__()
        self.msg = string

    def __str__(self):
        return self.msg


class ParamError(Exception):
    pass


class ApikeyError(Exception):
    pass


def generate_link(apiserver, params):
    link = apiserver + '?'
    for key, value in params.items():
        if link[-1] != '?':
            link += '&'
        link += f'{key}={value}'
    return link


def make_response(apiserver, params, return_link, check_success=False):
    response = requests.get(apiserver, params=params)
    if check_success:
        if response.status_code == 200:
            if return_link:
                return response, generate_link(apiserver, params)
            return response
        try:
            raise ResponseError(f'Response returned code: {response.status_code}\n'
                                f'Response message: {response.json()["message"]}')
        except KeyError:
            raise ResponseError(f'Response returned code: {response.status_code}')
    if return_link:
        return response, generate_link(apiserver, params)
    return response


def add_search_area(params, ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0))):
    if bbox != ((0, 0), (0, 0)):
        if not isinstance(bbox, str):
            bbox = f'{bbox[0][0]},{bbox[0][1]}~{bbox[1][0]},{bbox[1][1]}'
        params['bbox'] = bbox
    else:
        if not isinstance(ll, str):
            ll = ','.join(map(str, ll))
        params['ll'] = ll
        if not isinstance(spn, str):
            spn = ','.join(map(str, spn))
        params['spn'] = spn
    return params


class YandexApi:
    def __init__(self, geocode_apikey, search_apikey, check_keys=False, app=None):
        self.app = app

        self.geocode_api = 'https://geocode-maps.yandex.ru/1.x/'
        self.geocode_apikey = geocode_apikey

        self.static_api = 'https://static-maps.yandex.ru/1.x/'

        self.search_api = "https://search-maps.yandex.ru/v1/"
        self.search_apikey = search_apikey

        self.format_res = 'json'

        if check_keys and not all([geocode_apikey, search_apikey]):
            g = '' if geocode_apikey else 'Geocoder apikey is missing\n'
            s = '' if search_apikey else 'Search apikey is missing\n'
            raise ApikeyError('Apikeys is required!\n' + g + s)

    def geocoder_get(self, geocode, sco='longlat', res_format='xml', kind=None, rspn=0,
                     ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0)), results=10, skip=0,
                     lang='ru_RU', callback=None, using_search_area: bool = False,
                     return_link=False, check_success=False):
        params = {
            'apikey': self.geocode_apikey,
            'geocode': geocode,
        }
        if sco != 'longlat':
            params['sco'] = sco
        if res_format != 'xml':
            params['format'] = res_format
        if kind is not None:
            params['kind'] = kind
        if rspn != 0:
            params['rspn'] = rspn
        if results != 10:
            params['results'] = results
        if skip != 0:
            params['skip'] = skip
        if lang != 'ru_RU':
            params['lang'] = lang
        if callback is not None:
            if res_format == 'json':
                params['callback'] = callback
        if using_search_area:
            params = add_search_area(params, ll=ll, spn=spn, bbox=bbox)
        return make_response(self.geocode_api, params, return_link, check_success=check_success)

    def search_get(self, what, lang='ru_RU', s_type=None, rspn=0,
                   results=10, skip=0, callback=None,
                   ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0)),
                   using_search_area: bool = False,
                   return_link=False, check_success=False):
        params = {
            "apikey": self.search_apikey,
            "lang": lang
        }
        if not isinstance(what, str):
            params['text'] = ','.join(map(str, what))
        else:
            params['text'] = what
        if results != 10:
            params['results'] = results
        if s_type is not None:
            params['type'] = s_type
        if rspn != 0:
            params['rspn'] = rspn
        if skip != 0:
            params['skip'] = skip
        if callback is not None:
            params['callback'] = callback
        if using_search_area:
            params = add_search_area(params, ll=ll, spn=spn, bbox=bbox)
        return make_response(self.search_api, params, return_link, check_success=check_success)

    def static_get(self, l, param, s_type='ll', spn=(0.005, 0.005), z=10, size=(600, 450), scale=1.0,
                   pt=None, pl=None, lang='ru_RU',
                   return_link=False, check_success=False, add_spn=True, add_zoom_manual=False):

        if s_type == 'bbox':
            if not isinstance(param, str):
                param = f'{param[0][0]},{param[0][1]}~{param[1][0]},{param[1][1]}'
            params = {
                'l': l,
                'bbox': param
            }
        elif s_type == 'll':
            if not isinstance(param, str):
                param = ','.join(list(map(str, param)))
            params = {
                'l': l,
                'll': param
            }
        else:
            raise ParamError(f's_type must be one of (ll, bbox), not {s_type}')
        if s_type == 'll' and add_spn:
            if isinstance(spn, str):
                params['spn'] = spn
            else:
                params['spn'] = ','.join(map(str, spn))
        if add_zoom_manual:
            params['z'] = z
        else:
            if z != 10:
                params['z'] = z
        if scale != 1.0 and l != 'sat':
            params['scale'] = scale
        if lang != 'ru_RU':
            params['lang'] = lang
        if size != (600, 450):
            if isinstance(size, str):
                params['size'] = size
            else:
                params['size'] = ','.join(map(str, size))
        if pt is not None:
            if isinstance(pt, str):
                params['pt'] = pt
            else:
                params['pt'] = '~'.join(pt)
        if pl is not None:
            if isinstance(pl, str):
                params['pl'] = pl
            else:
                params['pl'] = '~'.join(pl)
        return make_response(self.static_api, params, return_link, check_success=check_success)

    def get_position(self, geocode, return_link=False, check_success=False):
        params = {
            'apikey': self.geocode_apikey,
            'geocode': geocode,
            'format': 'json'
        }
        if return_link:
            response, link = make_response(self.geocode_api, params, return_link, check_success)
        else:
            response = make_response(self.geocode_api, params, return_link, check_success)
        try:
            res_json = response.json()['response']['GeoObjectCollection']['featureMember'][0]
            position = tuple(map(float, res_json['GeoObject']['Point']['pos'].split()))
            if return_link:
                return position, link
            return position
        except (KeyError, IndexError):
            raise ResponseError('Bad Request')
