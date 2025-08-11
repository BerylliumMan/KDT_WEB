# app/crud.py
from fastapi import HTTPException
from .database import get_db_cursor
from . import models

# ----------------------------
# 项目CRUD
# ----------------------------

def create_project(project: models.ProjectCreate):
    """
    在数据库中创建新项目并将其作为Pydantic模型返回。
    """
    sql = "INSERT INTO projects (name, description, base_url, browser, headless) VALUES (%s, %s, %s, %s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(sql, (project.name, project.description, project.base_url, project.browser, project.headless))
        # 获取新创建的项目以返回它
        cursor.execute("SELECT * FROM projects WHERE name = %s ORDER BY id DESC LIMIT 1", (project.name,))
        project_data = cursor.fetchone()
        if project_data:
            return models.Project(**project_data)
        # 如果插入成功，理论上不应到达此情况
        raise HTTPException(status_code=500, detail="Could not retrieve created project.")

def get_project(project_id: int):
    """
    通过其ID检索单个项目并将其作为Pydantic模型返回。
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project_data = cursor.fetchone()
        if project_data:
            # 确保headless存在，如果不在DB中则默认为True
            if 'headless' not in project_data or project_data['headless'] is None:
                project_data['headless'] = True
            return models.Project(**project_data)
    return None

def get_all_projects():
    """
    检索所有项目并将它们作为Pydantic模型列表返回。
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects_data = cursor.fetchall()
        projects = []
        for p_data in projects_data:
            # 为所有项目应用headless默认值
            if 'headless' not in p_data or p_data['headless'] is None:
                p_data['headless'] = True
            projects.append(models.Project(**p_data))
        return projects

def update_project(project_id: int, project: models.ProjectUpdate):
    """
    更新现有项目并将更新的项目作为Pydantic模型返回。
    """
    sql = "UPDATE projects SET name = %s, description = %s, base_url = %s, browser = %s, headless = %s WHERE id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(sql, (project.name, project.description, project.base_url, project.browser, project.headless, project_id))
        updated_project = get_project(project_id)
        if not updated_project:
             raise HTTPException(status_code=404, detail="Project not found after update.")
        return updated_project

def delete_project(project_id: int):
    """
    删除项目及其所有关联资产（测试用例和步骤）。
    """
    with get_db_cursor(commit=True) as cursor:
        # 还删除关联的测试用例和步骤
        cursor.execute("SELECT id FROM test_cases WHERE project_id = %s", (project_id,))
        case_ids = [row['id'] for row in cursor.fetchall()]
        for case_id in case_ids:
            delete_test_case(case_id) # This will also delete steps
        
        cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        return {"message": f"项目 {project_id} 及其所有资产已删除。"}


# ----------------------------
# 模块CRUD
# ----------------------------

def create_module(module: models.ModuleCreate):
    sql = "INSERT INTO modules (project_id, name, description) VALUES (%s, %s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(sql, (module.project_id, module.name, module.description))
        cursor.execute("SELECT * FROM modules WHERE project_id = %s AND name = %s ORDER BY id DESC LIMIT 1", (module.project_id, module.name))
        module_data = cursor.fetchone()
        if module_data:
            return models.Module(**module_data)
        raise HTTPException(status_code=500, detail="Could not retrieve created module.")

