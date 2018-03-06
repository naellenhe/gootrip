import flickrapi
import random

api_key = u'500072adc6bc7a46dbf6ffcefc488a94'
api_secret = u'c483bc161f6343be'
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

def get_flickr_photo_url(attraction, lat, lng):
    """Convert result's dictionary format to url

    Data format of search result:
        { "photos": { "page": 1, "pages": "1660", "perpage": 100, "total": "165949",
            "photo": [
              { "id": "39281945045", "owner": "70075489@N03", "secret": "01f2ce9893",
                "server": "4625", "farm": 5, "title": "The wok shop",
                "ispublic": 1, "isfriend": 0, "isfamily": 0 },
              { "id": "25307247167", "owner": "19159227@N06", "secret": "9a31b422f3",
                "server": "4611", "farm": 5, "title": "Telegraph Hill - 020918 - 01",
                "ispublic": 1, "isfriend": 0, "isfamily": 0 },
            ] }, "stat": "ok" }

    """
    search = flickr.photos.search(tags='sightseeing, city, travel',
                                  in_gallery=True,
                                  media='photos',
                                  text=attraction,
                                  lat=lat,
                                  lon=lng,
                                  extras='url_sq,url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o',
                                  )

    url = 'https://farm{farm}.staticflickr.com/{server}/{id}_{secret}.jpg'

    imgs = search['photos']['photo'][:10]

    urls = []

    # for img in imgs:
    #     farm = img.get('farm')
    #     server = img.get('server')
    #     user_id = img.get('id')
    #     secret = img.get('secret')
    #     urls.append(url.format(farm=farm, server=server, id=user_id, secret=secret))

    for img in imgs:
      urls.append(img.get('url_q'))

    if urls != []:
        return random.choice(urls)

    else:
        return ""
