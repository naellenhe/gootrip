import requests
from titlecase import titlecase
import urllib

def get_wiki_description(title):
    """Get the wiki content.

    response format:

    {u'batchcomplete': u'',
     u'query': {u'pages': {u'12103': {u'extract': u'The Golden Gate Bridge is a ...',
                                      u'pageid': 12103,
                                      u'title': u'Golden Gate Bridge'}}}}

    """

    # Convert to title format
    title = titlecase(title)
    title = urllib.quote(title)

    url_search = "https://en.wikipedia.org//w/api.php?action=query&format=json&prop=extracts&exsentences=5&exintro=1&explaintext=1&exsectionformat=plain&titles={}".format(title)

    response = requests.get(url_search).json()
    pages = response['query']['pages'].values()
    page = pages[0]

    if 'extract' in page:
        extract = page['extract']
        extract = extract.encode('utf-8')

    else:
        extract = ''

    return extract


def get_wiki_response(title):
    """Get the wiki content.

    response format:

    {u'batchcomplete': u'',
     u'query': {u'pages': {u'12103': {u'extract': u'The Golden Gate Bridge is a ...',
                                      u'pageid': 12103,
                                      u'title': u'Golden Gate Bridge'}}}}

    """

    # Convert to title format
    title = titlecase(title).encode('utf-8')

    url_search = "https://en.wikipedia.org//w/api.php?action=query&format=json&prop=extracts&exsentences=5&exintro=1&explaintext=1&exsectionformat=plain&titles={}".format(title)
    response = requests.get(url_search).json()

    return response
