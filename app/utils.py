

def get_task_info(celery,task_id):
        """
        return task info for the given task_id
        """
        task_result = celery.AsyncResult(task_id)
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result
        }
        return result
