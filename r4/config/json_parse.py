import json

boto2url(jsonfile):
    js = open(jsonfile)
    data = json.load(js)
    uridict = dict()
    for datum in data['operations']:
        uri = datum['http']['requestUri']
        method = datum['http']['method']
        if uri not in uridict:
            uridict[uri] = []
        uridict[uri].append(method)
    return uridict

if __name__ == '__main__':
    pass
