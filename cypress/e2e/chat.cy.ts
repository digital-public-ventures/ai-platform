// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../support/index.d.ts" />

// These tests run through the chat flow.
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
		// Wait for page to load
		cy.get('body').should('be.visible');

		cy.screenshot('chat-body-is-visible');

		cy.dismissWelcomeModal();
	});

	context('Ollama', () => {
		it('can see ollama models in dropdown', () => {
			// Take screenshot of clean state (modal should already be dismissed by beforeEach)
			cy.screenshot('chat-ollama-clean-state-no-modal');

			// Click model selector
			cy.get('button[aria-label="Select a model"]').should('be.visible').click();

			// Take screenshot after clicking model selector
			cy.screenshot('05-model-selector-clicked');

			// Wait for dropdown to appear and contain model items
			cy.get('button[aria-roledescription="model-item"]', { timeout: 10000 }).should('exist');
			cy.get('body').then(($body) => {
				const allButtons = $body.find('button');
				const modelButtons = $body.find('button[aria-roledescription="model-item"]');
				const menuItems = $body.find('[role="menuitem"]');

				cy.log(`Total buttons: ${allButtons.length}`);
				cy.log(`Model item buttons: ${modelButtons.length}`);
				cy.log(`Menu items: ${menuItems.length}`);

				// Look for text content that matches known Ollama models
				const ollamaModels = ['qwen', 'deepseek', 'coder'];
				ollamaModels.forEach((modelName) => {
					const matchingButtons = $body.find(`button:contains("${modelName}")`);
					cy.log(`Buttons containing "${modelName}": ${matchingButtons.length}`);
					if (matchingButtons.length > 0) {
						matchingButtons.each((i, el) => {
							cy.log(`  ${modelName} button ${i}: "${el.textContent}"`);
						});
					}
				});
			});

			// Take final screenshot
			cy.screenshot('06-model-dropdown-analysis');
		});

		it('user can perform text chat', () => {
			// Take screenshot at start (modal should already be dismissed by beforeEach)
			cy.screenshot('chat-01-test-start');

			// Take screenshot showing app ready state
			cy.screenshot('chat-02-app-loaded');

			// Click on the model selector
			cy.get('button[aria-label="Select a model"]').click();
			cy.screenshot('chat-05-model-dropdown-opened');

			// Select the first model
			cy.get('button[aria-roledescription="model-item"]').first().click();
			cy.screenshot('chat-06-model-selected');

			// Type a message
			cy.get('#chat-input')
				.should('exist')
				.focus()
				.type('Hi, what can you do? A single sentence only please.', {
					force: true,
					parseSpecialCharSequences: false
				});
			cy.screenshot('chat-07-message-typed');

			// Wait for submit button to appear (only shows when typing)
			cy.get('button[type="submit"]').should('be.visible');
			cy.screenshot('chat-08-submit-button-visible');

			// Send the message
			cy.get('button[type="submit"]').click();
			cy.screenshot('chat-09-message-sent');

			// User's message should be visible
			cy.get('.chat-user').should('exist');
			// Wait for the response
			// .chat-assistant is created after the first token is received
			cy.get('.chat-assistant', { timeout: 10_000 }).should('exist');
			// Generation Info is created after the stop token is received
			cy.get('button[aria-label="Good Response"]', { timeout: 120_000 }).should('exist');
		});

		it('user can share chat', () => {
			// Modal should already be dismissed by beforeEach, proceed directly to test

			// Click on the model selector
			cy.get('button[aria-label="Select a model"]').click();
			// Select the first model
			cy.get('button[aria-roledescription="model-item"]').first().click();
			// Type a message
			cy.get('#chat-input')
				.should('exist')
				.focus()
				.type('Hi, what can you do? A single sentence only please.', {
					force: true,
					parseSpecialCharSequences: false
				});
			// Wait for submit button to appear (only shows when typing)
			cy.get('button[type="submit"]').should('be.visible');
			// Send the message
			cy.get('button[type="submit"]').click();
			// User's message should be visible
			cy.get('.chat-user').should('exist');
			// Wait for the response
			// .chat-assistant is created after the first token is received
			cy.get('.chat-assistant', { timeout: 10_000 }).should('exist');
			// Generation Info is created after the stop token is received
			cy.get('button[aria-label="Good Response"]', { timeout: 120_000 }).should('exist');
			// spy on requests
			const spy = cy.spy();
			cy.intercept('POST', '/api/v1/chats/**/share', spy);
			// Open context menu
			cy.get('#chat-context-menu-button').click();
			// Click share button
			cy.get('#chat-share-button').click();
			// Check if the share dialog is visible
			cy.get('#copy-and-share-chat-button').should('exist');
			// Click the copy button
			cy.get('#copy-and-share-chat-button').click();
			cy.wrap({}, { timeout: 5_000 }).should(() => {
				// Check if the share request was made
				expect(spy).to.be.callCount(1);
			});
		});

		// it('user can generate image', () => {
		// 	// Ironclad modal dismissal at test start
		// 	cy.get('body').then($body => {
		// 		const okayButton = $body.find('button').filter((i, el) => {
		// 			const text = el.textContent || '';
		// 			return /okay/i.test(text);
		// 		});
		// 		if (okayButton.length > 0) {
		// 			cy.wrap(okayButton.first()).click({ force: true });
		// 		}
		// 	});
	});
});
