import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import LinkPreviewOptions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from utils import service
from utils.handlers import routers_list
from utils.config import Config, load_config
from utils.middlewares.config import ConfigMiddleware
from utils.middlewares.scheduler import SchedulerMiddleware


def register_global_middlewares(dp: Dispatcher, 
                                config: Config,
                                scheduler: AsyncIOScheduler):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        SchedulerMiddleware(scheduler),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


async def main():
    service.start_logging()
    config = load_config(".env")
    storage = service.get_storage(config)
    bot = Bot(token=config.tgbot.token,
              default=DefaultBotProperties(
                  parse_mode="HTML",
                  link_preview=LinkPreviewOptions(is_disabled=True)))
    dp = Dispatcher(storage=storage)
    job_stores = {"default": RedisJobStore(
            jobs_key="dispatched_trips_jobs", 
            run_times_key="dispatched_trips_running",
            host=config.redis.redis_host,
            port=config.redis.redis_port,
            password=config.redis.redis_pass)}
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
    scheduler.ctx.add_instance(bot, 
                               declared_class=Bot)
    dp.include_routers(*routers_list)
    register_global_middlewares(dp, config, scheduler)
    scheduler.start()
    await service.on_startup(bot, config.tgbot.admins)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот выключен!!!")
