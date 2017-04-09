angular.module('myApp').service('userService', function($http, $location, $q) {

	var userService = {
    	user: undefined,
        response: undefined,
        // Send user info to login API endpoint
    	login: function(userCredentials) {
            var def = $q.defer();

            $http({
                url: "/api/login/",
                method: "POST",
                data: userCredentials
            }).success(function (userObj) {
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

        // Send user info to signup API endpoint
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
        add_movie: function(userCredentials) {

            var def = $q.defer();

            $http({
                url: "/api/add_movie_to_watchlist/",
                method: "POST",
                data: userCredentials
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        },
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
        getMovieData: function() {

            var def = $q.defer();

            $http({
                url: "/api/getFullMovieDetails/",
                method: "POST",
                data: userService.user.email
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        }
    }


    return userService;
})
