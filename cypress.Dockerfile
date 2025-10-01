# Use the latest Node LTS and Cypress browsers
FROM cypress/browsers:node-22.14.0-chrome-133.0.6943.126-1-ff-135.0.1-edge-133.0.3065.82-1

# Install global packages as root first
RUN npm install -g ts-node typescript

# Create a non-root user for better security
RUN addgroup --system cypress && adduser --system --ingroup cypress cypress

# Set a working directory and change ownership
WORKDIR /e2e
RUN chown -R cypress:cypress /e2e

# Switch to cypress user
USER cypress

# Set npm cache directory for the cypress user
ENV npm_config_cache=/e2e/.npm-cache
ENV HOME=/e2e

# 1. Copy package files first for better caching
COPY --chown=cypress:cypress package.json package-lock.json ./

# 2. Install dependencies + Cypress
RUN npm ci && npx cypress install

# 3. Copy in only the files you need for tests
COPY --chown=cypress:cypress cypress/ ./cypress/
COPY --chown=cypress:cypress cypress/cypress.config.js ./cypress.config.cjs
COPY --chown=cypress:cypress cypress/tsconfig.json ./tsconfig.json

# 4. Verify Cypress is installed properly (catches environment issues ASAP)
RUN npx cypress verify

# 5. Default command to run tests
CMD ["npx", "cypress", "run"]