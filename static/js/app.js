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
                    	templateUrl: 'static/partials/nav.html',

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
