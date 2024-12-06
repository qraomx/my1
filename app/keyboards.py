from aiogram.types import (ReplyKeyboardMarkup,KeyboardButton, 
                           InlineKeyboardMarkup,InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import  types
from texts import *
#from app.database.requests import   get_sub_olimp
from app.database.models import   OlimpList

#главное меню
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=BTN_COMING_SOON), KeyboardButton(text=BTN_CURRENT_EVENTS)] ,
     [ KeyboardButton(text=BTN_CHANGE_MY_OLIMPS),KeyboardButton(text=BTN_HELP)]
     #, [KeyboardButton(text=btn_change_olimp1),KeyboardButton(text=btn_add_olimp), KeyboardButton(text=btn_del_olimp)] 
        ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню:') 
 
 

#меню предметы
kb_subjects = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=sub1), KeyboardButton(text=sub2)],
                                            [KeyboardButton(text=sub3),KeyboardButton(text=sub4)],
                                            [KeyboardButton(text=sub5),KeyboardButton(text=sub6)],
                                          [KeyboardButton(text=sub7),KeyboardButton(text=sub8)],
                                          [KeyboardButton(text=sub9),KeyboardButton(text=sub10)],
                                          [KeyboardButton(text=BTN_TO_BACK)] 
                                     ],
                                      resize_keyboard=True,
                                      input_field_placeholder='Выберите предмет:',
                                      one_time_keyboard=True)

#мини меню с 1 кнопкой "На главную" 
kb_to_main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_TO_BACK)]] ,                                     
                                      resize_keyboard=True,  
                                      one_time_keyboard=True)


#клавиатура  5+2 вкл/выкл кнопок для переключения отслеживания олимпиад
async def inline_top5_olimpList(olimpList:OlimpList,show_next_page:int):
    keyboard = InlineKeyboardBuilder()
    text_prev=BTN_PREV
    text_next=BTN_NEXT

    cnt=0
    cnt_arrays=0
    sub_id=0
    i=0

    for row in olimpList: 
        cnt=cnt+1
        sub_id=row.id_subject
        i=row.i
        page=1
        if (i>5 and i<=10):
            page=2
        if (i>10 and i<=15):
            page=3
        if (i>15 and i<=20):
            page=4
        if (i>20 and i<=25):
            page=5
        if (i>25 and i<=30):
            page=5

    #если есть записи
    if cnt>0:
        #показать кнопку "назад"           
        prev_page=page-1
        if prev_page<1:
            prev_page=1  
        keyboard.add(InlineKeyboardButton(text=text_prev, callback_data=f"select_page_{prev_page}_{sub_id}" )) 
        cnt_arrays=cnt_arrays+1  #считаем кол-во стрелок

    #печатаем основные 5 кнопок     
    for row in olimpList:            
        i=row.i
        i=i-(page-1)*5 

        if (row.subscribed==1):
            text_=BTN_YES +str(row.i)
        else:
            text_=BTN_NO +str(row.i)        
        keyboard.add(InlineKeyboardButton(text=text_, callback_data=f"select_mytop5olimp_{i}_{row.id}" )) 
 
    #если есть записи
    if cnt>0:
        # показать кнопку "вперед" 
        if show_next_page==1:             
            cnt_arrays=cnt_arrays+1
            next_page=page+1
            keyboard.add(InlineKeyboardButton(text=text_next, callback_data=f"select_page_{next_page}_{row.id_subject}" )) 
              
        #выводим клавиатуру на кол-во олимпиад+ кол-во стрелок
        return keyboard.adjust(cnt+cnt_arrays).as_markup()
    print('закончили inline_top5_olimpList')
   

 
 
