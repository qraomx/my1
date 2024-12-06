import asyncio
from aiogram import Bot, Dispatcher, F, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import Message

from app.handlers import router
from app.database.models import async_main
from secrets_and_text import token
from app.scheduler import send_message_scheduler
from datetime import datetime, timedelta
 
async def main(): 
    await async_main()
    bot= Bot(token=token)
    dp=Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)

    #создаем экземпляр класса AsyncIOScheduler    
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
  
    #Здесь будет запуск рассылки по рассписанию
    scheduler.add_job(send_message_scheduler,trigger="cron",hour=17,minute=00,start_date=datetime.now(), kwargs={"bot": bot },)
    #scheduler.add_job(send_message_scheduler,trigger="interval",seconds=60, kwargs={"bot": bot },)
   
    #стартуем работу
    scheduler.start()


    await dp.start_polling(bot)
    
if __name__=='__main__':
    try:
       asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')

