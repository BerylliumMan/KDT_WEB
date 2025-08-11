# UI 自动化测试平台

这是一个基于 Web 的 UI 自动化测试平台，使用 FastAPI 和 Playwright 构建。它允许用户管理项目、模块和测试用例，并以关键字驱动的模式执行自动化的 UI 测试。

## 功能特性

*   **Web 操作界面:** 通过用户友好的 Web UI 管理测试用例并查看报告，前端采用 Vue.js 构建。
*   **关键字驱动测试:** 测试步骤由简单的关键字定义，使非程序员也能轻松创建测试用例。
*   **项目和模块管理:** 将测试用例组织到项目和模块中，便于更好地管理。
*   **测试执行和报告:** 运行测试用例并查看详细的日志和报告，包括失败步骤的屏幕截图。
*   **RESTful API:** 提供全面的 API，用于通过编程方式与平台进行交互。
*   **多语言支持:** 支持英文和中文界面。
*   **浏览器选择:** 可选择 Chromium、Firefox 或 WebKit 进行测试执行。
*   **无头模式:** 可选择无头模式运行测试以提高执行速度。
*   **丰富的UI组件:** 现代化、响应式的界面，带有动画和交互元素。

## 技术栈

*   **后端:** FastAPI
*   **浏览器自动化:** Playwright
*   **数据库:** MySQL
*   **前端:** Vue.js, HTML, CSS (使用 Remix Icons)
*   **模板引擎:** Jinja2

## 项目结构

```
uitest/
├── app/
│   ├── __init__.py
│   ├── crud.py             # 数据库 CRUD 操作
│   ├── database.py         # 数据库连接和会话管理
│   ├── main.py             # FastAPI 应用程序入口
│   ├── models.py           # SQLAlchemy 数据库模型
│   ├── routers/            # 不同模块的 API 路由
│   │   ├── __init__.py
│   │   ├── project_router.py
│   │   ├── module_router.py
│   │   └── testcase_router.py
│   ├── static/             # 静态文件 (CSS, JS, 图标)
│   │   ├── js/             # JavaScript 库和自定义脚本
│   │   │   └── vue.global.prod.js  # Vue.js 库
│   │   ├── locales/        # 本地化文件
│   │   │   ├── en.json     # 英文翻译
│   │   │   └── zh.json     # 中文翻译
│   │   └── style.css       # 主样式表
│   └── templates/          # HTML 模板
│       └── index.html      # 主应用程序页面
├── core/
│   ├── __init__.py
│   ├── keyword_engine.py   # 用于解释和执行关键字的逻辑
│   ├── playwright_manager.py # 管理 Playwright 浏览器实例
│   └── runner.py           # 测试用例执行引擎
├── logs/                   # 执行日志
├── reports/                # 测试报告，包括屏幕截图和跟踪文件
├── config.py               # 应用程序配置
├── requirements.txt        # Python 依赖项
├── run_tests.py            # 用于从命令行运行测试的脚本
└── schema.sql              # 用于数据库初始化的 SQL 模式
```

## 安装与设置

1.  **克隆仓库:**
    ```bash
    git clone <repository-url>
    cd uitest
    ```

2.  **创建并激活虚拟环境:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上, 使用 `venv\Scripts\activate`
    ```

3.  **安装所需依赖:**
    ```bash
    pip install -r requirements.txt
    ```
    *注意: 本项目使用 MySQL。您可能需要安装 `mysqlclient` 或其他合适的 MySQL 驱动程序。*

4.  **安装 Playwright 浏览器驱动:**
    ```bash
    playwright install
    ```

5.  **(可选) 安装特定浏览器依赖:**
    ```bash
    playwright install-deps
    ```
    此命令安装 Playwright 在您的系统上正确运行浏览器所需的额外依赖项。

## 数据库初始化

1.  **设置 MySQL 服务器:** 确保您有一个正在运行的 MySQL 服务器实例。

2.  **创建数据库:** 为应用程序创建一个新的数据库。
    ```sql
    CREATE DATABASE ui_test;
    ```

3.  **配置连接:** 在 `config.py` 文件中更新数据库连接字符串，填入您的 MySQL 服务器详细信息（主机、端口、用户名、密码、数据库名）。
    ```python
    # config.py 中的配置示例
    DB_HOST = '127.0.0.1'  # 或您的 MySQL 服务器 IP 地址
    DB_PORT = 3306
    DB_USER = 'your_username'  # 替换为您的 MySQL 用户名
    DB_PASSWORD = 'your_password' # 替换为您的 MySQL 密码
    DB_NAME = 'ui_test' # 替换为您的数据库名
    ```

4.  **初始化表结构:** 导入 `schema.sql` 文件以在数据库中创建必要的表。
    ```bash
    mysql -u your_username -p ui_test < schema.sql
    ```

5.  **验证设置:** 您可以通过连接到数据库并运行以下命令来验证表是否正确创建：
    ```sql
    USE ui_test;
    SHOW TABLES;
    ```
    您应该能看到 `projects`、`modules` 和 `test_cases` 表。

## 运行应用

要启动 FastAPI 服务器，请从项目根目录运行以下命令：

```bash
uvicorn app.main:app --reload
```

应用程序将在 `http://127.0.0.1:8000` 上可用。

