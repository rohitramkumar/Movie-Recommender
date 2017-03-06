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
                            	$state.go('root.login');
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


        .state('root.restricted', {
            url: '/restricted',
            resolve: {
            	auth: function(userService, $q, $timeout) {
                    // TO-DO: Should this by async too?
                    var deferred = $q.defer();

                    $timeout(function() {
                        if ( angular.isUndefined(userService.user) ) {
                            return deferred.reject({redirectTo: 'root.login'});
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

        .state('root.login', {
            url: '/login',
            views: {
                'content': {
                    templateUrl: 'static/partials/partial-login.html',
                    controller: function($scope, $state, $q, userService) {
                    	$scope.login = function(cred) {
                        	userService.login(cred).then(function(resp) {
                                if (angular.isUndefined(resp)) {
                                	alert('Unhandled exception :|')
                                } else if (resp == "Fail") {
                                    alert('username or password incorrect.')
                                }
                                else {
                                    alert('Thanks for logging in!')
                                	$state.go('root.home');
                                }
                            });
                        };
                    }
                }
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
