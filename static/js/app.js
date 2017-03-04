'use strict';   // See note about 'use strict'; below

var movieApp = angular.module('myApp', [
 'ui.router',
]);

routerApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');
    $stateProvider
        // HOME STATES AND NESTED VIEWS ========================================
        .state('home', {
            url: '/home',
            templateUrl: 'static/partials/partial-home.html'
        })

        // nested list with custom controller
        .state('home.movie_detail', {
            url: '/movie_detail',
            templateUrl: 'partial-movie-detail.html',
            controller: function($scope) {
                        $scope.movies = ['Die Hard', 'Star Wars', 'The Hobbit'];
            }
        })

        // nested list with just some random string data
        .state('home.paragraph', {
            url: '/paragraph',
            template: 'I could sure use a glass of water right now.'
        })

        // ABOUT PAGE AND MULTIPLE NAMED VIEWS =================================
        .state('about', {
            // we'll get to this in a bit
        });

});

/*movieApp.config(['$routeProvider',
     function($routeProvider) {
         console.log("I'm trying to resolve routes!");
         $routeProvider.
             when('/', {
                 templateUrl: 'static/partials/index.html',
             }).
             when('/about', {
                 templateUrl: 'static/partials/about.html',
             }).
             when('/sign-up', {
                 templateUrl: 'static/partials/sign-up.html',
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);
*/