def get_module(module_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM modules WHERE id = %s", (module_id,))
        module_data = cursor.fetchone()
        if module_data:
            return models.Module(**module_data)
    return None

def get_modules_for_project(project_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM modules WHERE project_id = %s ORDER BY name ASC", (project_id,))
        modules_data = cursor.fetchall()
        return [models.Module(**m) for m in modules_data]


def update_module(module_id: int, module: models.ModuleUpdate):
    sql = "UPDATE modules SET name = %s, description = %s WHERE id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(sql, (module.name, module.description, module_id))
        return get_module(module_id)

def delete_module(module_id: int):
    with get_db_cursor(commit=True) as cursor:
        # 将module_id设置为NULL用于关联的测试用例
        cursor.execute("UPDATE test_cases SET module_id = NULL WHERE module_id = %s", (module_id,))
        # 删除模块
        cursor.execute("DELETE FROM modules WHERE id = %s", (module_id,))
        return {"message": f"模块 {module_id} 已删除，其测试用例已取消分配。"}




# ----------------------------
# 测试用例CRUD
# ----------------------------

def create_test_case(case: models.TestCaseCreate):
    with get_db_cursor(commit=True) as cursor:
        # 创建测试用例
        sql = "INSERT INTO test_cases (project_id, module_id, name, description) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (case.project_id, case.module_id, case.name, case.description))
        
        # 获取新案例ID
        cursor.execute("SELECT id, created_at FROM test_cases WHERE project_id = %s AND name = %s ORDER BY id DESC LIMIT 1", (case.project_id, case.name))
        new_case_data = cursor.fetchone()
        case_id = new_case_data['id']
        created_at = new_case_data['created_at']

        # 创建步骤并收集它们
        created_steps = []
        for step_data in case.steps:
            step_to_create = models.TestStepCreate(
                case_id=case_id, 
                **step_data.dict()
            )
            # create_test_step现在需要返回创建步骤及其新ID
            created_step = create_test_step(step_to_create, cursor=cursor)
            created_steps.append(created_step)

        # 手动构造响应对象
        return models.TestCase(
            id=case_id,
            project_id=case.project_id,
            module_id=case.module_id,
            name=case.name,
            description=case.description,
            created_at=created_at,
            steps=created_steps
        )


def get_test_case(case_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM test_cases WHERE id = %s", (case_id,))
        case_data = cursor.fetchone()
        if case_data:
            case_data['steps'] = get_steps_for_case(case_id)
        return case_data

def get_all_test_cases_for_project(project_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM test_cases WHERE project_id = %s ORDER BY created_at DESC", (project_id,))
        cases = cursor.fetchall()
        for case in cases:
            case['steps'] = get_steps_for_case(case['id'])
        return cases

def get_all_test_cases_for_project_paginated(project_id: int, page: int = 1, size: int = 20):
    with get_db_cursor() as cursor:
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM test_cases WHERE project_id = %s", (project_id,))
        total_items = cursor.fetchone()['count']

        # Get paginated results
        offset = (page - 1) * size
        sql = "SELECT * FROM test_cases WHERE project_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(sql, (project_id, size, offset))
        cases = cursor.fetchall()
        for case in cases:
            case['steps'] = get_steps_for_case(case['id'])
            
        return {"total_items": total_items, "items": cases}

def get_all_test_cases_for_module(module_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM test_cases WHERE module_id = %s ORDER BY created_at DESC", (module_id,))
        cases = cursor.fetchall()
        for case in cases:
            case['steps'] = get_steps_for_case(case['id'])
        return cases

def get_all_test_cases_for_module_paginated(module_id: int, page: int = 1, size: int = 20):
    with get_db_cursor() as cursor:
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM test_cases WHERE module_id = %s", (module_id,))
        total_items = cursor.fetchone()['count']

        # Get paginated results
        offset = (page - 1) * size
        sql = "SELECT * FROM test_cases WHERE module_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(sql, (module_id, size, offset))
        cases = cursor.fetchall()
        for case in cases:
            case['steps'] = get_steps_for_case(case['id'])
        
        return {"total_items": total_items, "items": cases}


def delete_test_case(case_id: int):
    with get_db_cursor(commit=True) as cursor:
        # 首先删除案例的所有步骤
        cursor.execute("DELETE FROM test_steps WHERE case_id = %s", (case_id,))
        # 然后删除案例本身
        cursor.execute("DELETE FROM test_cases WHERE id = %s", (case_id,))
        return {"message": f"测试用例 {case_id} 及其步骤已删除。"}

def update_test_case(case_id: int, case: models.TestCaseUpdate):
    with get_db_cursor(commit=True) as cursor:
        # 1. 更新测试用例详细信息
        sql_update_case = "UPDATE test_cases SET name = %s, description = %s, module_id = %s WHERE id = %s"
        cursor.execute(sql_update_case, (case.name, case.description, case.module_id, case_id))

        # 2. 删除此测试用例的所有现有步骤
        cursor.execute("DELETE FROM test_steps WHERE case_id = %s", (case_id,))

        # 3. 插入新步骤列表
        for step_data in case.steps:
            step_to_create = models.TestStepCreate(
                case_id=case_id,
                **step_data.dict(exclude={'id'}) # Exclude 'id' if it exists
            )
            create_test_step(step_to_create, cursor=cursor)
            
        # 4. 获取并返回完全更新的测试用例
        return get_test_case(case_id)



# ----------------------------
# 测试步骤CRUD
# ----------------------------

def create_test_step(step: models.TestStepCreate, cursor=None):
    sql = """
    INSERT INTO test_steps (case_id, step_order, keyword, locator, value, description)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    def _execute(c):
        c.execute(sql, (step.case_id, step.step_order, step.keyword, step.locator, step.value, step.description))
        # 获取新创建的步骤
        c.execute("SELECT * FROM test_steps WHERE case_id = %s AND step_order = %s", (step.case_id, step.step_order))
        new_step_data = c.fetchone()
        return models.TestStep(**new_step_data)

    if cursor:
        return _execute(cursor)
    else:
        with get_db_cursor(commit=True) as c:
            return _execute(c)

def get_steps_for_case(case_id: int):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM test_steps WHERE case_id = %s ORDER BY step_order ASC", (case_id,))
        return cursor.fetchall()
