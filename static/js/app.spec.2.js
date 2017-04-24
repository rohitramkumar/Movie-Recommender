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
        alert = jasmine.createSpy();
        $rootScope.login(undefined);
        // expect alert here
        $rootScope.$digest();
        expect(alert).toHaveBeenCalledWith('Username or password incorrect.');

        $httpBackend.expectPOST("/api/login/").respond("Fail");
        $rootScope.login({"username": "nonsense", "passwords": "nonsense"});
        $rootScope.$digest();
        // expect alert here

        $httpBackend.expectPOST("/api/login/").respond("Fail");
        $rootScope.login({"username": "...", "passwords": "..."});
        $rootScope.$digest();
        // expect state transition here
        expect($state.current.name).toBe('root.home');
        
    });
/*
    it('root.home logout controller', function() {
        $state.go(state, {}, {reload: true});
        $rootScope.$digest();
        var controller = $controller($scope, $rootScope, $state, $q, user, userService);
        
        $rootScope.login({"username": "...", "passwords": "..."});
        $rootScope.$digest();
        // expect state transition here
        expect($state.current.name).toBe('root.home');

        $rootScope.$logout();
        $rootScope.$digest();
        expect(userService.user).toBe(undefined);
        expect($state.current.name).toBe('root.home');
    });

    it('root.home send controller', function() {
        $state.go(state, {}, {reload: true});
        $rootScope.$digest();
        // var controller = $controller($scope, $rootScope, $state, $q, user, userService);
        
        $rootScope.login(undefined);
        // expect alert here
        $rootScope.login({"username": "nonsense", "passwords": "nonsense"});
        // expect alert here
        $rootScope.login({"username": "...", "passwords": "..."});
        $rootScope.$digest();
        // expect state transition here
        expect($state.current.name).toBe('root.home');
    });
*/
});

