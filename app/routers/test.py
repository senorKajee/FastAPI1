from fastapi import APIRouter,Request
# from tasks.worker import create_task,infer_thai_text,infer_en_text
from fastapi.responses import JSONResponse
from typing import Union
from numpy import int64
from utils import get_task_info
# from main import app
router = APIRouter(prefix='', responses={404: {"description": "Not found"}})
# app = Celery('tasks', broker='redis://localhost:6379', backend='redis://localhost:6379',include=['tasks.worker'])

@router.get("/")
async def read_root():
    return {"Hello": "World"}

# @router.get("/testQueue")
# async def testQueue():
#     task = create_task.delay(1)
#     return {"task_id": task.id}

@router.get("/infer")
async def test_infer(request: Request):
    # task = infer_thai_text.delay('ร้านอาหารนี้อาหารอร่อยมาก แต่ราคามันแพงมาก แต่ก็คุ้มค่ากับรสชาติที่ดีมาก และบริการด้วย แนะนำให้ลองกิน และมีเมนูอาหารหลากหลายมาก และราคาก็ไม่แพงเท่าที่คิด')
    # task = infer_en_text.delay('The food is delicious, but the price is very expensive, but it is worth it with the good taste and service, I recommend you to try it, and there are many menus and prices are not expensive as you think')
    task = request.app.celery_app.send_task('infer_en_text',args=['The food is delicious, but the price is very expensive, but it is worth it with the good taste and service, I recommend you to try it, and there are many menus and prices are not expensive as you think'])
    # task = request.app.celery_app.send_task('infer_thai_text',args=['ร้านอาหารนี้อาหารอร่อยมาก แต่ราคามันแพงมาก แต่ก็คุ้มค่ากับรสชาติที่ดีมาก และบริการด้วย แนะนำให้ลองกิน และมีเมนูอาหารหลากหลายมาก และราคาก็ไม่แพงเท่าที่คิด'])

    return {"task_id": task.id}

@router.get("/twiiter")
async def twitter(request: Request):
    # task = infer_thai_text.delay('ร้านอาหารนี้อาหารอร่อยมาก แต่ราคามันแพงมาก แต่ก็คุ้มค่ากับรสชาติที่ดีมาก และบริการด้วย แนะนำให้ลองกิน และมีเมนูอาหารหลากหลายมาก และราคาก็ไม่แพงเท่าที่คิด')
    # task = infer_en_text.delay('The food is delicious, but the price is very expensive, but it is worth it with the good taste and service, I recommend you to try it, and there are many menus and prices are not expensive as you think')
    task = request.app.celery_app.send_task('get_twitter_scape',args=['9arm',1000])
    return {"task_id": task.id}


@router.get("/tasks/{task_id}")
def get_status(task_id:str, request: Request):
    print(task_id)
    # task_result = request.app.celery_app.AsyncResult(task_id)
    task_result = get_task_info(request.app.celery_app,task_id)
    print(task_result)
    if task_result['task_status'] == 'PENDING':
        response = JSONResponse(status_code=202, content={"task_id": task_id, "task_status": task_result['task_status']})
        response.headers["Location"] = "/tasks/"+task_id
        return response
    label,scores = task_result['task_result']
    scores:int64 = scores.tolist()
    

    return {"task_id": task_id, "task_status": task_result['task_status'], "task_result": {"label":label,"scores":float(scores)}}

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
