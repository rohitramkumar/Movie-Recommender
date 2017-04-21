describe('States', function () {
    // Define global references for injections

	beforeEach(module('myApp'));
	beforeEach(module('ui.router'));

    var $state,
        $rootScope,
        state = 'about';

    // Inject and assign the $state and $rootScope services.
    // Put the template in template cache.
    beforeEach(inject(function (_$state_, $templateCache, _$rootScope_) {
        $state = _$state_;
        $rootScope = _$rootScope_;

        $templateCache.put('static/partials/partial-home.html', '');
    }));

    // Test whether the url is correct
    it('root.home URL', function() {
        expect($state.href('root.home')).toEqual('static/partials/layout.html');
    });

    // Test whether our state activates correctly
    it('root.home state activation', function() {
        $state.go('root.home');
        $rootScope.$digest();
        expect($state.current.name).toBe('root.home');
    });
});

