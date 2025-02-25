from sqlalchemy import select, result_tuple

from schemas import STaskAdd
from database import new_session, TasksOrm


class TaskRepository:
    @classmethod
    async def add_one(cls, data: STaskAdd):
        async with new_session() as session:
            task_dict =  data.model_dump()

            task = TasksOrm(**task_dict)
            session.add(task)
            await session.flush()
            await session.commit()
            return task.id


    @classmethod
    async def find_all(cls) -> list[STaskAdd]:
        async with new_session() as session:
            query = select(TasksOrm)
            result = await session.execute(query)
            task_models = result.scalars().all()
            task_shemas = [ STaskAdd.model_validate(task_models) for task in task_models]
            return task_models
