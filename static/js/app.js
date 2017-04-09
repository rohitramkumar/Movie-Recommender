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
                        controller: function($scope, $rootScope, $state, $q, user, userService) {
                            $rootScope.user = user;
                            $rootScope.login = function(cred) {
                                userService.login(cred).then(function(resp) {

                                    if (angular.isUndefined(resp)) {
                                        alert('username or password incorrect.')
                                    } else if (resp == "Fail") {
                                        alert('Username or password incorrect.')
                                    }
                                    else {
                                        alert('Thanks for logging in!')
                                        $state.go('root.home', {}, {reload: true});
                                    }
                                });
                            };
                            $rootScope.logout = function() {
                                userService.logout();
                                $state.go('root.home', {}, {reload: true});
                            };
                            $rootScope.signup = function() {
                                $state.go('sign_up');
                            };
                            $rootScope.add_movie = function(cred) {
                                userService.add_movie(cred).then(function(response) {
                                    if(response == "Success") {
                                        alert('Succesfuly added movie');
                                    } else {
                                        alert(response);
                                    }
                                });
                            };
                        }
                    },
                	'header@root': {
                    	templateUrl: 'static/partials/partial-header.html',
                        controller: function($scope, $rootScope, $state, $q, user, userService) {
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
                        controller: function ($scope, $rootScope, $state) {
                            var accessToken = "d9854338952446d589f83e6a575e0ba4";
                            var baseUrl = "https://api.api.ai/v1/";

                            angular.element(document).ready(function () {

                                $("#input").keypress(function(event) {
                                    if (event.which == 13) {
                                        event.preventDefault();
                                        send();
                                    }
                                });

                    			$("#rec").click(function(event) {
                    				send();
                    			});
                            });

                            function send() {
                                var text = $("#input").val();
                                $.ajax({
                                    type: "POST",
                                    url: baseUrl + "query?v=20150910",
                                    contentType: "application/json; charset=utf-8",
                                    dataType: "json",
                                    headers: {
                                        "Authorization": "Bearer " + accessToken
                                    },
                                    data: JSON.stringify({ query: text, lang: "en", sessionId: "a_session" }),
                                    success: function(data) {
                                        setResponse(JSON.stringify(data, undefined, 2));
                                    },
                                    error: function() {
                                        setResponse("Internal Server Error");
                                    }
                                });
                                //setResponse("Loading...");
                            }

                            function setResponse(val) {
                                var respObject = JSON.parse(val);
                                var respStr = respObject.result.fulfillment.speech;

                                $("#spokenResponse").addClass("is-active").find(".spoken-response__text").html(respStr);

                                if (respStr.includes("I found you the following movies")) {
                                    console.log(respObject.result.fulfillment.data);
                                    $scope.movies = respObject.result.fulfillment.data;
                                    $state.go('root.home.movie_detail', {}, {reload: true});
                                }

                                $("#input").val('');
                            }
                        }
                    }
                }
            })

            .state('root.home.movie_detail', {
                url: '/movie_detail',
                views: {
                    'movie_detail': {
                        templateUrl: 'static/partials/partial-movie-detail.html',
                        controller: function($scope, $rootScope) {
                            console.log("I am a placeholder function!");
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
            url: '/profile',
            resolve: {
            	auth: function(userService, $q, $timeout) {

                    var deferred = $q.defer();

                    $timeout(function() {
                        if (angular.isUndefined(userService.user) ) {
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
                    controller: function($scope, $rootScope, auth, userService) {
                    	$rootScope.user = auth;

                        userService.getUserMovies().then(function(resp) {

                            if (angular.isUndefined(resp)) {
                                console.log('Could not retrieve movies')
                            } else if (resp == "Fail") {
                                console.log('Could not retrieve movies')
                            } else {
                                console.log(resp)
                                $scope.userMovies = resp;
                            }
                        });
                    }
                }
            }
    	})

        .state('login', {
            url: '/login',
            templateUrl: 'static/partials/partial-login.html',
            controller: function($scope, $state, $q, userService) {
            	$scope.login = function(cred) {
                	userService.login(cred).then(function(resp) {

                        if (angular.isUndefined(resp)) {
                        	alert('username or password incorrect.')
                        } else if (resp == "Fail") {
                            alert('Username or password incorrect.')
                        }
                        else {
                            alert('Thanks for logging in!')
                            console.log($scope.user)
                        	$state.go('root.home');
                        }
                    });
                };
            }
        })

        .state('sign_up', {
            url: '/signup',
            views: {
                'content': {
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
                }
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
