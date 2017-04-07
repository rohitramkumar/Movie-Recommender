import json
import unittest
import mock
from app import processFilteringRequest, processSimilarityRequest, prepareResponse

class AppTest(unittest.TestCase):

    def test_process_filtering_request(self):
        with open("test_json/filtering_req.json", "r") as f:
            j = json.loads(f.read())
            result = processFilteringRequest(j)
            self.assertEqual(result["speech"], "I found you the following movies: Mad Max: Fury Road, The Dark Knight Rises")

    def test_process_similarity_request(self):
        pass

if __name__ == "__main__":
    unittest.main()
