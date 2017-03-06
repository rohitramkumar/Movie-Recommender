angular.module('myApp').service('userService', function($http, $location, $q) {
    var usersMock = {
    	'testUser': {
        	username: 'testUser',
            password: '1234'
        },
        'testUser2': {
        	username: 'testUser2',
            password: '12345'
        }
    };

	var userService = {
    	user: undefined,
        response: undefined,
    	login: function(userCredentials) {
        	// later --> $http.post('auth', userCredentials).then(...)
            // for demo use local data
            var user = usersMock[userCredentials.username]
            userService.user = ( user && ( user.password == userCredentials.password ) ) ?
            	user : undefined;
            return user;
        },
        logout: function() {
        	userService.user = undefined;
        },
        signup: function(userCredentials) {
            console.log("I'm inside signup!");
            console.log(userCredentials)
            // Send user info to signup endpoint
            var def = $q.defer();

            $http({
                url: "/api/signup/",
                method: "POST",
                data: userCredentials
            }).success(function (response) {
                // Redirect to login upon success
                console.log("About to print response from api below");
                console.log(response);

                def.resolve(response);
            });

            return def.promise;
        }
    }

    return userService;
})
