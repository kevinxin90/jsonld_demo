from config import *
from jsonld_processor import load_context, fetch_doc_from_api, nquads_transform, get_uri_value_pairs
from biothings_client import ClientRedirect

def get_biothings(api, id, fields=None, fields_uri=None):
    if fields:
        doc = ClientRedirect().annotate(id, api, fields=fields)
        return doc
    elif fields_uri:
        field_name_list = uri_to_field_name(fields_uri, api)
        field_name = ",".join(field_name_list)
        doc = ClientRedirect().annotate(id, api, fields=field_name)
        return doc
    else:
        doc = ClientRedirect().annotate(id, api)
        return doc

def query_biothings(api, fields=None, fields_uri=None, fields_value=None, return_fields=None, return_fields_uri=None, fetch_all=True):
    if return_fields_uri:
        field_name_list = uri_to_field_name(return_fields_uri, api)
        return_fields = ",".join(field_name_list)    
    if fields:
        query_info = fields + ': ' + fields_value
    elif fields_uri:
        query_field_name_list = uri_to_field_name(fields_uri, api)
        query_info = compose_query_parameter_from_uri(fields_uri, fields_value, api)
        print(query_info)
        print(return_fields)
    return ClientRedirect().query(api, query_info, fields=return_fields, fetch_all=fetch_all)

def find_id_from_uri(uri):
    for _id in AVAILABLE_IDS.keys():
        if AVAILABLE_IDS[_id]["uri"] == uri:
            return _id

def uri_to_field_name(uri, api):
    context = load_context(api)
    return [_field for _field, _uri in context["@context"].items() if _uri==uri]

def compose_query_parameter_from_uri(uri, value, api):
    field_name_list = uri_to_field_name(uri, api)
    query_string = ''
    for _field_name in field_name_list:
        query_string = query_string + ' ' + _field_name + ':' + value + ' OR'
    return query_string.strip(' OR')

class Biothingsexplorer():
    def __init__(self):
        self.jsonld_doc = None
        self._api_value = {}

    def get_json_doc(self, api, id):
        # construct url from id
        url = AVAILABLE_API_SOURCES[api]['annotate_syntax'].replace('*', id)
        json_doc = fetch_doc_from_api(url)
        context = load_context(api)
        json_doc.update(context)
        self.jsonld_doc = nquads_transform(json_doc)
        return json_doc

    def find_linked_apis(self):
        uri_list = get_uri_value_pairs(self.jsonld_doc)
        for _uri,_value in uri_list.items():
            _id = find_id_from_uri(_uri)
            for _api in AVAILABLE_API_SOURCES.keys():
                if _id in AVAILABLE_API_SOURCES[_api]['annotate_ids']:
                    self._api_value[_api] = _value
        print('Available APIs which could be linked out is: {}'.format(self._api_value))

    def explore_api(self, api, fields=None, fields_uri=None):
        return get_biothings(api, self._api_value[api], fields=fields, fields_uri=fields_uri)



