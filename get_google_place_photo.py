import requests

#my Google api key
key = "AIzaSyBeD1vIu0C2hIMeiLWDD0_4L28Mj8A4YyM"

def get_place_photo_url(place, lat, lng):
    """Request google place photo and save to database.

    Text Search Requests:
    https://maps.googleapis.com/maps/api/place/textsearch/output?parameters

    Required parameters:
        query
        API key

    Returned from place search request:
    An example of a photos[] array is shown below.
    "photos" : [
       {
          "html_attributions" : [],
          "height" : 853,
          "width" : 1280,
          "photo_reference" : "CnRvAAAAwMpdHeWlXl-lH0vp7lez4znKPIWSWvgvZFISdKx45AwJVP1Qp37YOrH7sqHMJ8C-vBDC546decipPHchJhHZL94RcTUfPa1jWzo-rSHaTlbNtjh-N68RkcToUCuY9v2HNpo5mziqkir37WU8FJEqVBIQ4k938TI3e7bf8xq-uwDZcxoUbO_ZJzPxremiQurAYzCTwRhE_V0"

    request url looks like:
    https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=CnRtAAAATLZNl354RwP_9UKbQ_5Psy40texXePv4oAlgP4qNEkdIrkyse7rPXYGd9D_Uj1rVsQdWT4oRz4QrYAJNpFX7rzqqMlZw2h2E2y5IKMUZ7ouD_SlcHxYq1yL4KbKUv3qtWgTK0A6QbGh87GB3sscrHRIQiG2RrmU_jF4tENr9wGS_YxoUSSDrYjWmrNfeEHSGSc3FyhNLlBU&key=YOUR_API_KEY

    - maxheight or maxwidth
    Both the maxheight and maxwidth properties accept an integer between 1 and 1600.
    """

    url_search = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&location={},{}&radius=500&key={}".format(place, lat, lng, key)

    response = requests.get(url_search).json()
    if response['status'] == 'OK':
        # results data type:list
        result = response['results'][0]
        photo = result['photos'][0]
        photo_url = get_place_photo(photo)
        return photo_url

    else:
        return ""

def get_place_photo(photo):
    """Return photo url from a photo dict."""

    photo_ref = photo['photo_reference']
    url_photo = "https://maps.googleapis.com/maps/api/place/photo?maxwidth={}&photoreference={}&key={}".format(400, photo_ref, key)

    return url_photo
