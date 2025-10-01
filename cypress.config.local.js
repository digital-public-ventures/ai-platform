const { defineConfig } = require('cypress');

module.exports = defineConfig({
	e2e: {
		baseUrl: 'http://localhost:8080',
		viewportWidth: 1280,
		viewportHeight: 720,
		video: true,
		screenshotOnRunFailure: true,
		defaultCommandTimeout: 10000,
		requestTimeout: 10000,
		responseTimeout: 10000,
		// Useful for local development
		watchForFileChanges: true
	},
	video: true,
	videosFolder: 'cypress/videos',
	screenshotsFolder: 'cypress/screenshots'
});
