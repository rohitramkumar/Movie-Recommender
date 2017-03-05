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
        }
    }

    return userService;
})

angular.module('myApp').service('movieService', function($http) {
    var usersMock = {
    	'testMovie': {
        	name: 'testMovie1',
            movie_id: '12734'
        },
        'testMovie2': {
        	username: 'testMovie2',
            password: '945'
        }
    };

	var movieService = {
    	movie: undefined,
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
        }
    }

    return userService;
})
