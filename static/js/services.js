angular.module('myApp').service('userService', function($http, $location, $q) {

	var userService = {
    	user: undefined,
        response: undefined,
    	login: function(userCredentials) {
            // Send user info to logni endpoint
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
        logout: function() {
        	userService.user = undefined;
        },
        signup: function(userCredentials) {
            // Send user info to signup endpoint
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
                url: "/api/add_movie/",
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
                url: "/api/get_movie_all/",
                method: "POST",
                data: user.email
            }).success(function (response) {
                    def.resolve(response);
            });

            return def.promise;
        }
    }


    return userService;
})
