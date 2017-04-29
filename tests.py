import json
import unittest
import mock
from app import process_filtering_request, process_similarity_request, prepare_response
from app_utils import MovieDBApiClient


class AppTest(unittest.TestCase):

    def test_process_filtering_request(self):
        with open("test_json/filtering_req.json", "r") as f:
            j = json.loads(f.read())
            expected = "I found you the following movies: Night at the Museum: Secret of the Tomb, Night at the Museum"
            result = process_filtering_request(j)['speech']
            self.assertEquals(expected, result)

    def test_process_similarity_request(self):
        with open("test_json/similarity_req.json", "r") as f:
            j = json.loads(f.read())
            result = process_similarity_request(j)


class AppUtilsTest(unittest.TestCase):

    def setUp(self):
        self.client = MovieDBApiClient(0, 0)

    def test_get_genre_ids(self):
        result = self.client.get_genre_ids(['Action', 'Adventure', 'Comedy'])
        expected = [28, 12, 35]
        self.assertEquals(result, expected)

    def test_get_cast_ids(self):
        result = self.client.get_cast_ids(
            ['Tom Hardy', 'Tom Hanks', 'Robin Williams'])
        expected = [2524, 31, 2157]
        self.assertEquals(result, expected)

    def test_get_cast_ids_none(self):
        result = self.client.get_cast_ids(['dsfasdfadsfads'])
        expected = []
        self.assertEquals(result, expected)

    def test_encode_url_key_value(self):
        result = self.client.encode_url_key_value(('key', 'value'))
        expected = '&key=value'
        self.assertEquals(result, expected)

    def test_spell_check(self):
        result = self.client.spell_check('Will Farell')
        expected = "Will Ferrell"
        self.assertEquals(result, expected)


if __name__ == "__main__":
    unittest.main()
