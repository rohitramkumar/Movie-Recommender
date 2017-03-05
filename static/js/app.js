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
                    	templateUrl: 'static/partials/partial-header.html',

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
                        templateUrl: 'static/partials/partial-footer.html'
                    }
                }
            })

        	.state('root.home', {
                url: '/',
                views: {
                    'content': {
                        templateUrl: 'static/partials/partial-home.html',
                        controller: function($scope, userService) {
                            $scope.bottles = true;
                            $scope.$watch('$parent.user', function(newValue, oldValue) {
                                    console.log('new user name is found');
                                    console.log(newValue);
                                    console.log(oldValue);
                            });
                        }
                    }
                }
            })

            .state('root.home.movie_detail', {
                url: '/movie_detail',
                views: {
                    'movie_detail': {
                        templateUrl: 'static/partials/partial-movie-detail.html',
                        controller: function($scope, userService) {
                            $scope.movies = ['Die Hard', 'Star Wars', 'Toy Story'];
                        }
                    }
                }
            })

            .state('root.about', {
            url: '/about',
            views: {
                'content': {
                    template: 'About view ... hmm! <p ng-if="user">A user is signed in!</p>'
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
                    template: 'this is only visible after login. Hello {{user.username}}!',
                    controller: function($scope, auth) {
                    	$scope.user = auth;
                    }
                }
            }
    	})
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
                    	$state.go('root.restricted');
                    }
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
