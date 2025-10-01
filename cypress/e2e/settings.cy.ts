// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />
import { adminUser } from '../support/e2e';

// These tests run through the various settings pages, ensuring that the user can interact with them as expected
describe('Settings', () => {
	// Wait for 2 seconds after all tests to fix an issue with Cypress's video recording missing the last few frames
	after(() => {
		// eslint-disable-next-line cypress/no-unnecessary-waiting
		cy.wait(2000);
	});

	beforeEach(() => {
		// Login as the admin user
		cy.loginAdmin();
		// Visit the home page
		cy.visit('/');
		// Dismiss any welcome modals
		cy.dismissWelcomeModal();
		// Write all visible aria-labels to log file
		cy.get('body').then(($body) => {
			const ariaLabels = [];
			$body.find('[aria-label]').each((i, el) => {
				ariaLabels.push(el.getAttribute('aria-label'));
			});
			cy.log('Visible aria-labels:', ariaLabels);
		});
		cy.screenshot('settings-before-user-menu-click');
		// Click on the user menu
		cy.get('button', { timeout: 15000 })
			.filter((_, btn) => {
				function getAllTextRecursively(element: Element): string {
					let text = '';
					for (const child of Array.from(element.children)) {
						text += (child as HTMLElement).innerHTML.toLowerCase();
						text += getAllTextRecursively(child);
					}
					return text;
				}
				const allText = getAllTextRecursively(btn);
				return allText.includes('user') && allText.includes('menu');
			})
			.first()
			.click();
		cy.screenshot('settings-after-user-menu-click');
		// Click on the settings link
		cy.get('[role="menuitem"]')
			.filter((_, el) => {
				return Array.from(el.children).some((child) =>
					child.innerHTML.toLowerCase().includes('settings')
				);
			})
			.first()
			.click();
		cy.screenshot('settings-after-user-menu-settings-click');
	});

	context('General', () => {
		it('user can open the General modal and hit save', () => {
			cy.get('button').contains('General').click();
			cy.screenshot('settings-after-user-menu-settings-general-click');
			cy.get('button').contains('Save').click();
		});
	});

	context('Interface', () => {
		it('user can open the Interface modal and hit save', () => {
			cy.get('button').contains('Interface').click();
			cy.screenshot('settings-after-user-menu-settings-interface-click');
			cy.get('button').contains('Save').click();
		});
	});

	context('Audio', () => {
		it('user can open the Audio modal and hit save', () => {
			cy.get('button').contains('Audio').click();
			cy.screenshot('settings-after-user-menu-settings-audio-click');
			cy.get('button').contains('Save').click();
		});
	});

	context('Chats', () => {
		it('user can open the Chats modal', () => {
			cy.get('button').contains('Chats').click();
			cy.screenshot('settings-after-user-menu-settings-chats-click');
		});
	});

	context('Account', () => {
		it('user can open the Account modal and hit save', () => {
			cy.get('button').contains('Account').click();
			cy.screenshot('settings-after-user-menu-settings-account-click');
			cy.get('button').contains('Save').click();
		});
	});

	context('About', () => {
		it('user can open the About modal', () => {
			cy.get('button').contains('About').click();
			cy.screenshot('settings-after-user-menu-settings-about-click');
		});
	});
});
