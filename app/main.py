# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .routers import project_router, testcase_router, module_router
from core.keyword_engine import KeywordEngine
from config import APP_HOST, APP_PORT
import uvicorn

# Import agent router
try:
    from agent.router import router as agent_router
    AGENT_SUPPORT = True
except ImportError:
    AGENT_SUPPORT = False
    print("Agent support not available")


app = FastAPI(
    title="UI测试自动化平台",
    description="用于管理和运行Playwright UI测试的Web平台。",
    version="1.0.0"
)

# 挂载静态文件（用于CSS、JS）
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="app/templates")

# 包含API路由
app.include_router(project_router.router)
app.include_router(testcase_router.router)
app.include_router(module_router.router)

# Include agent router if available
if AGENT_SUPPORT:
    app.include_router(agent_router)

@app.get("/api/keywords")
def get_keywords():
    """
    返回支持的关键词列表。
    """
    # 我们可以从KeywordEngine的映射中获取键
    return KeywordEngine.KEYWORD_DEFINITIONS

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    提供主HTML页面。
    """
    # 这些数据可用于预加载页面并初始化状态
    # 在实际应用中，您可能会在此处获取第一个项目及其测试用例
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "title": "UI测试平台"
    })

# 可选：添加健康检查端点
@app.get("/health")
def health_check():
    return {"status": "ok"}

def start():
    """
    由uvicorn运行器调用以启动服务器。
    """
    print(f"在 http://{APP_HOST}:{APP_PORT} 启动服务器")
    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True # 在代码更改时重新加载服务器，对开发有用
    )

if __name__ == "__main__":
    # 这允许通过 `python app/main.py` 直接运行应用程序
    start()
