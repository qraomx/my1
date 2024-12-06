from aiogram import F, Router, session
from aiogram import Bot, Dispatcher, F, types

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram.filters import CommandStart,Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode


from aiogram.types import Message
from aiogram.utils.markdown import hbold
#from apscheduler.schedulers.asyncio import AsyncIOScheduler


from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
#from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta


import app.keyboards as kb
import app.database.requests as rq

from texts import *

router = Router()
 

available_subjects=[sub1,sub2,sub3,sub4,sub5,sub6,sub7,sub8,sub9,sub10]
available_subjects_id=[1,2,3,10,5,4,7,8,9,12]
#available_actions=[btn_add_olimp,btn_del_olimp]


#Состояния
class SelectMyOlimps(StatesGroup):
    select_action = State()          #выбор из главного меню
    select_subject_change2= State()      #пользователь выбирает предмет олимпиады для редактирования своего списка v2
    
    
#обработка команды Start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await rq.set_user(message.from_user.id)   
    await message.answer(GREATING_TEXT, reply_markup=kb.main)   
    # Устанавливаем пользователю состояние "выбор из главного меню"
    await state.set_state(SelectMyOlimps.select_action)  

#обработка кнопки "на главную"  
@router.message(F.text == BTN_TO_BACK)
async def catalog(message: Message):
    await message.answer('Выберите пункт меню', reply_markup=kb.main)
     # Устанавливаем пользователю состояние "выбор из главного меню"
   # await state.set_state(SelectMyOlimps.select_action)  
  
  
#помощь для особо умных
@router.message(F.text == BTN_HELP)
async def catalog(message: Message):
    print("help")
    await message.answer(HELP_TEXT, reply_markup=kb.main)



#обработка кнопки "Мои олимпиады". Список всех олимпиад, которые отслеживает пользователь
@router.message(F.text == BTN_CURRENT_EVENTS)
async def add_olimp(message: Message):   
    user_id=message.from_user.id #ТГ номер юзера
    str_olimps_sub = await rq.get_user_olimp_all_subs(user_id) #получаем список олимпиад, на которые подписан юзер
    await message.answer(text=f'{str_olimps_sub}',
                         reply_markup=kb.main, 
                         parse_mode = ParseMode.HTML, 
                         disable_web_page_preview=True) 


#обработка кнопки "Текущие события" . Показываем отборы на ближайшие 10 дней
@router.message(F.text == BTN_COMING_SOON)
async def add_olimp(message: Message):   
    user_id=message.from_user.id #ТГ номер юзера        
    text_news = await rq.get_user_news(user_id) #получаем список событий
    await message.answer(text=f'{text_news}',
                         reply_markup=kb.main, 
                         parse_mode = ParseMode.HTML, 
                         disable_web_page_preview=True)  


#обработка кнопки "редактировать мои олимпиады v2"  
@router.message(F.text == BTN_CHANGE_MY_OLIMPS)
async def add_olimp(message: Message, state: FSMContext):
    await message.answer(SELECT_SUB_TEXT, 
                         reply_markup=kb.kb_subjects)
    # Устанавливаем пользователю состояние "выбирает предмет"
    await state.set_state(SelectMyOlimps.select_subject_change2)


#выбор предмета, чтобы отредактировать список олимпиад v2
@router.message(SelectMyOlimps.select_subject_change2, F.text.in_(available_subjects))
async def sub_chosenv2(message: Message, state: FSMContext):
 
    my_sub=message.text.lower()
    await state.update_data(chosen_sub=my_sub)   

    #находим ID предмета по его названию  
    idx = available_subjects.index(my_sub)  
    id_sub=available_subjects_id[idx] 
    user_id=message.from_user.id     
 
    olimp_top5_btns = await rq.get_top5_olimp_list(user_id,id_sub,1) #топ5 олимпиад по предмету на страницу. массив кнопок
 
    olimp_top5_text = await rq.get_top5_olimp_text(user_id,id_sub,1) #топ5 олимпиад по предмету на страницу. текст


    
    #показ топ 5 олимпиад и 5 кнопок вкл/выкл
    await message.answer(
        text = olimp_top5_text,
        reply_markup=await kb.inline_top5_olimpList(olimp_top5_btns,1),          
                         parse_mode = ParseMode.HTML, 
                         disable_web_page_preview=True ) 
    
    #сообщения о том, как выйти и кнопка "на главную"      
    await message.answer(
        text = GO_AWAY_TEXT,
        reply_markup=kb.kb_to_main 
    ) 
    await state.set_state(SelectMyOlimps.select_action)
 

#реакция на Вкл/выкл олимпиады для отслеживания в клавиатуре топ-5
@router.callback_query(lambda c: c.data.startswith('select_mytop5olimp_'))
async def process_olimps_buttons(call: CallbackQuery):     
    user_id=call.from_user.id                 #номер пользователя
    id= int(call.data.split('_')[-1])         #номер олимпиады
    index = int(call.data.split('_')[-2])#-1  #индекс в массиве кнопок
    
    print(call.data)
    # Текст кнопки
    current_text = call.message.reply_markup.inline_keyboard[0][index].text
        

    if BTN_YES in current_text:       
        #была галочка, стал крестик.  
        new_text = current_text.replace(BTN_YES, BTN_NO).strip()        
        #Удаляем олимпиаду из списка
        await rq.del_user_olimp(user_id,id)             
    else:  
        #была крестик , стал галочка. 
        new_text = current_text.replace(BTN_NO,BTN_YES ).strip()
        #добавляем олимпиаду из списка
        await rq.add_user_olimp(user_id,id)     
    
    # Обновление кнопки
    call.message.reply_markup.inline_keyboard[0][index].text = new_text
        
    # Обновление разметки
    await call.message.edit_reply_markup(reply_markup=call.message.reply_markup)
    await call.answer()
   

#реакция на кнопки вперед-назад в клавиатуре топ-5
@router.callback_query(lambda c: c.data.startswith('select_page_'))
async def process_olimps_buttons(call: CallbackQuery):  
    print(call.data)   
    user_id=call.from_user.id                 #номер пользователя
    page_id= int(call.data.split('_')[-2])         # номер страницы
    id_sub = int(call.data.split('_')[-1])     # предмет
 
    olimp_top5_btns = await rq.get_top5_olimp_list(user_id,id_sub,page_id) #топ5 олимпиад по предмету на страницу. массив кнопок 
    olimp_top5_text = await rq.get_top5_olimp_text(user_id,id_sub,page_id) #топ5 олимпиад по предмету на страницу. текст
    #print('olimp_top5_text: ',olimp_top5_text)

    cnt_olimps= await rq.get_count_olimp_by_sub(id_sub) #общее количество олимпиад для данного предмета
    #print('cnt_olimps=',cnt_olimps)
    show_next_page=1
    if (page_id*5>=cnt_olimps):
        show_next_page=0

    #изменяем текущее сообщение новым текстом и кнопками
    await call.message.edit_text(text=olimp_top5_text,
                                 reply_markup=await kb.inline_top5_olimpList(olimp_top5_btns,show_next_page),
                                 parse_mode = ParseMode.HTML, 
                                 disable_web_page_preview=True)
    
    
    
 

    
 


 
 