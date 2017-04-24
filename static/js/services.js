angular.module('myApp').service('userService', function userServiceFunction($http, $location, $q) {

	var userService = {
    	user: undefined,
        response: undefined,

        // Send user credentials to login API endpoint
    	login: function(userCredentials) {
            var def = $q.defer();

            $http({
                url: "/api/login/",
                method: "POST",
                data: userCredentials
            }).then(function (userObj) {
                if(userObj == "Fail") {
                    console.log("Uh Oh");
                } else {
                    userService.user = userObj;
                }

                def.resolve(userObj);
            });

            return def.promise;

        },

        // Destroy user session
        logout: function() {
        	userService.user = undefined;
        },

        // Send user credentials to signup API endpoint
        signup: function(userCredentials) {
            var def = $q.defer();

            $http({
                url: "/api/signup/",
                method: "POST",
                data: userCredentials
            }).then(function (response) {
                def.resolve(response);
            });

            return def.promise;
        },

        // Add movie info to relevant watchlist API endpoint
        addMovie: function(movieCredentials) {

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

        // Get movie watchlist from relevant API endpoint
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
