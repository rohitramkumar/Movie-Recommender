angular.module('myApp').service('userService', function($http) {
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

            var response = {
                errorStatus: 'this is fine'
            }

            return response;
        }
    }

    return userService;
})
