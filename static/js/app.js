'use strict';   // See note about 'use strict'; below

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
                    	template: '<h1>header View<span ng-if="user"><button ng-click="logout()">logout</button></span><span ng-if="!user"><button ng-click="login()">login</button></span></h1>',

                        controller: function($scope, $state, user, userService) {
                        	$scope.user = user;
                            $scope.login = function() {
                            	$state.go('login');
                            };
                            $scope.logout = function() {
                            	userService.logout();
                                $state.go('root.home', {}, {reload: true});
                            };
                        }
                	},
                    'footer@root': {
                        template: '<p>footer view</p>'
                    }
                }
            })
        	.state('root.home', {
                url: '/',
                views: {
                    'content': {
                        template: 'Hello at home. Maybe this is wheere I can fit my home-partial'
                    }
                }
            })
            .state('root.about', {
            url: '/about',
            views: {
                'content': {
                    template: 'About view ... hmm'
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
                    template: 'this is only visible after login. Hello {{user}}!',
                    controller: function($scope, auth) {
                    	$scope.user = auth.username;
                    }
                }
            }
    	})
        /*
        // HOME STATES AND NESTED VIEWS ========================================
        .state('home', {
            url: '/home',
            templateUrl: 'static/partials/partial-home.html'
        })

        .state('home.movie_detail', {
            url: '/movie_detail',
            templateUrl: 'static/partials/partial-movie-detail.html',
            controller: function($scope, $rootScope) {
                        $scope.movies = ['Die Hard', 'Star Wars', 'The Hobbit'];
                        $rootScope.userIsLoggedIn = true;
            }
        })

        // nested list with just some random string data
        .state('home.paragraph', {
            url: '/paragraph',
            template: 'I could sure use a glass of water right now.',
        })
        */

        .state('login', {
            url: '/login',
            templateUrl: 'static/partials/login.html',
            controller: function($scope, $state, userService) {
            	$scope.login = function(cred) {
                	var user = userService.login(cred);

                    if (angular.isUndefined(user)) {
                    	alert('username or password incorrect.')
                    }
                    else {
                    	$state.go('home.restricted');
                    }
                };
            }
        })


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
