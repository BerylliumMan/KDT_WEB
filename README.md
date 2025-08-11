# UI Test Automation Platform

This is a web-based UI automation testing platform built with FastAPI and Playwright. It allows users to manage projects, modules, and test cases, and to execute automated UI tests in a keyword-driven manner.

## Features

*   **Web-based interface:** Manage test cases and view reports through a user-friendly web UI with Vue.js frontend.
*   **Keyword-driven testing:** Test steps are defined by simple keywords, making test case creation accessible to non-programmers.
*   **Project and module management:** Organize test cases into projects and modules for better organization.
*   **Test execution and reporting:** Run test cases and view detailed logs and reports, including screenshots of failed steps.
*   **RESTful API:** A comprehensive API for programmatic interaction with the platform.
*   **Multi-language support:** Supports both English and Chinese interfaces.
*   **Browser selection:** Choose between Chromium, Firefox, or WebKit for test execution.
*   **Headless mode:** Option to run tests in headless mode for faster execution.
*   **Rich UI components:** Modern, responsive interface with animations and interactive elements.
*   **Agent-based distributed testing:** Run tests on remote machines through agent connections.

## Technology Stack

*   **Backend:** FastAPI
*   **Browser Automation:** Playwright
*   **Database:** MySQL
*   **Frontend:** Vue.js, HTML, CSS with Remix Icons

## Project Structure

```
uitest/
├── app/
│   ├── __init__.py
│   ├── crud.py             # Database CRUD operations
│   ├── database.py         # Database connection and session management
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # SQLAlchemy database models
│   ├── routers/            # API routers for different modules
│   │   ├── __init__.py
│   │   ├── project_router.py
│   │   ├── module_router.py
│   │   └── testcase_router.py
│   ├── static/             # Static files (CSS, JS, Icons)
│   │   ├── js/             # JavaScript libraries and custom scripts
│   │   │   └── vue.global.prod.js  # Vue.js library
│   │   ├── locales/        # Localization files
│   │   │   ├── en.json     # English translations
│   │   │   └── zh.json     # Chinese translations
│   │   └── style.css       # Main stylesheet
│   └── templates/          # HTML templates
│       └── index.html      # Main application page
├── core/
│   ├── __init__.py
│   ├── keyword_engine.py   # Logic for interpreting and executing keywords
│   ├── playwright_manager.py # Manages Playwright browser instances
│   └── runner.py           # Test case execution engine
├── agent/                  # Agent system for distributed testing
│   ├── __init__.py
│   ├── client.py           # Client agent implementation
│   ├── manager.py          # Agent manager on server side
│   ├── models.py           # Data models for agent communication
│   └── router.py           # API routes for agent management
├── logs/                   # Execution logs
├── reports/                # Test reports, including screenshots and trace files
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
├── run_tests.py            # Script to run tests from the command line
└── schema.sql              # SQL schema for database initialization
```

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd uitest
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This project uses MySQL. You may need to install `mysqlclient` or another appropriate MySQL driver.*

4.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

5.  **(Optional) Install specific browser dependencies:**
    ```bash
    playwright install-deps
    ```
    This command installs additional dependencies needed for Playwright to run browsers properly on your system.

## Database Initialization

1.  **Set up a MySQL server:** Ensure you have a running MySQL server instance.

2.  **Create a database:** Create a new database for the application.
    ```sql
    CREATE DATABASE ui_test;
    ```

3.  **Configure the connection:** Update the database connection string in `config.py` with your MySQL server details (host, port, username, password, database name).
    ```python
    # Example configuration in config.py
    DB_HOST = '127.0.0.1'  # or your MySQL server IP address
    DB_PORT = 3306
    DB_USER = 'your_username'  # Replace with your MySQL username
    DB_PASSWORD = 'your_password' # Replace with your MySQL password
    DB_NAME = 'ui_test' # Replace with your database name
    ```

4.  **Initialize the schema:** Import the `schema.sql` file to create the necessary tables in your database.
    ```bash
    mysql -u your_username -p ui_test < schema.sql
    ```

5.  **Verify the setup:** You can verify that the tables were created correctly by connecting to your database and running:
    ```sql
    USE ui_test;
    SHOW TABLES;
    ```
    You should see tables for `projects`, `modules`, and `test_cases`.

## Running the Application

To start the FastAPI server, run the following command from the project root:

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### Alternative ways to run the application:

1.  **Using the built-in start function:**
    ```bash
    python -m app.main
    ```

2.  **Running with custom host and port:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
    This allows external connections to your server.

