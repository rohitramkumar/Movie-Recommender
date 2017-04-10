import json
import unittest
import mock
import json
from app import processFilteringRequest, processSimilarityRequest, prepareResponse
from utils import MovieDBApiClient

class AppTest(unittest.TestCase):

    def test_process_filtering_request(self):
        with open("test_json/filtering_req.json", "r") as f:
            j = json.loads(f.read())
            result = processFilteringRequest(j)

    def test_process_similarity_request(self):
        with open("test_json/similarity_req.json", "r") as f:
            j = json.loads(f.read())
            result = processSimilarityRequest(j)

class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.client = MovieDBApiClient(0,0)

    def test_get_genre_ids(self):
        result = self.client.getGenresIds(['Action', 'Adventure', 'Comedy'])
        expected = [28, 12, 35]
        self.assertEquals(result, expected)

    def test_get_cast_ids(self):
        result = self.client.getCastIds(['Tom Hardy', 'Tom Hanks', 'Robin Williams'])
        expected = [2524, 31, 2157]
        self.assertEquals(result, expected)

    def test_get_cast_ids_none(self):
        result = self.client.getCastIds(['dsfasdfadsfads'])
        expected = []
        self.assertEquals(result, expected)

    def test_encode_url_key_value(self):
        result = self.client.encodeURLKeyValue(('key', 'value'))
        expected = '&key=value'
        self.assertEquals(result, expected)
        
if __name__ == "__main__":
    unittest.main()