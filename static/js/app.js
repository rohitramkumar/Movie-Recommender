'use strict';   // See note sign_up 'use strict'; below

var movieApp = angular.module('myApp', [
 'ui.router'
]);

movieApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider

    .state('root', {
            	url: '',
            	abstract:true,
                resolve: {
                	'user': function(userService) {
                    	return userService.user; // would be async in a real app
                    }
                },
                views: {
                	'': {
                    	templateUrl: 'static/partials/layout.html',
                    },
                	'header@root': {
                    	templateUrl: 'static/partials/partial-header.html',

                        controller: function($scope, $rootScope, $state, user, userService) {
                        	$rootScope.user = user;
                            $rootScope.login = function() {
                            	$state.go('login');
                            };
                            $rootScope.logout = function() {
                            	userService.logout();
                                $state.go('root.home', {}, {reload: true});
                            };
                            $rootScope.signup = function() {
                                $state.go('sign_up');
                            };
                        }
                	},
                    'footer@root': {
                        templateUrl: 'static/partials/partial-footer.html'
                    }
                }
            })

        	.state('root.home', {
                url: '/',
                views: {
                    'content': {
                        templateUrl: 'static/partials/partial-home.html'
                    }
                }
            })

            .state('root.home.movie_detail', {
                url: '/movie_detail',
                views: {
                    'movie_detail': {
                        templateUrl: 'static/partials/partial-movie-detail.html',
                        controller: function($scope, $rootScope, userService) {
                            $scope.movies = ['Die Hard', 'Star Wars', 'Toy Story'];
                        }
                    }
                }
            })

            .state('root.sign_up', {
            url: '/sign_up',
            views: {
                'content': {
                    template: 'sign_up view ... hmm! <p ng-if="user">A user is signed in!</p>'
                }
            }
    	})

        .state('root.restricted', {
            url: '/restricted',
            resolve: {
            	auth: function(userService, $q, $timeout) {

                	var deferred = $q.defer();
                	/* //with an async
                    return UserService.load().then(function(user){
                      if (permissionService.can(user, {goTo: state})) {
                        return deferred.resolve({});
                      } else {
                        return deferred.reject({redirectTo: 'some_other_state'});
                      }
                    }*/

                   $timeout(function() {
                        if ( angular.isUndefined(userService.user) ) {
                            return deferred.reject({redirectTo: 'login'});
                        }
                        else {
                            return deferred.resolve(userService.user);
                        }
                    });

                    return deferred.promise;
                }
            },
            views: {
                'content': {
                    templateUrl: 'static/partials/partial-profile.html',
                    controller: function($scope, $rootScope, auth) {
                    	$rootScope.user = auth;
                    }
                }
            }
    	})

        .state('login', {
            url: '/login',
            templateUrl: 'static/partials/partial-login.html',
            controller: function($scope, $state, $q, userService) {
            	$scope.login = function(cred) {
                    console.log("Clicky happended");
                	userService.login(cred).then(function(resp) {
                        console.log("Got a response");
                        console.log(resp);

                        if (angular.isUndefined(resp)) {
                            console.log("Here");

                        	alert('username or password incorrect.')
                        } else if (resp == "Fail") {
                            console.log("Failing");

                            alert('username or password incorrect.')
                        }
                        else {
                            console.log("Logged in app js");
                            alert('Thanks for logging in!')

                        	$state.go('root.home');
                        }
                    });
                };
            }
        })

        .state('sign_up', {
            url: '/signup',
            templateUrl: 'static/partials/partial-signup.html',
            controller: function($scope, $state, $q, userService) {
                $scope.signup = function(cred) {
                    userService.signup(cred).then(function(response) {
                            if(response == "Success") {
                                alert('Succesfuly signed up');
                                $state.go('root.home');
                            } else {
                                alert(response);
                            }
                    });
                };
            }
        });
});

movieApp.run(function ($rootScope) {
    $rootScope.$on('$stateChangeError', function(evt, to, toParams, from, fromParams, error) {
        if (error.redirectTo) {
            $state.go(error.redirectTo);
        } else {
            $state.go('error', {status: error.status})
        }
    });
});
