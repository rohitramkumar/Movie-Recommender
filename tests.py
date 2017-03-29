import unittest
import mock
import json
from app import processFilteringRequest, processSimilarityRequest, prepareResponse

class AppTest(unittest.TestCase):

	def processFilteringRequestTest(self):
		# TODO: fill in real testcases
		# Problem: not regression test since API queries are out of the system
		
		with open("test_movie_query.json", "r") as f:
			req = json.load(f.read())
		moviesResponse = processFilteringRequest(req)
		assert(moviesResponse)
		assertEqual(moviesResponse["speech"], "")
		
		pass

	def processSimilarityRequestTest(self):
		# TODO: fill in real testcases
		# Problem: not regression test since API queries are out of the system

		with open("test_movie_query.json", "r") as f:
			req = json.load(f.read())
		moviesResponse = processFilteringRequest(req)
		assert(moviesResponse)
		assertEqual(moviesResponse["speech"], "")

		pass

	def prepareResponseTest(self):

		testMovies0 = []
		testMovies1 = ["Logan"]
		testMovies2 = ["Logan", "Iron-Man", "Avengers"]

		# {"results":[{"title":""},{"title":""}]}
		self.assertEqual(prepareResponse(testMovies0).get("speech"), "Sorry there are no movies that match your request")
		self.assertEqual(prepareResponse(testMovies1).get("speech"), "I recommend the following movies: Logan")
		self.assertEqual(prepareResponse(testMovies2).get("speech"), "I recommend the following movies: Logan,Iron-Man,Avengers")

	def spellCheckTest(self):
		# need verifying
		self.assertEqual(spellCheck("SuPERNan"), "superman")
		pass

if __name__ == "__main__":
	unittest.main()