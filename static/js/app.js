'use strict';   // See note about 'use strict'; below

var myApp = angular.module('myApp', [
 'ngRoute',
]);

myApp.config(['$routeProvider',
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
