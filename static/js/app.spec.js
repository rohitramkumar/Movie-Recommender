describe('States', function () {
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

describe('Login', function () {
    	beforeEach(module('myApp'));
	beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        state = 'root.login';

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
    
    //Test failed logins
    
    var resp = undefined;
    it('tests if correct error message shows with undefined response', function(resp, done){
        spyOn(window, 'alert');
        expect(window.alert).toHaveBeenCalledWith('username or password incorrect.');
        done();
    });
    
    resp = "Success";
    
    resp = "";
    
    
    
});



