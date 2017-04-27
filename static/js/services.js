angular.module('myApp').service('userService', function($http, $location, $q) {

	/**
	 * Main service that routes front-end requests through
     * to the back-end API calls or database queries.
	 */
	var userService = {
    	user: undefined, // Tracks if user is logged in or not
        response: undefined,


    	/**
    	 * login - Sends login credentials to login API endpoint.
         * This API communicates with the underlying database.
    	 * @param  {type} loginCredentials a dictionary of username and password
    	 */
    	login: function(loginCredentials) {
            var def = $q.defer();

            $http({
                url: "/api/login/",
                method: "POST",
                data: loginCredentials
            }).success(function (userObj) {
                if(userObj == "Fail") {
                    console.log("Failed to login.");
                } else {
                    userService.user = userObj;
                }

                def.resolve(userObj);
            });

            return def.promise;
        },

        /**
    	 * logout - Resets user session.
    	 *
    	 */
        logout: function() {
        	userService.user = undefined;
        },

        /**
         * signup - Sends user credentials to signup API endpoint.
         * This API communicates with the database.
         * @param  {type} userCredentials a dictionary of user credentials
         */
        signup: function(userCredentials) {
            var def = $q.defer();

            $http({
                url: "/api/signup/",
                method: "POST",
                data: userCredentials
            }).success(function (response) {
                def.resolve(response);
            });

            return def.promise;
        },

        /**
         * addMovieToWatchList - Adds movie to user's watchlist
         * through the relevant watchlist API endpoint.
         * This API communicates with the database.
         *
         * @param  {type} movieCredentials movie information
         */
        addMovieToWatchList: function(movieCredentials) {

            var def = $q.defer();

            $http({
                url: "/api/add_movie_to_watchlist/",
                method: "POST",
                data: movieCredentials
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        },


        /**
         * getUserMovies - Gets movie watchlist for a
         * logged in user through relevant API endpoint.
         * This API communicates with the database.
         */
        getUserMovies: function() {

            var def = $q.defer();

            $http({
                url: "/api/get_watchlist/",
                method: "POST",
                data: userService.user.email
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        },

        /**
         * getLearningRecomendations - Given a user profile
         * containing a list of candidate movies, the underlying
         * API call communicates with the learning server to
         * provide personalized recommendation.
         *
         * @param  {type} userProfile a list of user details and candidate movie list
         */
        getLearningRecomendations: function(userProfile) {

            var def = $q.defer();

            $http({
                url: "/api/get_learning_recommendation/",
                method: "POST",
                data: userProfile
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        },


        /**
         * getGuideboxInfo - Given a list of movie names, returns
         * information about movie showtime, reviews and streaming
         * options.
         * @param  {type} movieList a list of movie names
         */
        getGuideboxInfo: function(movieList) {

            var def = $q.defer();

            $http({
                url: "/api/get_guidebox_info/",
                method: "POST",
                data: movieList
            }).success(function (response) {
                def.resolve(response);
            });

            return def.promise;
        }
    }


    return userService;
})
