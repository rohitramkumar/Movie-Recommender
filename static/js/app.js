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

                    $rootScope.signupRedirect = function() {
                        $state.go('root.signup', {}, {reload: true});
                    };

                    $rootScope.addMovie = function(cred) {
                        userService.addMovie(cred).then(function(response) {
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
                controller: function ($scope, $rootScope, $state, $q, user, userService) {
                    // API.AI Credentials
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

                    // Function to send request to API.AI chat agent
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
                        //setResponse("Loading..."); TO-DO: Add loading animation
                    }

                    // Function to update movie item details using received JSON from API.AI chat agent
                    function setResponse(val) {
                        var respObject = JSON.parse(val);
                        var respStr = respObject.result.fulfillment.speech;

                        $("#spokenResponse").addClass("is-active").find(".spoken-response__text").html(respStr);

                        if (respStr.includes("I found you the following movies")) {
                            console.log("Display movie details!!");
                            console.log(respObject.result.fulfillment.data);
                            var movieList = respObject.result.fulfillment.data;

                            var index = 0;
                            $scope.movies = movieList;
                            $scope.movies.currentMovie = movieList[index];

                            // Navigate movie array through nextMovie() and prevMovie()
                            // TO-DO: Write unit tests for these functions
                            $scope.movies.nextMovie = function() {
                                if (index >= (movieList.length - 1)){
                                    index = 0;
                                } else {
                                    index = index + 1;
                                }

                                $scope.movies.currentMovie = movieList[index];
                            };

                            $scope.movies.prevMovie = function() {
                                if (index < 1 ){
                                    index = movieList.length - 1;
                                } else {
                                    index = index - 1;
                                }

                                $scope.movies.currentMovie = movieList[index];
                            };

                            // Get learning recommendations if user is logged in
                            if (userService.user) {
                                getRecommendations();
                            }

                            $state.go('root.home.movie_detail');
                        }

                        $("#input").val('');
                    }

                    // Function to get learning recommendations from learning agent
                    function getRecommendations() {
                        console.log('in recomenndations');

                        userService.getUserMovies().then(function(resp) {
                            if (angular.isUndefined(resp)) {
                                console.log('Could not retrieve movies')
                            } else if (resp == "Fail") {
                                console.log('Could not retrieve movies')
                            } else {
                                console.log(resp)
                                var userMovies = resp;
                                var candidateList = [];

                                for (var index in userMovies) {
                                    console.log(resp[index]);
                                    var movieObject = userMovies[index];

                                    candidateList.push(movieObject[movie_imdb_id]);
                                }

                                console.log('About to print username');
                                console.log(userService.user.email)

                                console.log('About to print final candidate list');
                                console.log(candidateList);

                                return candidateList;
                            }
                        }).then(function(requestObj) {
                            console.log('I am in the next cascasde and got the thing below!');
                            console.log(requestObj);
                        });
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
                    //$window.location.reload()

                }
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
                            var userMovies = resp;
                            var candidateList = []
                            for (movie in userMovies) {
                                candidateList.push(movie.imdb_id);
                            }
                            console.log('About to print final candidate list');
                            console.log(candidateList);
                        }
                    });
                }
            }
        }
    })

    .state('root.signup', {
        url: '/signup',
        views: {
            'content': {
                templateUrl: 'static/partials/partial-signup.html',
                controller: function($scope, $rootScope, $q, $state, userService) {
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
