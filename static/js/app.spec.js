describe('states', function () {
    // Define global references for injections

    beforeEach(module('myApp'));
    beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        state = 'root.home';

    // Inject and assign the $state and $rootScope services.
    // Put the template in template cache.
    beforeEach(inject(function (_$state_, $templateCache, _$rootScope_) {
        $state = _$state_;
        $rootScope = _$rootScope_;

        $templateCache.put('static/partials/partial-home.html', '');
        $templateCache.put('static/partials/partial-header.html', '');
        $templateCache.put('static/partials/partial-footer.html', '');
        $templateCache.put('static/partials/layout.html', '');
        $templateCache.put('static/partials/partial-movie-detail.html', '');
        $templateCache.put('static/partials/partial-login.html', '');
    }));

    // Test whether the url is correct
    it('root URL', function() {
        // expect($state.href(state)).toEqual('root.home');
    });

    // Test whether our state activates correctly
    it('root.home state activation', function() {
        $state.go(state, {}, {reload: true});
        $rootScope.$digest();
        // expect($state.href(state)).toEqual('root.home');
        expect($state.current.name).toBe(state);
        expect($state.current.name).toBe('root.home');
    });

    // Test whether our state activates correctly
    it('root.home state activation', function() {

        $state.go(state, {}, {reload: true});
        $rootScope.$digest();
        // expect($state.href(state)).toEqual('root.home');
        expect($state.current.name).toBe(state);
        expect($state.current.name).toBe('root.home');

        $state.go('root.home.movie_detail');
        $rootScope.$digest();
        expect($state.current.name).toBe('root.home.movie_detail');

        $state.go('login');
        $rootScope.$digest();
        expect($state.current.name).toBe('login');

    });
});

describe('root controllers', function () {
    // Define global references for injections

    beforeEach(module('myApp'));
    beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        $scope,
        $controller,
        $q,
        user,
        userService,
        $httpBackend,
        state = 'root.home';

    var timeout = 1500;

    // Inject and assign the $state and $rootScope services.
    // Put the template in template cache.
    beforeEach(inject(function (_$state_, $templateCache, _$rootScope_, _$controller_, _$q_, _userService_, _$httpBackend_) {
        $state = _$state_;
        console.log($state.current.name);
        $rootScope = _$rootScope_;
        $controller = _$controller_;
        $q = _$q_,
        userService = _userService_,
        $httpBackend = _$httpBackend_;

        $templateCache.put('static/partials/partial-home.html', '');
        $templateCache.put('static/partials/partial-header.html', '');
        $templateCache.put('static/partials/partial-footer.html', '');
        $templateCache.put('static/partials/layout.html', '');
        $templateCache.put('static/partials/partial-movie-detail.html', '');
        $templateCache.put('static/partials/partial-login.html', '');
    }));

    it('root.home login controller', function() {
        $state.go(state);
        // $state.go('root.home.movie_detail');
        $rootScope.$digest();

        user = $q.defer().resolve("user");
        // $controller = $state.current.controller;
        console.log($controller);

        var controller = $controller('rootController', {$scope: $scope, $rootScope: $rootScope, $state: $state, $q: $q, user: user, userService: userService});

        $httpBackend.expectPOST("/api/login/").respond("Fail");
        spyOn(window, 'alert');
        alert = jasmine.createSpy();

        var msg = $rootScope.login(undefined);
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(msg).toBe('Username or password incorrect.');
            expect(alert).toHaveBeenCalledWith('Username or password incorrect.');
        }, timeout);

        $httpBackend.expectPOST("/api/login/").respond("Fail");
        $rootScope.login({"username": "nonsense", "passwords": "nonsense"});
        // done();
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(msg).toBe('Username or password incorrect.');
            expect(alert).toHaveBeenCalledWith('Username or password incorrect.');
        }, timeout);

        $httpBackend.expectPOST("/api/login/").respond({"username": "user2", "passwords": "pass"});
        $rootScope.login({"username": "user2", "passwords": "pass"});
        // done();
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(msg).toBe('Thanks for logging in!');
            expect(alert).toHaveBeenCalledWith('Thanks for logging in!');
            // done();
        }, timeout);
    });

    it('root.home logout controller', function() {
        $state.go(state, {}, {reload: true});
        $rootScope.$digest();
        var controller = $controller('rootController', {$scope: $scope, $rootScope: $rootScope, $state: $state, $q: $q, user: user, userService: userService});

        $httpBackend.expectPOST("/api/login/").respond({"username": "user2", "passwords": "pass"});
        $rootScope.login({"username": "user2", "passwords": "pass"});
        $rootScope.$digest();
        

        setTimeout(function() {
            expect(userService.user).toBe({"username": "user2", "passwords": "pass"});
            expect(userService.user).toBe("fdgdsf");
        }, timeout);

        $rootScope.logout();
        $rootScope.$digest();
        setTimeout(function() {
            expect(userService.user).toBe(undefined);
        }, timeout);
    });

});

