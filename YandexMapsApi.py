import requests


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
        return
    if return_link:
        return response, generate_link(apiserver, params)
    return response


def add_search_area(params, ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0)), format_bbox=True):
    if bbox != ((0, 0), (0, 0)):
        if format_bbox:
            bbox = f'{bbox[0][0]},{bbox[0][1]}~{bbox[1][0]},{bbox[1][1]}'
        params['bbox'] = bbox
    else:
        params['ll'] = ','.join(map(str, ll))
        params['spn'] = ','.join(map(str, spn))
    return params


class YandexApi:
    def __init__(self, geocode_apikey, search_apikey, app=None):
        self.app = app

        self.geocode_api = 'http://geocode-maps.yandex.ru/1.x/'
        self.geocode_apikey = geocode_apikey

        self.static_api = 'http://static-maps.yandex.ru/1.x/'

        self.search_api = "https://search-maps.yandex.ru/v1/"
        self.search_apikey = search_apikey

        self.format_res = 'json'

    def geocoder_get(self, geocode, sco='longlat', res_format='xml', kind=None, rspn=0,
                     ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0)), results=10, skip=0,
                     lang='ru_RU', callback=None, using_search_area: bool = False,
                     format_bbox=True,
                     return_link=False):
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
            params = add_search_area(params, ll=ll, spn=spn, bbox=bbox, format_bbox=format_bbox)
        return make_response(self.geocode_api, params, return_link)

    def search_get(self, what: str, lang='ru_RU', s_type=None, rspn=0,
                   results=10, skip=0, callback=None,
                   ll=(0, 0), spn=(0, 0), bbox=((0, 0), (0, 0)),
                   using_search_area: bool = False, format_bbox=True,
                   return_link=False):
        params = {
            "apikey": self.search_apikey,
            "text": what,
        }
        if results != 10:
            params['results'] = results
        if lang != 'ru_RU':
            params['lang'] = lang
        if s_type is not None:
            params['type'] = s_type
        if rspn != 0:
            params['rspn'] = rspn
        if skip != 0:
            params['skip'] = skip
        if callback is not None:
            params['callback'] = callback
        if using_search_area:
            params = add_search_area(params, ll=ll, spn=spn, bbox=bbox, format_bbox=format_bbox)
        return make_response(self.search_api, params, return_link)

    def static_get(self, l, param, s_type='ll', z=10, size=(600, 450), scale=2.0,
                   pt=None, pl=None, lang='ru_RU', format_bbox=False,
                   return_link=False):
        if s_type == 'bbox':
            if format_bbox and param is list:
                param = f'{param[0][0]},{param[0][1]}~{param[1][0]},{param[1][1]}'
            params = {
                'l': l,
                'bbox': param,
            }
        elif s_type == 'll':
            params = {
                'l': l,
                'll': ','.join(map(str, param)),
            }
        else:
            return
        if z != 10:
            params['z'] = z
        if scale != 2.0:
            params['scale'] = scale
        if lang != 'ru_RU':
            params['lang'] = lang
        if size != (600, 450):
            params['size'] = ','.join(map(str, size))
        if pt is not None:
            params['pl'] = '~'.join(pl)
        if pl is not None:
            params['pl'] = '~'.join(pl)
        return make_response(self.static_api, params, return_link)