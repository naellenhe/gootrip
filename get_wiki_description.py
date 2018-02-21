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

    reponse = requests.get(url_search).json()
    pages = reponse['query']['pages'].values()
    page = pages[0]

    extract = page['extract']
    extract = extract.encode('utf-8')

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
    reponse = requests.get(url_search).json()

    return reponse
