module.exports = function(config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine'],
    files: [
      '/usr/local/lib/node_modules/angular/angular.js',
      '/usr/local/lib/node_modules/angular/angular.min.js',
      '/usr/local/lib/node_modules/angular-mocks/angular-mocks.js',
      '/usr/local/lib/node_modules/angular-ui-router/release/*.js',
      'app.js',
      'services.js',
      'app.spec.js'
    ],
    browsers: ['Chrome'],
    singleRun: true,
    reporters: ['progress', 'coverage'],
    preprocessors: { '*.js': ['coverage'] }
  });
};