### 运行应用的其他方式：

1.  **使用内置的启动函数:**
    ```bash
    python -m app.main
    ```

2.  **使用自定义主机和端口运行:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
    这允许外部连接到您的服务器。

3.  **在生产模式下运行 (不重启):**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    ```
    这会启动带有 4 个工作进程的服务器以获得更好的性能。

## API 接口

该应用程序提供了多个用于管理项目、模块和测试用例的 API 端点。您可以在 `http://127.0.0.1:8000/docs` 浏览交互式 API 文档 (由 Swagger UI 提供)。

### 主要 API 端点：

- **项目:**
  - `GET /api/projects/` - 列出所有项目
  - `POST /api/projects/` - 创建新项目
  - `GET /api/projects/{project_id}` - 获取特定项目
  - `PUT /api/projects/{project_id}` - 更新特定项目
  - `DELETE /api/projects/{project_id}` - 删除特定项目

- **模块:**
  - `GET /api/projects/{project_id}/modules/` - 列出项目中的所有模块
  - `POST /api/projects/{project_id}/modules/` - 在项目中创建新模块
  - `GET /api/modules/{module_id}` - 获取特定模块
  - `PUT /api/modules/{module_id}` - 更新特定模块
  - `DELETE /api/modules/{module_id}` - 删除特定模块

- **测试用例:**
  - `GET /api/testcases/` - 列出所有测试用例
  - `POST /api/testcases/` - 创建新测试用例
  - `GET /api/testcases/{testcase_id}` - 获取特定测试用例
  - `PUT /api/testcases/{testcase_id}` - 更新特定测试用例
  - `DELETE /api/testcases/{testcase_id}` - 删除特定测试用例
  - `POST /api/testcases/{testcase_id}/run` - 运行特定测试用例
  - `GET /api/testcases/module/{module_id}/testcases` - 列出模块中的所有测试用例 (带分页)
  - `POST /api/testcases/module/{module_id}/run` - 运行模块中的所有测试用例
  - `POST /api/testcases/project/{project_id}/run` - 运行项目中的所有测试用例

- **关键字:**
  - `GET /api/keywords` - 获取测试步骤支持的所有关键字列表

### 健康检查:

- `GET /health` - 检查应用程序是否正常运行

## 如何运行测试

可以通过 Web 界面或通过从命令行运行 `run_tests.py` 脚本来执行测试。

### 通过 Web 界面运行测试：

1. 启动应用程序服务器
2. 在浏览器中导航到 `http://127.0.0.1:8000`
3. 选择一个项目和模块
4. 点击测试用例、模块或项目旁边的"运行"按钮

### 从命令行运行测试：

要从命令行运行特定的测试用例：

```bash
python run_tests.py --testcase_id <your_testcase_id>
```

要运行模块中的所有测试用例：

```bash
python run_tests.py --module_id <your_module_id>
```

要运行项目中的所有测试用例：

```bash
python run_tests.py --project_id <your_project_id>
```

要查看所有可用的命令行选项：

```bash
python run_tests.py --help
```

### 测试执行功能：

- 测试在项目设置中指定的浏览器 (Chromium、Firefox 或 WebKit) 中运行
- 可选择无头模式运行测试以提高执行速度
- 详细的测试执行日志
- 测试失败时自动捕获屏幕截图
- 为调试失败的测试生成跟踪文件

## 日志与报告

每次测试运行后，会生成以下内容：

*   **日志文件:** 详细的执行日志存储在 `logs/` 目录中。每次测试运行都会创建一个新的日志文件，其中包含每个步骤执行的详细信息。

*   **报告:** 测试运行的摘要，包括任何失败步骤的屏幕截图，都保存在 `reports/` 目录中。每次测试运行都会创建一个以测试用例 ID 和时间戳命名的新子目录。

*   **屏幕截图:** 失败的测试步骤会自动捕获屏幕截图，这些截图保存在 `reports/<run_id>/screenshots/` 目录中。

*   **跟踪文件:** 为每次测试运行生成 Playwright 跟踪文件 (trace.zip)，并保存在 `reports/<run_id>/` 目录中。这些文件可用于调试，可以使用 Playwright Trace Viewer 查看。

### 访问报告：

1.  **通过文件系统:** 导航到 `reports/` 目录查看所有报告。

2.  **使用 Playwright Trace Viewer:** 要查看跟踪文件进行调试：
    ```bash
    playwright show-trace reports/<run_id>/trace.zip
    ```

### 日志文件格式：

日志文件包含每个测试步骤的时间戳条目，包括：
- 步骤执行状态 (通过/失败)
- 失败步骤的错误消息
- 每个步骤的执行时间
- 失败步骤的屏幕截图引用

## 贡献

欢迎贡献！如果您有任何想法、建议或错误报告，请随时提出 issue 或提交 pull request。