describe ('root.signup controllers', function(){
    beforeEach(module('myApp'));
    beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        $scope,
        $controller,
        $q,
        user,
        userService,
        $httpBackend,
        state = 'root.signup';

    var timeout = 1500;

    // Inject and assign the $state and $rootScope services.
    // Put the template in template cache.
    beforeEach(inject(function (_$state_, $templateCache, _$rootScope_, _$controller_, _$q_, _userService_, _$httpBackend_) {
        $state = _$state_;
        console.log($state.current.name);
        $rootScope = _$rootScope_;
        $controller = _$controller_;
        $q = _$q_,
        userService = _userService_,
        $httpBackend = _$httpBackend_;

        $templateCache.put('static/partials/partial-home.html', '');
        $templateCache.put('static/partials/partial-header.html', '');
        $templateCache.put('static/partials/partial-footer.html', '');
        $templateCache.put('static/partials/layout.html', '');
        $templateCache.put('static/partials/partial-movie-detail.html', '');
        $templateCache.put('static/partials/partial-login.html', '');
        $templateCache.put('static/partials/partial-signup.html', '');
    }));
    
    it('signup controller', function() {
        $state.go(state);
        // $state.go('root.home.movie_detail');
        $rootScope.$digest();
        
        user = $q.defer().resolve("user");
        // $controller = $state.current.controller;
        console.log($controller);

        var controller = $controller('signupController', {$scope: $scope, $rootScope: $rootScope, $state: $state, $q: $q, user: user, userService: userService});

        // $httpBackend.expectPOST("/api/signup/").respond("Fail");
        alert = jasmine.createSpy();
        
        var str = $rootScope.str;
        $httpBackend.expectPOST("/api/signup/").respond("Success");
        $rootScope.signup({"username": "newUser", "passwords": "newPass"});
        $rootScope.$digest();

        setTimeout(function() {
            expect(str).toBe('Succesfuly signed up');
        }, timeout);
        
        $httpBackend.expectPOST("/api/signup/").respond("Fail");
        $rootScope.signup(undefined);
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(str).toBe('Could not sign up');
        }, timeout);

    });
    
});

describe('recommendation', function(){
    beforeEach(module('myApp'));
    beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        $scope,
        $controller,
        $q,
        user,
        userService,
        $httpBackend,
        state = 'root.home';

        var timeout = 1500;

    // Inject and assign the $state and $rootScope services.
    // Put the template in template cache.
    beforeEach(inject(function (_$state_, $templateCache, _$rootScope_, _$controller_, _$q_, _userService_, _$httpBackend_) {
        $state = _$state_;
        console.log($state.current.name);
        $rootScope = _$rootScope_;
        $controller = _$controller_;
        $q = _$q_,
        userService = _userService_,
        $httpBackend = _$httpBackend_;

        $templateCache.put('static/partials/partial-home.html', '');
        $templateCache.put('static/partials/partial-header.html', '');
        $templateCache.put('static/partials/partial-footer.html', '');
        $templateCache.put('static/partials/layout.html', '');
        $templateCache.put('static/partials/partial-movie-detail.html', '');
        $templateCache.put('static/partials/partial-login.html', '');
    }));
    
    it('getMovies', function() {
        $state.go(state);
        // $state.go('root.home.movie_detail');
        $rootScope.$digest();
        
        user = $q.defer().resolve("user");
        // $controller = $state.current.controller;
        console.log($controller);

        var controller = $controller('homeController', {$scope: $scope, $rootScope: $rootScope, $state: $state, $q: $q, user: user, userService: userService});

        var str = $rootScope.str;
        $httpBackend.whenPOST("/api/get_watchlist/").respond("Fail");
        
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(str).toBe('Could not get movies');
        }, timeout);
        
        $httpBackend.whenPOST("api/get_watchlist/").respond("Success");
        $rootScope.$digest();
        
        setTimeout(function() {
            expect(str).toBe('retrieved movies');
        }, timeout);

    });
});