const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Petabytz HRMS application.
 |
 */

// Since the static files are already organized, we'll just ensure
// the build process completes successfully
mix.options({
    processCssUrls: false
});

// Create a simple build that doesn't require specific source files
mix.setPublicPath('static/build');

// If there are specific JS files to compile, add them here
// For now, we'll create a minimal setup