3.  **Running in production mode (without reload):**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    ```
    This starts the server with 4 worker processes for better performance.

## Agent-based Distributed Testing

This platform supports running tests on remote machines through agent connections. This allows you to execute tests on different environments or machines without installing the full platform on each.

### Running an Agent

To run an agent on a remote machine:

1.  Clone the repository to the remote machine
2.  Install dependencies as described in the Installation section
3.  Run the agent client:
    ```bash
    python agent_client.py --server http://<server-ip>:<port> --name <agent-name>
    ```

For example:
    ```bash
    python agent_client.py --server http://192.168.1.100:8000 --name "Windows-Test-Agent"
    ```

### Using Agents in the Web Interface

Once agents are connected to the server:

1.  Navigate to the web interface
2.  Select a test case to run
3.  Click the "Run" button, which will now show a dropdown menu
4.  Choose "Run on Server" to run the test locally on the server
5.  Or choose "Run on [Agent Name]" to execute the test on a connected agent

### Agent Features

- Real-time status updates (online/offline/busy)
- Heartbeat mechanism to detect disconnected agents
- Support for running test cases, modules, and projects
- Detailed execution logs sent back to the server

## API Endpoints

The application provides several API endpoints for managing projects, modules, and test cases. You can explore the interactive API documentation (provided by Swagger UI) at `http://127.0.0.1:8000/docs`.

### Main API Endpoints:

- **Projects:**
  - `GET /api/projects/` - List all projects
  - `POST /api/projects/` - Create a new project
  - `GET /api/projects/{project_id}` - Get a specific project
  - `PUT /api/projects/{project_id}` - Update a specific project
  - `DELETE /api/projects/{project_id}` - Delete a specific project

- **Modules:**
  - `GET /api/projects/{project_id}/modules/` - List all modules for a project
  - `POST /api/projects/{project_id}/modules/` - Create a new module in a project
  - `GET /api/modules/{module_id}` - Get a specific module
  - `PUT /api/modules/{module_id}` - Update a specific module
  - `DELETE /api/modules/{module_id}` - Delete a specific module

- **Test Cases:**
  - `GET /api/testcases/` - List all test cases
  - `POST /api/testcases/` - Create a new test case
  - `GET /api/testcases/{testcase_id}` - Get a specific test case
  - `PUT /api/testcases/{testcase_id}` - Update a specific test case
  - `DELETE /api/testcases/{testcase_id}` - Delete a specific test case
  - `POST /api/testcases/{testcase_id}/run` - Run a specific test case
  - `GET /api/testcases/module/{module_id}/testcases` - List all test cases in a module (with pagination)
  - `POST /api/testcases/module/{module_id}/run` - Run all test cases in a module
  - `POST /api/testcases/project/{project_id}/run` - Run all test cases in a project

- **Agents:**
  - `POST /api/agents/register` - Register a new agent
  - `POST /api/agents/{agent_id}/unregister` - Unregister an agent
  - `GET /api/agents/` - List all registered agents
  - `GET /api/agents/{agent_id}` - Get information about a specific agent
  - `POST /api/agents/{agent_id}/command` - Send a command to a specific agent
  - `GET /api/agents/{agent_id}/commands` - Get pending commands for an agent
  - `POST /api/agents/{agent_id}/run/testcase/{case_id}` - Run a specific test case on a remote agent
  - `GET /api/agents/available` - List all available agents

- **Keywords:**
  - `GET /api/keywords` - Get a list of all supported keywords for test steps

### Health Check:

- `GET /health` - Check if the application is running properly

## How to Run Tests

Tests can be executed through the web interface or by running the `run_tests.py` script from the command line.

### Running tests through the web interface:

1. Start the application server
2. Navigate to `http://127.0.0.1:8000` in your browser
3. Select a project and module
4. Click the "Run" button next to a test case, module, or project
5. For remote execution, use the dropdown menu to select an agent

### Running tests from the command line:

To run a specific test case from the command line:

```bash
python run_tests.py --testcase_id <your_testcase_id>
```

To run all test cases in a module:

```bash
python run_tests.py --module_id <your_module_id>
```

To run all test cases in a project:

```bash
python run_tests.py --project_id <your_project_id>
```

To see all available command-line options:

```bash
python run_tests.py --help
```

### Test execution features:

- Tests run in the browser specified in the project settings (Chromium, Firefox, or WebKit)
- Option to run tests in headless mode for faster execution
- Detailed logging of test execution
- Screenshots captured on test failures
- Trace files generated for debugging failed tests

## Logs and Reports

After each test run, the following are generated:

*   **Log files:** Detailed execution logs are stored in the `logs/` directory. Each test run creates a new log file with detailed information about each step execution.

*   **Reports:** A summary of the test run, including screenshots of any failed steps, is saved in the `reports/` directory. Each test run creates a new subdirectory named with the test case ID and a timestamp.

*   **Screenshots:** Failed test steps automatically capture screenshots which are saved in the `reports/<run_id>/screenshots/` directory.

*   **Trace files:** Playwright trace files (trace.zip) are generated for each test run and saved in the `reports/<run_id>/` directory. These files can be used for debugging and can be viewed using the Playwright Trace Viewer.

### Accessing Reports:

1.  **Through the file system:** Navigate to the `reports/` directory to view all reports.

2.  **Using Playwright Trace Viewer:** To view trace files for debugging:
    ```bash
    playwright show-trace reports/<run_id>/trace.zip
    ```

### Log File Format:

Log files contain timestamped entries for each test step, including:
- Step execution status (passed/failed)
- Error messages for failed steps
- Execution time for each step
- Screenshot references for failed steps

## Contribution

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.