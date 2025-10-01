/// <reference types="cypress" />
// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

export const adminUser = {
	name: 'Admin User',
	email: 'admin@example.com',
	password: 'password'
};

const login = (email: string, password: string) => {
	return cy.session(
		email,
		() => {
			// Make sure to test against us english to have stable tests,
			// regardless on local language preferences
			localStorage.setItem('locale', 'en-US');
			// Visit auth page
			cy.visit('/auth');
			// Fill out the form
			cy.get('input[autocomplete="email"]').type(email);
			cy.get('input[type="password"]').type(password);
			// Submit the form
			cy.get('button[type="submit"]').click();
			// Wait until the user is redirected to the home page
			cy.url().should('not.include', '/auth');

			// Wait for the app to finish loading (splash screen to disappear)
			cy.get('#splash-screen', { timeout: 10000 }).should('not.exist');

			// Handle any modals that might appear after loading
			cy.get('body').then(($body) => {
				// Handle version/changelog dialog
				if ($body.find('button:contains("Okay, Let\'s Go!")').length > 0) {
					cy.get('button').contains("Okay, Let's Go!").click();
				}
				// Handle any other modal dialogs
				if ($body.find('[aria-modal="true"]').length > 0) {
					cy.get('body').type('{esc}');
					// Wait for modal to disappear
					cy.get('[aria-modal="true"]', { timeout: 5000 }).should('not.exist');
				}
			});

			// Wait for the model selector to be available (this indicates the app is ready)
			cy.get('button[aria-label="Select a model"]', { timeout: 15000 }).should('exist');
		},
		{
			validate: () => {
				cy.request({
					method: 'GET',
					url: '/api/v1/auths/',
					headers: {
						Authorization: 'Bearer ' + localStorage.getItem('token')
					}
				});
			}
		}
	);
};

const register = (name: string, email: string, password: string) => {
	return cy
		.request({
			method: 'POST',
			url: '/api/v1/auths/signup',
			body: {
				name: name,
				email: email,
				password: password
			},
			failOnStatusCode: false
		})
		.then((response) => {
			expect(response.status).to.be.oneOf([200, 400, 403]);
		});
};

const registerAdmin = () => {
	return register(adminUser.name, adminUser.email, adminUser.password);
};

const loginAdmin = () => {
	return login(adminUser.email, adminUser.password);
};

Cypress.Commands.add('login', (email, password) => login(email, password));
Cypress.Commands.add('register', (name, email, password) => register(name, email, password));
Cypress.Commands.add('registerAdmin', () => registerAdmin());
Cypress.Commands.add('loginAdmin', () => loginAdmin());

Cypress.Commands.add('dismissWelcomeModal', () => {
	cy.window().then((win) => {
		const version = win.localStorage.getItem('version');
		if (version) {
			cy.log('Version key found in localStorage, skipping modal dismissal');
			return;
		}

		// Wait up to 10s for modal to appear, but don't fail if it doesn't
		// TODO: it seems there's a still a way to fail on [aria-modal="true"] doesn't exist
		cy.get('body').then(($body) => {
			cy.get('[aria-modal="true"]', { timeout: 10000 })
				.should('exist')
				.then(() => {
					// Modal appeared, continue with dismissal logic as before
					cy.log('Modal detected, attempting dismissal...');
					cy.screenshot('chat-modal-discovered');
					if ($body.find('[aria-modal="true"]').length > 0) {
						cy.log('Modal detected, attempting dismissal...');

						// Try to find any dismissal button with common text
						cy.get('body').then(($modalBody) => {
							const dismissButtons = $modalBody.find('button').filter((i, el) => {
								const text = (el.textContent || '').toLowerCase();
								return (
									text.includes('okay') ||
									text.includes('ok') ||
									text.includes('got it') ||
									text.includes('continue') ||
									text.includes('dismiss') ||
									text.includes('close')
								);
							});

							if (dismissButtons.length > 0) {
								cy.log(`Found ${dismissButtons.length} potential dismiss buttons`);
								cy.wrap(dismissButtons.first()).click({ force: true });

								// Wait for modal to be dismissed
								cy.get('[aria-modal="true"]', { timeout: 10000 }).should('not.exist');
								cy.log('Modal successfully dismissed');
							} else {
								cy.log('No dismiss buttons found, trying escape key');
								cy.get('body').type('{esc}');
								// Check if escape worked
								cy.get('body').then(($escapeBody) => {
									if ($escapeBody.find('[aria-modal="true"]').length > 0) {
										cy.log('Escape key failed, modal still present');
									}
								});
							}
						});
					} else {
						cy.log('No modal detected');
					}
				})
				.then({}, () => {
					// Modal did NOT appear in 10s, check localStorage again
					cy.window().then((win2) => {
						const version2 = win2.localStorage.getItem('version');
						if (version2) {
							cy.log('Version key found after waiting, skipping modal dismissal');
							return;
						}
						// Fail if version still not present
						throw new Error(
							'Timed out waiting for modal and "version" key is still missing in localStorage'
						);
					});
				});
		});
	});

	// Final verification - ensure we're in a clean state
	cy.get('[aria-modal="true"]').should('not.exist');
	cy.screenshot('chat-modal-dismissed');
	// Take final screenshot to confirm modal is dismissed
	cy.get('button[aria-label="Select a model"]', { timeout: 15000 }).should('be.visible');
});

Cypress.Commands.overwrite('log', function (log, ...args) {
	const indent = '\t'; // You can adjust the number of tabs or spaces here
	const formattedArgs = args.map((arg) =>
		typeof arg === 'string' ? indent + arg : indent + JSON.stringify(arg)
	);
	if (Cypress.browser.isHeadless) {
		return cy.task('log', formattedArgs, { log: false }).then(() => {
			return log(...args);
		});
	} else {
		console.log(...formattedArgs);
		return log(...args);
	}
});

before(() => {
	cy.registerAdmin();
});
