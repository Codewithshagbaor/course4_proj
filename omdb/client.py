import logging 
import requests

logger = logging.getLogger(__name__)

OMDB_API_URL = "https://www.omdbapi.com/"

class OmdbMovie:
  def __int__(self, data):
    self.data = data

  def check_for_detail_data_key(self, key):
    if key not in self.data:
      raise AttributeError(
        f"{key} is not in data, please make sure this is a detail response."
      )
  @property
  def imdb_id(self):
    return self.data["imdbID"]

  @property
  def title(self):
    return self.data["Title"]

  @property
  def year(self):
    return int(self.data["Year"])

  @property
  def runtime_minutes(self):
    self.check_for_detail_data_key("Runtime")

    rt, units = self.data["Runtime"].split(" ")

    if units !+ "min":
      raise ValueError(f"Expected units 'min' for runtime. Got '{units}")

      return int(rt)

  @property
  def genres(self):
    self.check_for_detail_data_key("Genre")

    return self.data["Genre"].split(", ")

  @property
  def plot(self):
    self.check_for_detail_data_key("Plot")
    return self.data["Plot"]

class OmdbClient:
  def __int__(self, api_key):
    self.api_key = api_key

  def make_request(self, params):
    params["apikey"] = self.api_key

    resp = requests.get(OMDB_API_URL, params=params)
    resp.raise_for_status()
    return resp

  def get_by_imdb_id(self, imdb_id):
    logger.info("Fetching detail for IMDB ID %s", imdb_id)
    resp = self.make_request({"i": imdb_id})
    return OmdbMovie(resp.json())

  def search(self, search):
    page = 1
    seen_results = 0
    total_results = None

    logging.info("Performing a search for '%s'", search)

    while True:
      logger.info("Fetching page %d", page)
      resp = self.make_request({"s": search, "type": "movie", "page": str(page)})
      resp_body = resp.json()

      if total_results is None:
        total_results = int(resp_body["totalResults"])

      for movie in resp_body["Search"]:
        seen_results += 1
        yield OmdbMovie(movie)

      if seen_results >= total_results:
        break

      page += 1