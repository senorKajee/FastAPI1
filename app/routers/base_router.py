"""
This Module contain explicit router for the base path of the application.

that will explicitly add to the root path of the application.
"""
from fastapi import APIRouter, HTTPException, Request,Body
from fastapi.responses import JSONResponse
from numpy import int64
from pydantic import BaseModel
from utils import get_task_info
from typing_extensions import Annotated
from typing import List
from bson.objectid import ObjectId

router = APIRouter(prefix='', responses={404: {"description": "Not found"}})

class TaskInferResonse(BaseModel):
    task_id: str

class TaskResult(BaseModel):
    label: str
    scores: float

class TaskInfoResponse(BaseModel):
    task_id: str
    task_status: str
    task_result: TaskResult



@router.get("/")
async def read_root()->dict:
    """Root of router use for health check."""
    return {"Hello": "World"}

@router.get("/infer",response_model=TaskInferResonse)
async def test_infer(request: Request)->TaskInferResonse:
    """Raw text to sentiment analysis This method use for testing purpose only."""
    # task = request.app.celery_app.send_task('infer_thai_text',args=['ร้านอาหารนี้อาหารอร่อยมาก แต่ราคามันแพงมาก แต่ก็คุ้มค่ากับรสชาติที่ดีมาก และบริการด้วย แนะนำให้ลองกิน และมีเมนูอาหารหลากหลายมาก และราคาก็ไม่แพงเท่าที่คิด'])
    task = request.app.celery_app.send_task('infer_en_text',args=['The food is delicious, but the price is very expensive, but it is worth it with the good taste and service, I recommend you to try it, and there are many menus and prices are not expensive as you think'])
    res = TaskInferResonse(task_id=task.id)
    return res

@router.get("/twiiter/{keyword}/{limit}")
async def twitter(keyword:str,limit:int,request:Request)->TaskInferResonse:
    """Create task for twitter scapping to celery worker."""
    # task = infer_thai_text.delay('ร้านอาหารนี้อาหารอร่อยมาก แต่ราคามันแพงมาก แต่ก็คุ้มค่ากับรสชาติที่ดีมาก และบริการด้วย แนะนำให้ลองกิน และมีเมนูอาหารหลากหลายมาก และราคาก็ไม่แพงเท่าที่คิด')
    # task = infer_en_text.delay('The food is delicious, but the price is very expensive, but it is worth it with the good taste and service, I recommend you to try it, and there are many menus and prices are not expensive as you think')
    if len(keyword.lstrip()) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    task = request.app.celery_app.send_task('get_twitter_scape',args=[keyword,limit])
    res = TaskInferResonse(task_id=task.id)
    return res

class TaskInfer2Req(BaseModel):
    keywords: List[str]
    analysisJobId: str
    since: str
    until: str

@router.post("/twiiter2")
async def twitter2(task:Annotated[TaskInfer2Req,Body()],request:Request)->TaskInferResonse:
    """Create task for twitter scapping to celery worker."""
    keywords = task.keywords
    analysisjobId = task.analysisJobId    
    since = task.since
    until = task.until
    bson_obj = ObjectId(analysisjobId)
    # request.app.database['AnalysisJob'].update_one({"_id":bson_obj},{"$set":{"status":"RUNNING"}})

    if len(keywords[0].lstrip()) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    task = request.app.celery_app.send_task('get_twitter_scape',args=[keywords,5000,analysisjobId,since,until],retries=3, retry_backoff=True, retry_backoff_max=60, retry_jitter=True, retry_jitter_max=10)
    res = TaskInferResonse(task_id=task.id)
    return res



@router.get("/tasks/{task_id}",response_model=TaskInfoResponse)
def get_status(task_id:str, request: Request)->TaskInfoResponse:
    """
    Return a task status and result. of the given task_id.

    in case of task is pending, return 202 status code and location header.
    """
    task_result = get_task_info(request.app.celery_app,task_id)
    print(task_result)
    if task_result['task_status'] == 'PENDING':
        response = JSONResponse(status_code=202, content={"task_id": task_id, "task_status": task_result['task_status']})
        response.headers["Location"] = "/tasks/"+task_id
        return response
    label,scores = task_result['task_result']
    scores:int64 = scores.tolist()

    res = TaskInfoResponse(task_id=task_id,task_status=task_result['task_status'],task_result=TaskResult(label=label,scores=scores))


    return res


