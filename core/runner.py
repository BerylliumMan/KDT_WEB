# core/runner.py
import asyncio
import logging
import os
import sys
import time
from datetime import datetime

# 将项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import crud, models
from app.database import get_db_cursor
from core.playwright_manager import PlaywrightManager
from core.keyword_engine import KeywordEngine

# 配置基本日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # 输出到控制台
    ]
)

async def run_test_case(case_id: int):
    """
    运行单个测试用例的主函数。
    """
    start_time = datetime.now()
    run_log_entries = []
    test_status = "Failed" # 默认为失败
    report_path = None
    log_file_path = None

    try:
        # 1. 获取测试用例和项目数据
        case_data = crud.get_test_case(case_id)
        if not case_data:
            raise ValueError(f"Test case with ID {case_id} not found.")
        
        project_data = crud.get_project(case_data['project_id'])
        if not project_data:
            raise ValueError(f"Project with ID {case_data['project_id']} not found.")

        # 为此运行创建唯一的输出目录
        run_timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join("reports", f"run_{case_id}_{run_timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        # 为此特定运行设置文件记录器
        log_file_path = os.path.join(output_dir, "run.log")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

        logging.info(f"开始测试用例：'{case_data['name']}' 来自项目：'{project_data.name}'")

        # 2. 初始化Playwright
        async with PlaywrightManager(browser_type=project_data.browser, headless=project_data.headless) as browser:
            # 创建带有跟踪文件的新页面
            report_path = os.path.join(output_dir, "report.zip")
            context = await browser.new_context(ignore_https_errors=True)
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            
            page = await context.new_page()
            engine = KeywordEngine(page, base_url=project_data.base_url or '', output_dir=output_dir)

            # 3. 执行步骤
            all_steps_succeeded = True
            for i, step in enumerate(case_data['steps']):
                step['id'] = i + 1  # 用循环索引覆盖步骤ID
                success, message, screenshot_path = await engine.execute_step(step)
                
                # 记录步骤结果
                log_level = "INFO" if success else "ERROR"
                run_log_entries.append({
                    "step_id": step['id'],
                    "level": log_level,
                    "message": message,
                    "screenshot_path": screenshot_path
                })

                if not success:
                    all_steps_succeeded = False
                    break # 第一次失败时停止
            
            # 4. 停止跟踪并保存报告
            trace_path = os.path.join(output_dir, "trace.zip")
            await context.tracing.stop(path=trace_path)
            await page.close()
            await context.close()
            
            # 注意：Playwright的HTML报告是从命令行生成的。
            # 跟踪文件（trace.zip）是其来源。我们保存其路径。
            # 为简单起见，我们将跟踪文件指向"报告"。
            report_path = trace_path


        test_status = "Passed" if all_steps_succeeded else "Failed"
        logging.info(f"测试用例 '{case_data['name']}' 以状态：{test_status} 完成")

    except Exception as e:
        test_status = "Failed"
        logging.error(f"运行案例 {case_id} 的测试期间发生意外错误：{e}", exc_info=True)
        run_log_entries.append({"step_id": None, "level": "CRITICAL", "message": str(e), "screenshot_path": None})

    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 5. 将运行结果保存到数据库
        save_run_results(case_id, test_status, start_time, end_time, duration, report_path, log_file_path, run_log_entries)
        
        # 清理文件处理器
        if 'file_handler' in locals() and file_handler:
            logging.getLogger().removeHandler(file_handler)
            file_handler.close()

def save_run_results(case_id, status, start_time, end_time, duration, report_path, log_path, logs):
    """将测试运行及其详细日志保存到数据库。"""
    try:
        with get_db_cursor(commit=True) as cursor:
            # 插入到test_runs
            sql_run = """
            INSERT INTO test_runs (case_id, status, start_time, end_time, duration, report_path, log_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_run, (case_id, status, start_time, end_time, duration, report_path, log_path))

            # 获取运行ID
            cursor.execute("SELECT id FROM test_runs WHERE case_id = %s ORDER BY id DESC LIMIT 1", (case_id,))
            run_id = cursor.fetchone()['id']

            # 插入到run_logs
            sql_log = """
            INSERT INTO run_logs (run_id, step_id, level, message, screenshot_path)
            VALUES (%s, %s, %s, %s, %s)
            """
            for log in logs:
                cursor.execute(sql_log, (run_id, log.get('step_id'), log['level'], log['message'], log.get('screenshot_path')))
            
            logging.info(f"案例 {case_id} 的测试运行结果已保存到数据库，运行ID为 {run_id}。")

    except Exception as e:
        logging.error(f"无法将测试运行结果保存到数据库：{e}", exc_info=True)

# 命令行入口点
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="运行特定测试用例。")
    parser.add_argument("case_id", type=int, help="要运行的测试用例的ID。")
    args = parser.parse_args()

     

    try:
        asyncio.run(run_test_case(args.case_id))
    except ValueError as e:
        if "I/O operation on closed pipe" not in str(e):
            raise # 如果不是预期错误，则重新引发
