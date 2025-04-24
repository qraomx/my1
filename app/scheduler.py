from aiogram import Bot 
import app.database.requests as rq
from texts import SOME_OLIMP_NEWS_TEXT
from aiogram.enums import ParseMode 
from sqlalchemy import  text 
from app.database.models import async_session
 

#оправить рассылку по юзерам
async def send_message_scheduler(bot: Bot ):
    async with async_session() as session:
        #Получаем список юзеров, которые подписаны хотя бы на 1 олимпиаду       
        query = text(f"select distinct tg_id from  User_Olymps ")     
       
        result =  await session.execute(query)      

        #для каждого отправляем рассылку
        for row in result:
            user_id=row.tg_id          
            #получаем список событий для рассылки
            news_message = await rq.get_user_news(user_id)      
            print('Бот отправил рассылку  для юзера   ',user_id)
            await bot.send_message(chat_id=int(user_id), text=news_message,parse_mode = ParseMode.HTML, disable_web_page_preview=True)
        