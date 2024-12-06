import asyncio 
from app.database.models import async_session
from app.database.models import User,  Subject,User_Olymp, OlimpList
from sqlalchemy import select, text, delete, insert
from sqlalchemy.dialects import sqlite
from texts import *

#добавить нового пользователя
async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


#список всех олимпиад пользователя по всем предметам (для кнопки "Мои олимпиады")
async def get_user_olimp_all_subs(tg_id: int):
    async with async_session() as session:         
        User_id=tg_id   
        query = text(f"select id,  id_olymp, olymp_name,id_subject , url_path, sub_name from v_user_olimps where  tg_id={tg_id} ")     
         
        #print(query)

        result =  await session.execute(query)                
        text_olimps=''
        i =0
        olymp_id=0
        for row in result:
            i=i+1
            #Печатаем олимпиаду и предмет
            text_olimps=text_olimps+f"\n{i}. <a href='{row.url_path}'>{row.olymp_name}</a> , {row.sub_name} \n" 
            olymp_id=row.id 
            
            #  находим и печаем этапы олимпиады
            query_steps= text(f"SELECT    id ,   step_name, date_text  from v_olymp_steps where id= {olymp_id}  ")     
 
            result_steps=  await session.execute(query_steps)    
            for step in result_steps:
                text_olimps=text_olimps+f"{step.step_name}:<b> {step.date_text}</b>\n" 

        if (len(text_olimps)>1):
            text_olimps=f'{MY_OLIMPS_TEXT} \n {text_olimps}'
        else:
            text_olimps=I_HAVE_NO_OLIMPS_TEXT
        return text_olimps

#Список отборов и событий на ближайшие 10 дней по олимпиадам (для кнопки "текущие события")
async def get_user_news(tg_id: int):
    async with async_session() as session:         
        User_id=tg_id   
        query = text(f"select id,  id_olymp, olymp_name,url_path,id_subject ,  sub_name,date_text,step_name from v_news where  tg_id={tg_id} ")     
        #print(query)

        result =  await session.execute(query)                
        text_olimps=''
        i =0
        
        for row in result:
            i=i+1            
            text_olimps=text_olimps+f"{i}. <a href='{row.url_path}'>{row.olymp_name}</a> , {row.sub_name} \n{row.step_name}:<b> {row.date_text}</b>\n\n"     
          
        if (len(text_olimps)>1):
            text_olimps=f'{SOME_OLIMP_NEWS_TEXT} \n {text_olimps}'
        else:
            text_olimps=NO_OLIMP_NEWS_TEXT
        return text_olimps           
        
 

#добавление олимпиады пользователя  по номеру олимпиады
async def add_user_olimp(tg_id: int,olimp_id: int) -> None:
    async with async_session() as session:
        #Находим олимпиаду у пользователя, чтобы проверить подписан ли он на нее
        IsExistOlimp = await session.scalar(select(User_Olymp)
                                            .where(User_Olymp.tg_id == tg_id)
                                            .where(User_Olymp.id_sub_olymps== olimp_id))
        
        #Если еще не подписан на эту олимпиаду, то добавляем в список "мои олимпиады"
        if not IsExistOlimp:            
            session.add(User_Olymp(tg_id=tg_id,id_sub_olymps= olimp_id))           
            await session.commit()

#удаление олимпиады пользователя  по номеру олимпиады
async def del_user_olimp(tg_id: int,olimp_id: int) -> None:
    async with async_session() as session: 
         #Находим олимпиаду у пользователя, чтобы проверить подписан ли он на нее
        IsExistOlimp2 = await session.scalar(select(User_Olymp)
                                            .where(User_Olymp.tg_id == tg_id)
                                            .where(User_Olymp.id_sub_olymps== olimp_id))
        
        # Пользователь подписан на олимпиаду, все ок, можно удалить из его списка "мои олимпиады"
        if IsExistOlimp2:               
            stmt = delete(User_Olymp).where(User_Olymp.tg_id == tg_id).where(User_Olymp.id_sub_olymps == olimp_id)
            #print(stmt)
            await session.execute(stmt)
            await session.commit()
 
 
#топ5 олимпиад по предмету на страницу. массив   
async def get_top5_olimp_list(tg_id: int,sub_id: int,pageID:int):
    async with async_session() as session:
        SubId=sub_id
        User_id=tg_id   
        #получим название предмета
        subject: Subject  = await session.scalar(select(Subject).where(Subject.id == sub_id)) 
     
        #список всех олимпиад по этому предмету
        query_all = text(f"select id,  id_olymp, olymp_name,id_subject ,  sub_name from v_sub_olymp where id_subject={SubId}  ") 
        #print("query_all= ",query_all)
        result_all =  await session.execute(query_all)        
        
        num_i=0
        
        my_olimp_list = []    
        for row in result_all:               
            num_i=num_i+1     
            if (num_i>((pageID-1)*5))&(num_i<=(pageID*5)):
                #print(f"{num_i}. {row.id}. {row.olymp_name} : {row.sub_name}" )
            
                #Находим олимпиаду у пользователя, чтобы проверить подписан ли он на нее
                IsItMyOlimp = await session.scalar(select(User_Olymp)
                                            .where(User_Olymp.tg_id == tg_id)
                                            .where(User_Olymp.id_sub_olymps== row.id))
                IsSubscribed=0
                if IsItMyOlimp:  
                    IsSubscribed=1
            
                ol=OlimpList(i=num_i,id=row.id,name=row.olymp_name+' : '+row.sub_name,subscribed=IsSubscribed,id_subject=row.id_subject)   
                my_olimp_list.append(ol)

        return my_olimp_list

#общее кол-во олимпиад по предмету  
async def get_count_olimp_by_sub( sub_id: int ):
    async with async_session() as session:        
        query_all = text(f"select count(id) cnt from v_sub_olymp where id_subject={sub_id}  ")      
        result_all =  await session.execute(query_all)           
        num=0 
        for row in result_all:               
            num=row.cnt 
        return num

 
#топ5 олимпиад по предмету на страницу. текст   
async def get_top5_olimp_text(tg_id: int,sub_id: int,pageID:int):
    async with async_session() as session:
        SubId=sub_id
        User_id=tg_id   
        #получим название предмета
        subject: Subject  = await session.scalar(select(Subject).where(Subject.id == sub_id)) 

        query = text(f"select id,  id_olymp, olymp_name,id_subject ,  sub_name ,url_path from v_sub_olymp where id_subject={SubId}  ") 
        #print(query)

        result =  await session.execute(query)         
        text_olimps=''
        i =0
        for row in result:
            i=i+1
            #показываем только 5 олимпиад на странице
            if (i>((pageID-1)*5))&(i<=(pageID*5)):
                text_olimps=text_olimps+f"{i}. <a href='{row.url_path}'>{row.olymp_name}</a> : {row.sub_name} \n"     

     
        if (len(text_olimps)>1):
            text_olimps=f'{subject.name}: страница {pageID}\n\n{text_olimps}'
        else:
            text_olimps=f'{subject.name}: Не нашлось олимпиад по предмету :('
        return text_olimps