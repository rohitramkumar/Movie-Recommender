'use strict';


/**
 *  Movie App Module
 */
var movieApp = angular.module('myApp', [
    'ui.router'
]);


/**
 * Declaring all states for Movie App Module
 */
movieApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider

    .state('root', {
        url: '',
        abstract:true,
        resolve: {
            'user': function(userService) {
                return userService.user;
            }
        },
        views: {
            '': {
                templateUrl: 'static/partials/layout.html',
                controller: function($scope, $rootScope, $state, $q, user, userService) {
                    $rootScope.user = user;


                    /**
                     * Login - Takes user credentials from front-end html
                     * and passes them to the relevant login function in the user
                     * service.
                     *
                     * @param  {type} credentials user credentials consisting of username and password
                     */
                    $rootScope.login = function(credentials) {
                        userService.login(credentials).then(function(resp) {

                            if (angular.isUndefined(resp)) {
                                alert('Did not get response from back-end')
                            } else if (resp == "Fail") {
                                alert('Username or password incorrect.')
                            }
                            else {
                                alert('Thanks for logging in!')
                                $state.go('root.home', {}, {reload: true});
                            }
                        });
                    };

                    /**
                     * Logout - Calls the relevant logout function
                     * in user service. Redirects to homepage as a result.
                     */
                    $rootScope.logout = function() {
                        userService.logout();
                        $state.go('root.home', {}, {reload: true});
                    };


                    /**
                     * Sign-up Redirect - Redirects the user to the sign-up
                     * state.
                     */
                    $rootScope.signupRedirect = function() {
                        $state.go('root.signup', {}, {reload: true});
                    };
                }
            },
            'header@root': {
                templateUrl: 'static/partials/partial-header.html'
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

                /**
                 * Home Controller - Responsible for all functionality on the home
                 * page. This includes any interaction with the chat agent and all
                 * functions populating movie detail or recommendation information.
                 */
                controller: function ($scope, $rootScope, $state, $q, user, userService) {
                    // API.AI Access Token
                    var accessToken = "d9854338952446d589f83e6a575e0ba4";
                    var baseUrl = "https://api.api.ai/v1/";

                    // On Document Load Javascriptality
                    angular.element(document).ready(function () {

                        // Handles input to interact with the chat agent
                        $("#input").keypress(function(event) {
                            if (event.which == 13) {
                                event.preventDefault();
                                sendToChatAgent();
                            }
                        });
                    });


                    /**
                     * sendToChatAgent - Sends typed input to the API.AI chat
                     * agent. Sends a POST http request to API.AI.
                     */
                    function sendToChatAgent() {
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
                    }

                    /**
                     * setResponse - Updates movie item details using received JSON from API.AI chat agent
                     *
                     * @param  {type} value the data received from the chat agent
                     */
                    function setResponse(value) {
                        var respObject = JSON.parse(value);
                        var respStr = respObject.result.fulfillment.speech;

                        // Update appropriate HTML objects with response via jQuery
                        $("#spokenResponse").addClass("is-active").find(".spoken-response__text").html(respStr);

                        // If movie recommnedations are passed on from the chat agent, displays them
                        if (respStr.includes("I found you the following movies")) {
                            var movieList = respObject.result.fulfillment.data;

                            var index = 0;
                            $scope.movies = movieList;

                            // Get movie showtimes and streaming information
                            getMovieInfo($scope.movies);

                            // Assign current movie to be displayed by front-end
                            $scope.movies.currentMovie = movieList[index];

                            /**
                             * nextMovie - Iterate through movie array and movie info array as per front-end HTML button.
                             * Updates the current movie being displayed.
                             */
                            $scope.nextMovie = function() {
                                if (index >= (movieList.length - 1)) {
                                    index = 0;
                                } else {
                                    index = index + 1;
                                }

                                $scope.movies.currentMovie = movieList[index];
                                if ($scope.movieInfo) {
                                    $scope.movieInfo.currentMovie = $scope.movieInfo[($scope.movies.currentMovie).original_title];
                                }

                                if ($scope.movieInfo.currentMovie) {
                                    validateStreamingList($scope.movieInfo.currentMovie.streaming);
                                }
                            };

                            /**
                             * prevMovie - Iterate through movie array and movie info array as per front-end HTML button.
                             * Updates the current movie being displayed.
                             */
                            $scope.prevMovie = function() {
                                if (index < 1) {
                                    index = movieList.length - 1;
                                } else {
                                    index = index - 1;
                                }

                                $scope.movies.currentMovie = movieList[index];
                                $scope.movieInfo.currentMovie = $scope.movieInfo[($scope.movies.currentMovie).original_title];

                                if ($scope.movieInfo.currentMovie) {
                                    validateStreamingList($scope.movieInfo.currentMovie.streaming);
                                }
                            };

                            // If user is logged in, get learning recommendations
                            if (userService.user) {
                                getRecommendations($scope.movies);
                            }

                            // Display movie detail
                            $state.go('root.home.movie_detail');
                        }

                        // Reset input field to blank state
                        $("#input").val('');

                        // Hack to get incoming movie details if user asked for more movies.
                        $("#nextResult").trigger("click");
                        $("#previousResult").trigger("click");
                    }


                    /**
                     * getMovieInfo - Given a list of movies, routes the list through
                     * to revelant user service function getGuideboxInfo() in order to request
                     * movie showtimes, reviews and streaming options.
                     *
                     * @param  {type} movieList a list of movie objects
                     */
                    function getMovieInfo(movieList) {
                        var userMovies = movieList;
                        var movieNameList = [];

                        for (var index in userMovies) {
                            var movieObject = userMovies[index];
                            movieNameList.push(movieObject['original_title']);
                        }

                        var request = {movieNames:movieNameList};

                        userService.getGuideboxInfo(request).then(function(resp) {
                            if (angular.isUndefined(resp)) {
                                console.log('Did not get response from back-end');
                            } else if (resp == "Fail") {
                                console.log('Could not retrieve showtimes');
                            } else {
                                $scope.movieInfo = resp;
                                $scope.movieInfo.currentMovie = $scope.movieInfo[($scope.movies.currentMovie).original_title];

                                if ($scope.movieInfo.currentMovie) {
                                    validateStreamingList($scope.movieInfo.currentMovie.streaming);
                                }
                            }
                        });
                    }

                    /**
                     * validateStreamingList - Capitalizes first word for each streaming option name.
                     * Also removes any underscores.
                     *
                     * @param  {type} streamList a list of streaming options
                     */
                    function validateStreamingList(streamList) {
                        for (var index in streamList) {
                            var streamObj = streamList[index].source;
                            var tokenList = streamObj.split('_');
                            var finalStreamObj = "";

                            for (var token in tokenList) {
                                var tempStr = tokenList[token].charAt(0).toUpperCase() + tokenList[token].slice(1);
                                finalStreamObj += tempStr + ' ';
                            }

                            streamList[index].source = finalStreamObj;
                        }
                    }

                    /**
                     * getRecommendations - Takes as input a list of movies, routes them through
                     * the relevant user service function to get learning recommendations from
                     * the learning agent
                     *
                     * @param  {type} movieList a list of movie objects
                     */

                    function getRecommendations(movieList) {
                        var userMovies = movieList;
                        var movieIDList = [];

                        for (var index in userMovies) {
                            var movieObject = userMovies[index];
                            movieIDList.push(movieObject['imdb_id']);
                        }

                        // Remove duplicate movie entry from the end of the list
                        movieIDList = movieIDList.slice(0, -1);

                        // Prepare request from the current movie candidate list
                        var userProfile = {user_id:userService.user.id, candidateList:movieIDList};

                        userService.getLearningRecomendations(userProfile)
                        .then(function(resp) {
                            if (angular.isUndefined(resp)) {
                                console.log('Could not retrieve recommendations');
                            } else {
                                var index = 0; // Default index is 0 to retrieve entry at head
                                var recommendationList = resp;
                                $scope.recommendations = recommendationList;

                                // Sometimes the server responds with an error string
                                if (typeof finalResp === 'string') {
                                    $scope.recommendations = "Could not provide user recommendation :(";
                                    return;
                                }

                                // Set current recommendation to be displayed
                                $scope.recommendations.currentRecommendation = $scope.movies[index];

                                // Find the movie at the head of the recommendation list
                                for (var num in $scope.movies) {
                                    if (recommendationList[index] == $scope.movies[num].imdb_id) {
                                        $scope.recommendations.currentRecommendation = $scope.movies[num];
                                        break;
                                    }
                                }
                            }
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

                /**
                * Movie Detail Controller - Responsible for all content on the
                * movie detail state. This includes any movie detail displayed and
                * functionality to rate a movie and add it to user watchlist.
                */
                controller: function($scope, $rootScope, $state, $q, user, userService) {


                    /**
                     * addMovie - Adds current movie being displayed to a logged
                     * in user's watchlist.
                     *
                     * @param  {type} ratingObject contains user rating for the movie to be added
                     */
                    $scope.addMovie = function(ratingObject) {
                        var curMovieObject = {"username":userService.user.email, "user_id":userService.user.id, "movieName":$scope.movies.currentMovie.original_title, "movieImdbId":$scope.movies.currentMovie.imdb_id, "rating":ratingObject.movieRating};

                        userService.addMovieToWatchList(curMovieObject).then(function(response) {
                            if (response == "Success") {
                                alert('Succesfully added movie to your watchlist!');
                            } else {
                                alert(response);
                            }
                        });
                    };
                }
            }
        }
    })

    .state('root.restricted', {
        url: '/profile',
        resolve: {

            /**
             * auth - Ensures that only a logged in user can
             * access profile page. Otherwise redirects to
             * the login state.
             */
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

                /**
                * User Profile Controller - Responsible for all content on the
                * logged in user's profile page. This includes any movies in a
                * user's watchlist. Calls user service getUserMovies() when
                * instantiated.
                */
                controller: function($scope, $rootScope, auth, userService) {
                    $rootScope.user = auth;

                    userService.getUserMovies().then(function(resp) {
                        if (angular.isUndefined(resp)) {
                            console.log('Did not get response from back-end')
                        } else if (resp == "Fail") {
                            console.log('Could not retrieve movies')
                        } else {
                            $scope.userMovies = resp;
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
                /**
                * Sign Up Controller - Responsible for the registeration
                * process for a new user.
                */
                controller: function($scope, $rootScope, $q, $state, userService) {

                    /**
                     * signup - Takes in user credentials as input and
                     * routes them through to the relevant user service function
                     * which communicates with the backend database.
                     *
                     * @param  {type} credentials a dictionary of user credentials
                     */
                    $scope.signup = function(credentials) {
                        userService.signup(credentials).then(function(response) {
                            if (response == "Success") {
                                // Redirects to home page after succesfuly regsitered
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
