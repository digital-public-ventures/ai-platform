// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />
import { adminUser } from '../support/e2e';

// These tests assume the following defaults:
// 1. No users exist in the database or that the test admin user is an admin
// 2. Language is set to English
// 3. The default role for new users is 'pending'
describe('Registration and Login', () => {
	// Wait for 2 seconds after all tests to fix an issue with Cypress's video recording missing the last few frames
	after(() => {
		// eslint-disable-next-line cypress/no-unnecessary-waiting
		cy.wait(2000);
	});

	beforeEach(() => {
		cy.visit('/');
	});

	it('can login with the admin user', () => {
		// Fill out the form
		cy.get('input[autocomplete="email"]').type(adminUser.email);
		cy.get('input[type="password"]').type(adminUser.password);
		// Submit the form
		cy.get('button[type="submit"]').click();
		// Wait until we're no longer on the auth page
		cy.url().should('not.include', '/auth');
		// Check that we have a token (indicating successful login)
		cy.window().its('localStorage').invoke('getItem', 'token').should('exist');
		// For admin users, we should be able to access the main chat interface
		// Look for any chat-related elements or navigation
		cy.get('body').should('be.visible');
		// Wait for workspace link to exist (admin-only element)
		cy.get('a[href="/workspace"]').should('exist');
	});

	it('can change enable signup config state', () => {
		// Login as the admin user
		cy.loginAdmin();
		// Visit the home page
		cy.visit('/');
		// Wait for page to load
		cy.get('body').should('be.visible');
		// Wait for user menu to appear
		cy.get('button:has(img[src="/user.png"])').should('exist');
		// Dismiss the welcome modal if it appears
		cy.dismissWelcomeModal();
		// Wait for user menu to appear
		cy.get('button:has(img[src="/user.png"])').should('be.visible');

		cy.get('button:has(img[src="/user.png"])').first().click();
		cy.screenshot('01-after-user-button-click');

		cy.get('a[href="/admin"]', { timeout: 10000 }).click();
		cy.screenshot('02-after-admin-link-click');

		cy.get('a[href="/admin/settings"]').click();
		cy.screenshot('03-after-admin-settings-link-click');

		cy.get('div')
			.contains('Enable New Sign Ups')
			.parent()
			.within(() => {
				cy.get('button')
					.first()
					.then(($btn) => {
						if ($btn.attr('data-state') === 'unchecked') {
							cy.wrap($btn).click();
						}
					});
			});
		cy.screenshot('04-after-enable-signups-toggle');

		cy.get('button[type="submit"]').click();
		cy.screenshot('05-after-submit-click');
	});

	it('should register a new user as pending', () => {
		const userName = `Test User - ${Date.now()}`;
		const userEmail = `cypress-${Date.now()}@example.com`;

		// Toggle from sign in to sign up
		cy.contains('Sign up').click();

		// Fill out the form
		cy.get('input[autocomplete="name"]').type(userName);
		cy.get('input[autocomplete="email"]').type(userEmail);
		cy.get('input[type="password"]').type('password');
		// Submit the form
		cy.get('button[type="submit"]').click();
		// Wait until we're no longer on the auth page
		cy.url().should('not.include', '/auth');
		// Check that we have a token (indicating successful registration/login)
		cy.window().its('localStorage').invoke('getItem', 'token').should('exist');
		// For pending users, we might see "Check Again" or similar pending status
		cy.get('body').then(($body) => {
			const text = $body.text();
			expect(text).to.satisfy(
				(str: string) =>
					str.includes('Check Again') || str.includes('pending') || str.includes('Pending')
			);
		});
	});
});
