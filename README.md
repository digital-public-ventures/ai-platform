# DPV AI Platform 👋

**Acknowledgments:** This project was hard forked from Open Webui on April 17th, 2025. See [Open Webui](https://docs.openwebui.com/) for more info.

## Demo

![Open WebUI Demo](./demo.gif)

## System Reqs

Before you begin, ensure your system meets these minimum requirements:

* **Operating System:** Linux (or WSL on Windows), Windows 11, or macOS. *(Recommended for best compatibility)*
* **IDE (Recommended):** We recommend using an IDE like [VS Code](https://code.visualstudio.com/) for code editing, debugging, and integrated terminal access. Feel free to use your favorite IDE if you have one!
* **\[Optional] GitHub Desktop:** For easier management of the Git repository, especially if you are less familiar with command-line Git, consider installing [GitHub Desktop](https://desktop.github.com/).

## Setting Up Your Local Environment

We'll set up both the frontend (user interface) and backend (API and server logic) of DPV AI Platform.

### 1. Clone the Repository

First, use `git clone` to download the DPV AI Platform repository to your local machine. This will create a local copy of the project on your computer.

1. **Open your terminal** (or Git Bash if you're on Windows and using Git Bash).
2. **Navigate to the directory** where you want to store the DPV AI Platform project.
3. **Clone the repository:** Run the following command:

```bash
git clone https://github.com/digital-public-ventures/ai-platform.git
cd ai-platform
```

The `git clone` command downloads the project files from GitHub. The `cd ai-platform` command then navigates you into the newly created project directory.

### 2. Frontend Setup (User Interface)

> [!IMPORTANT]
> **Use Node.js:** Version **22.10 or higher**. *(Required for frontend development)*

1. **Install nvm and use Node.js v22.10 or higher:**

   * For managing Node versions, we recommend [nvm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating). You can install [nvm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating) and tell it to use the Node version specified in this repo's `.nvmrc` like so:

   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
   ```

   * Open a new terminal or run `source ~/.bashrc` (or `source ~/.zshrc` if you use zsh), then:

   ```bash
   nvm install # should automatically install version in .nvmrc, else specify 22.18.0
   nvm use # should automatically use version in .nvmrc, else specify 22.18.0
   ```

2. **Configure Environment Variables:**
   * Copy the example environment file to `.env`:

     ```bash
     cp -RPp .env.example .env
     ```

     This command copies the `.env.example` file to a new file named `.env`. The `.env` file is where you'll configure environment variables for the frontend.

   * **Customize `.env`**: Open the `.env` file in your code editor (like VS Code). This file contains configuration variables for the frontend, such as API endpoints and other settings. For local development, the default settings in `.env.example` are usually sufficient to start with. However, you can customize them if needed.
   
> [!IMPORTANT]
> Do not commit sensitive information to `.env`. Always ensure that `.env` is listed in your `.gitignore` file.

3. **Install Frontend Dependencies:**
   * **Navigate to the frontend directory:** If you're not already in the project root (`ai-platform` directory), ensure you are there.

     ```bash
     # If you are not yet in the project root, run:
     cd ai-platform
     ```

   * Install the required JavaScript packages:

     ```bash
     npm install
     ```

     This will install all frontend dependencies listed in `package.json`.

     *Note: Depending on your DPV AI Platform version, you might see compatibility warnings or errors. If so, just run:*

     ```bash
     npm install --force
     ```

     *Some setups need this to get around version issues.*

4. **Start the Frontend Development Server:**

   * In your terminal, run:

   ```bash
   npm run dev
   ```

   * This command launches the frontend development server. If the steps were followed successfully, it will usually indicate the server is running and provide a local URL.

   🎉 **Access the Frontend:** Open your web browser and go to <http://localhost:5173>. You should see a message indicating that DPV AI Platform's frontend is running and is waiting for the backend to be available. Don't worry about that message yet! Let's set up the backend next. **Keep this terminal running** – it's serving your frontend!

### 2.5: Build the Frontend for Production (Optional but Recommended)

Once you’ve verified that the frontend development server (`npm run dev`) is running correctly and you can see DPV AI Platform at <http://localhost:5173>, it's a **good practice to also build the frontend assets**. This step simulates the production environment and can help catch build-time errors that don't show up during development.

**In the same frontend terminal:**

```bash
npm run build
```

* This command generates an optimized, production-ready build of the frontend and places the static files in the `build` directory.
* If the build completes successfully (without errors), you're ready! If there are errors, address them before proceeding.
* You don't need to do anything more with `build` for local development, but building ensures your code will not break in production or during deployment.

### 3. Backend Setup (API and Server)

> [!IMPORTANT]
> **Python:** Version **3.11 or higher**. *(Required for backend services)*

For managing Python versions, we recommend [uv](https://docs.astral.sh/uv/). You can [install uv](https://docs.astral.sh/uv/getting-started/installation/) and tell it to use Python 3.11 like so:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv --python 3.11
```

This application **requires** you to use separate terminal instances for your frontend and backend processes. This keeps your workflows organized and makes it easier to manage each part of the application independently.

**Using VS Code Integrated Terminals:**

VS Code's integrated terminal feature makes managing multiple terminals easy. Here's how to leverage it for frontend and backend separation:

1. **Frontend Terminal (You likely already have this):** If you followed the Frontend Setup steps, you probably already have a terminal open in VS Code at the project root (`ai-platform` directory). This is where you'll run your frontend commands (`npm run dev`, etc.). Ensure you are in the `ai-platform` directory for the next steps if you are not already.

2. **Backend Terminal (Open a New One):**

   * In VS Code, go to **Terminal > New Terminal** (or use the shortcut `Ctrl+Shift+` on Windows/Linux or `Cmd+Shift+` on macOS). This will open a new integrated terminal panel.
   * **Navigate to the `backend` directory:** In this *new* terminal, use the `cd backend` command to change the directory to the `backend` folder within your project. This ensures all backend-related commands are executed in the correct context.

   Now you have **two separate terminal instances within VS Code**: one for the frontend (likely in the `ai-platform` directory) and one specifically for the backend (inside the `backend` directory). You can easily switch between these terminals within VS Code to manage your frontend and backend processes independently. This setup is highly recommended for a cleaner and more efficient development workflow.

**Backend Setup Steps (in your *backend* terminal):**

1. **Navigate to the Backend Directory:** (You should already be in the `backend` directory in your *new* terminal from the previous step). If not, run:

   ```bash
   cd backend
   ```

2. **Create and Activate a uv Virtual Environment (Recommended):**

   * We highly recommend using [Astral’s uv](https://docs.astral.sh/uv/) to manage Python dependencies and isolate your project environment. It is significantly faster than Conda or pip, handles both virtual environments and dependency resolution, and ensures you have the correct Python version and libraries.

     ```bash
     uv venv --python 3.11 .venv
     source .venv/bin/activate
     ```

     * `uv venv --python 3.11 .venv`: This command creates a new virtual environment named `.venv` using Python version 3.11. If you chose a different Python 3.11.x version, that’s fine.
     * `source .venv/bin/activate`: This command activates the newly created uv environment. Once activated, your terminal prompt will usually change to indicate you are in the `.venv` environment (e.g., it might show `(.venv)` at the beginning of the line).

   **Make sure you activate the environment in your backend terminal before proceeding.**

   *(Using uv is optional but strongly recommended for managing Python dependencies and avoiding conflicts.)* If you choose not to use uv, ensure you are using Python 3.11 or higher and proceed to the next step, but be aware of potential dependency conflicts.

3. **Install Backend Dependencies:**

   * In your *backend* terminal (and with the uv environment activated if you are using uv), run:

   ```bash
   uv pip install -r requirements.txt -U
   ```

   This command uses uv's accelerated version of `pip` (Python Package Installer) to read the `requirements.txt` file in the `backend` directory. `requirements.txt` lists all the Python libraries that the backend needs to run. `pip install` downloads and installs these libraries into your active Python environment (your uv environment if you are using it, or your system-wide Python environment otherwise). The `-U` flag ensures you get the latest compatible versions of the libraries.

4. **Make an AI model available to your backend:** In order to chat with a model immediately, you can either provide an `OPENAI_API_KEY` environment variable in your `.env` file or [download and run Ollama](https://ollama.com/download).

   To use Ollama, [download and install Ollama](https://ollama.com/download), then open a terminal and run:

   ```sh
   ollama run gemma
   ```

   This will download and install the [Gemma](https://deepmind.google/models/gemma/) open source model by Google, which will run on most laptops.

   To use OpenAI or Azure OpenAI, you can add the following to your `.env` file:

   ```env
   OPENAI_API_KEY='your_openai_api_key_here'
   OPENAI_API_BASE_URL='https://api.openai.com/v1' # or your Azure OpenAI endpoint
   ```

   If using Azure OpenAI, your base URL should look like: `https://my-resource-name.openai.azure.com/openai/v1`. To work out of the box, you must use default deployment names, like `gpt-4.1`, `gpt-5-mini-2025-08-07`. [See expected names here](./azure_deployment_names.md).

> [!NOTE]
> When using an Azure base url, the models dropdown will show all models, but **only the models you have created deployments for will work**. You can turn off the other models by clicking your profile icon > admin panel > settings > models.

5. **Start the Backend Development Server:**

   * In your *backend* terminal, run:

   ```bash
   bash dev.sh
   ```

   This command executes the `dev.sh` script. This script contains the command to start the backend development server. *(You can open and examine the `dev.sh` file in your code editor to see the exact command being run if you are curious.)* The backend server will usually start and print some output to the terminal.

   📄 **Explore the API Documentation:** Once the backend is running, you can access the automatically generated API documentation in your web browser at <http://localhost:8080/docs>. This documentation is incredibly valuable for understanding the backend API endpoints, how to interact with the backend, and what data it expects and returns. Keep this documentation handy as you develop!

6. **Start the Backend Production Server:** *(Skip for local development)*

   * Ensure that your dev server or any other processes listening on `8080` are stopped (see `Port Conflicts` below), then in your *backend* terminal, run:

   ```bash
   bash start.sh
   ```

   This command executes the `start.sh` script. This script contains the command to start the backend production server. *(You can open and examine the `backend/start.sh` file in your code editor to see the exact commands being run if you are curious.)* The backend server will start and print some output to the terminal.

🎉 **Congratulations!** If you have followed all the steps, you should now have both the frontend and backend development servers running locally. Go back to your browser tab where you accessed the frontend (usually <http://localhost:5173>). **Refresh the page.** You should now see the full DPV AI Platform application running in your browser, connected to your local backend!

## Next Steps

To set up postgres and redis locally, see the [Local Postgres and Redis Setup Guide](./local_postgres_redis_setup.md).

For help with common issues, see the [Troubleshooting Guide](./TROUBLESHOOTING.md).
