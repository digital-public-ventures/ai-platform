## Troubleshooting Common Issues

Here are solutions to some common problems you might encounter during setup or development:

### 💥 "FATAL ERROR: Reached Heap Limit" (Frontend)

This error, often seen during frontend development, indicates that Node.js is running out of memory during the build process, especially when working with large frontend applications.

**Solution:** Increase the Node.js heap size. This gives Node.js more memory to work with. You have a couple of options:

1. **Using `NODE_OPTIONS` Environment Variable (Recommended for Development):**
   * This is a temporary way to increase the memory limit for the current terminal session. Before running `npm run dev` or `npm run build` in your *frontend* terminal, set the `NODE_OPTIONS` environment variable:

     ```bash
     export NODE_OPTIONS="--max-old-space-size=4096" # For Linux/macOS (bash, zsh)
     # set NODE_OPTIONS=--max-old-space-size=4096 # For Windows (Command Prompt)
     # $env:NODE_OPTIONS="--max-old-space-size=4096" # For Windows (PowerShell)
     npm run dev
     ```

     Choose the command appropriate for your operating system and terminal. `4096` represents 4GB of memory. You can try increasing this value further if needed (e.g., `8192` for 8GB). This setting will only apply to commands run in the current terminal session.

2. **Modifying `Dockerfile` (For Dockerized Environments):**
   * If you are working with Docker, you can permanently set the `NODE_OPTIONS` environment variable within your `Dockerfile`. This is useful for consistent memory allocation in Dockerized environments, as shown in the original guide example:

     ```dockerfile
     ENV NODE_OPTIONS=--max-old-space-size=4096
     ```

   * **Allocate Sufficient RAM:** Regardless of the method, ensure your system or Docker container has enough RAM available for Node.js to use. **At least 4 GB of RAM is recommended**, and more might be needed for larger projects or complex builds. Close unnecessary applications to free up RAM.

### ⚠️ Port Conflicts (Frontend & Backend)

If you see errors related to ports, such as "Address already in use" or "Port already bound," it means another application on your system is already using port `5173` (default for frontend) or `8080` (default for backend). Only one application can use a specific port at a time.

**Solution:**

1. **Identify the Conflicting Process:** You need to find out which application is using the port you need.
   * **Linux/macOS:** Open a new terminal and use the `lsof` or `netstat` commands:
     * `lsof -i :5173` (or `:8080` for the backend port)
     * `netstat -tulnp | grep 5173` (or `8080`)
       These commands will list the process ID (PID) and the name of the process using the specified port.
   * **Windows:** Open Command Prompt or PowerShell as an administrator and use `netstat` or `Get-NetTCPConnection`:
     * `netstat -ano | findstr :5173` (or `:8080`) (Command Prompt)
     * `Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess` (PowerShell)
       These commands will also show the PID of the process using the port.

2. **Terminate the Conflicting Process:** Once you identify the process ID (PID), you can stop the application using that port. **Be careful when terminating processes, especially if you are unsure what they are.**
   * **Linux/macOS:** Use the `kill` command: `kill <PID>` (replace `<PID>` with the actual process ID). If the process doesn't terminate with `kill`, you can use `kill -9 <PID>` (force kill), but use this with caution.
   * **Windows:** Use the `taskkill` command in Command Prompt or PowerShell as administrator: `taskkill /PID <PID> /F` (replace `<PID>` with the process ID). The `/F` flag forces termination.

3. **Alternatively, Change Ports (Advanced):**
   * If you cannot terminate the conflicting process (e.g., it's a system service you need), you can configure DPV AI Platform to use different ports for the frontend and/or backend. This usually involves modifying configuration files.
     * **Frontend Port:** Check the frontend documentation or configuration files (often in `vite.config.js` or similar) for how to change the development server port. You might need to adjust the `.env` file as well if the frontend uses environment variables for the port.
     * **Backend Port:** Examine the `dev.sh` script or backend configuration files to see how the backend port is set. You might need to modify the startup command or a configuration file to change the backend port. If you change the backend port, you'll likely need to update the frontend's `.env` file to point to the new backend URL.

### 🔄 Hot Reload Not Working

Hot reload (or hot module replacement - HMR) is a fantastic development feature that automatically refreshes your browser when you make changes to the code. If it's not working, it can significantly slow down your development workflow.

**Troubleshooting Steps:**

1. **Verify Development Servers are Running:** Double-check that both `npm run dev` (frontend) and `sh dev.sh` (backend) are running in their respective terminals and haven't encountered any errors. Look for messages in the terminal output indicating they are running and in "watch mode" or "development mode." If there are errors, address them first.
2. **Check for Watch Mode/HMR Messages:** When the development servers start, they should usually print messages in the terminal indicating that hot reload or watch mode is enabled. Look for phrases like "HMR enabled," "watching for file changes," or similar. If you don't see these messages, there might be a configuration issue.
3. **Browser Cache:** Sometimes, your browser's cache can prevent you from seeing the latest changes, even if hot reload is working. Try a **hard refresh** in your browser:
   * **Windows/Linux:** Ctrl+Shift+R
   * **macOS:** Cmd+Shift+R
   * Alternatively, you can try clearing your browser cache or opening the frontend in a private/incognito browser window.
4. **Dependency Issues (Frontend):** Outdated or corrupted frontend dependencies can sometimes interfere with hot reloading. Try refreshing your frontend dependencies:
   * In your *frontend* terminal, run:

     ```bash
     rm -rf node_modules && npm install
     ```

     This command deletes the `node_modules` directory (where dependencies are stored) and then reinstalls them from scratch. This can resolve issues caused by corrupted or outdated packages.
5. **Backend Restart Required (For Backend Changes):** Hot reload typically works best for frontend code changes (UI, styling, components). For significant backend code changes (especially changes to server logic, API endpoints, or dependencies), you might need to **manually restart the backend server** (by stopping `sh dev.sh` in your backend terminal and running it again). Hot reload for backend changes is often less reliable or not automatically configured in many backend development setups.
6. **IDE/Editor Issues:** In rare cases, issues with your IDE or code editor might prevent file changes from being properly detected by the development servers. Try restarting your IDE or ensuring that files are being saved correctly.
7. **Configuration Problems (Advanced):** If none of the above steps work, there might be a more complex configuration issue with the frontend or backend development server setup. Consult the project's documentation, configuration files (e.g., `vite.config.js` for frontend, backend server configuration files).

### Offline Mode

If you are running DPV AI Platform in an offline environment, you can set the `HF_HUB_OFFLINE` environment variable to `1` to prevent attempts to download models from the internet.

```bash
export HF_HUB_OFFLINE=1
```
