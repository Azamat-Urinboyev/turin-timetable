import asyncio
from os import getenv

from aiogram import F
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext

from config import TOKEN, FEEDBACK_GROUP, ADMIN
from states import User, Admin
from data.database_setup import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import functions as func
from datetime import datetime
import json
from pytz import utc




#-----------Open files---------------------#
with open("./data/languages.json") as file:
    languages = json.load(file)

user_info = func.get_user_lan_data()



dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


db = Database()
scheduler = AsyncIOScheduler(timezone=utc)



def schedule_jobs():
    trigger_updating = CronTrigger(year="*", month="*", day_of_week="6", day="*", hour="18", minute="0", second="0")
    trigger_sending = CronTrigger(year="*", month="*", day_of_week="6", day="*", hour="18", minute="30", second="0")
    trigger_updating_day = CronTrigger(hour="13", minute="10", second="0")

    scheduler.add_job(func.update_screenshots, trigger=trigger_updating_day, kwargs={"only_turin": True})
    scheduler.add_job(func.update_screenshots, trigger=trigger_updating)
    scheduler.add_job(func.send_timetable, trigger=trigger_sending, args=(bot, db, ADMIN))




##----------------------------------Telegram bot------------------------------------##
@dp.message(CommandStart())
async def command_start_handler(message: Message, state=FSMContext) -> None:
    global user_info
    user_id = str(message.from_user.id)
    full_name = message.from_user.full_name
    username = message.from_user.username
    user_lan = message.from_user.language_code

    if not db.user_exist(user_id):
        db.insert_user(user_id=user_id, full_name=full_name, username=username)
    
    if user_id in user_info:
        user_lan = user_info[user_id]
        hello_msg = func.text_update(languages[user_lan]["hello_msg"], {"name123": full_name})
        await message.answer(hello_msg)
        univer_btns = func.univer_btns()
        await message.answer(languages[user_lan]["choose_univer"], reply_markup=univer_btns)
        return
    
    elif user_lan in languages:
        func.add_user_language(user_id=user_id, language=user_lan)
        user_info = func.get_user_lan_data()
        hello_msg = func.text_update(languages[user_lan]["hello_msg"], {"name123": full_name})
        await message.answer(hello_msg)
        univer_btns = func.univer_btns()
        await message.answer(languages[user_lan]["choose_univer"], reply_markup=univer_btns)
        return

    await ask_change_language(message)



@dp.message(Command("language"))
async def ask_change_language(message: Message) -> None:
    lan_btn_data = languages["languages"]
    lan_btn = func.get_inline(lan_btn_data, row=2)
    await message.answer(text=languages["uz"]["choose_lan"], reply_markup=lan_btn)



@dp.message(Command("feedback"))
async def send_feedback(message: Message, state=FSMContext) -> None:
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    fedback_msg = languages[user_lan]["feedback"]
    back_btn = func.reply_key([languages[user_lan]["back"]])

    await message.answer(fedback_msg, reply_markup=back_btn)
    await state.set_state(User.feedback)


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.reply("Canceled ✅")

##------------------------------callback queries---------------------#
@dp.callback_query(F.data == "stats")
async def send_stats(call: CallbackQuery):
    stats = func.get_stats(database=db)
    await call.message.answer(stats)


@dp.callback_query(F.data == "send_msg_all")
async def send_message_all(call: CallbackQuery, state:FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]

    msg = languages[user_lan]["ask_admin_msg"]
    await call.message.answer(msg)
    await state.set_state(Admin.message)


@dp.callback_query(F.data == "update_timetable")
async def update_screenshots(call: CallbackQuery):
    func.update_screenshots()
    await call.message.answer(f"Timetable will be updated ✅")


@dp.callback_query(F.data == "get_users_db")
async def get_user_db(call: CallbackQuery):
    func.save_user_database(database=db)
    user_db_path = "./data/users.csv"

    user_db = types.input_file.FSInputFile(user_db_path)
    await call.message.answer_document(user_db)


@dp.callback_query(F.data.startswith("change_lan_"))
async def change_language(call: CallbackQuery):
    global user_info
    chosen_lan = call.data.split("_")[-1]
    user_id = call.message.chat.id

    func.add_user_language(user_id=user_id, language=chosen_lan)
    user_info = func.get_user_lan_data()

    changed_success = languages[chosen_lan]["lan_changed_success"]
    await call.message.edit_text(changed_success)
    
    ask_start = languages[chosen_lan]["ask_to_start"]
    await call.message.answer(ask_start)


@dp.callback_query(F.data.startswith("choose_univer_"))
async def choose_university(call: CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]
    univer = call.data.split("_")[-1]

    db.insert_univer(user_id=user_id, university=univer)
    ask_group = languages[user_lan]["ask_group"]
    await call.message.edit_text(ask_group)

    groups_btns = func.get_groups_btn(univer)
    msg_ids = []
    for group_name, btns in groups_btns.items():
        msg = await call.message.answer(group_name, reply_markup=btns)
        msg_ids.append(msg.message_id)
    await state.set_data({"msg_ids": msg_ids})
    

@dp.callback_query(F.data.startswith("choose_gp&"))
async def choose_group(call: CallbackQuery, state: FSMContext):
    user_id = str(call.message.chat.id)
    user_lan = user_info[user_id]
    group_name = call.data.split("&")[-1]

    db.insert_group(user_id=user_id, group=group_name)

    univer_btn_ids = await state.get_data()    ##deleting last button messages
    for i in univer_btn_ids["msg_ids"]:
        await bot.delete_message(call.message.chat.id, i)

    msg = languages[user_lan]["successfull"]
    await call.message.answer(msg)

    univer, group = db.get_univer_group(user_id)
    photo_path = f"./screenshots/{univer}/{group}.png"
    photo = types.input_file.FSInputFile(photo_path)

    msg = languages[user_lan]["timetable_week"]
    timetable_btn = func.reply_key([languages[user_lan]["timetable"]])
    await call.message.answer_photo(photo=photo, caption=msg, reply_markup=timetable_btn)



##-------------------reply-keyboard----------------------------#
@dp.message(lambda message: message.from_user.id == ADMIN and message.text == "Admin")
async def admin_controls(message: Message) -> None:
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    admin_checked = languages[user_lan]["admin_checked"]

    admin_btns = func.get_inline(languages[user_lan]["admin_controls"], row=2)
    await message.answer(admin_checked, reply_markup=admin_btns)



@dp.message(Admin.message)
async def get_timatable(message: Message, state: FSMContext) -> None:
    all_users = db.get_all_users()
    error_msgs = {}
    for user in all_users:
        user = user[0]
        exception = await send_rassilka(message, user)
        if exception:
            if str(exception) not in error_msgs:
                error_msgs[str(exception)] = 1
            else:
                error_msgs[str(exception)] += 1
    msg = []
    for exeption_text, number in error_msgs.items():
        msg.append(f"{exeption_text}:  {number}")
    if len(msg) != 0:
        await bot.send_message(ADMIN, "\n".join(msg))


async def send_rassilka(message, i):
    try:
        caption_entities = message.caption_entities
        entities = message.entities
        if message.content_type == "text":
            # text
            tex = message.text
            await bot.send_message(i, tex, entities=entities)
        elif message.content_type == "photo":
            # photo
            capt = message.caption
            photo = message.photo[-1].file_id
            await bot.send_photo(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "video":
            # video
            capt = message.caption
            photo = message.video.file_id
            await bot.send_video(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "audio":
            # audio
            capt = message.caption
            photo = message.audio.file_id
            await bot.send_audio(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "voice":
            # voice
            capt = message.caption
            photo = message.voice.file_id
            await bot.send_voice(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "animation":
            # animation
            capt = message.caption
            photo = message.animation.file_id
            await bot.send_animation(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "document":
            # document
            capt = message.caption
            photo = message.document.file_id
            await bot.send_document(i, photo, caption=capt, caption_entities=caption_entities)
        elif message.content_type == "video_note":
            # rounded video
            video = message.video_note.file_id
            await bot.send_video_note(i, video)
        return
    except Exception as e:
        return e



@dp.message(lambda message: message.text in languages["timetable"])
async def get_timatable(message: Message) -> None:
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]

    univer, group_name = db.get_univer_group(user_id)
    photo_path = f"./screenshots/{univer}/{group_name}.png"
    photo = types.input_file.FSInputFile(photo_path)

    msg = languages[user_lan]["timetable_week"]

    await message.answer_photo(photo=photo, caption=msg)


@dp.message(User.feedback)
async def test(message: Message, state=FSMContext):
    user_id = str(message.from_user.id)
    user_lan = user_info[user_id]
    if message.text in languages["back"]:
        await state.clear()
        timetable_btn = func.reply_key([languages[user_lan]["timetable"]])
        await message.reply("Ok", reply_markup=timetable_btn)
        return
    
    await bot.forward_message(chat_id=FEEDBACK_GROUP, from_chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(chat_id=FEEDBACK_GROUP, text=user_id)
    await message.reply(languages[user_lan]["send"])


@dp.message(lambda message: message.chat.id == FEEDBACK_GROUP)
async def answer_feedbacks(message: types.Message):
    try:
        if message.from_user.id == ADMIN:
            to_user = message.reply_to_message.text
            await bot.send_message(to_user, message.text)
        else:
            await message.reply("You are not an admin.")
    except:
        return


async def on_startup():
    schedule_jobs()


async def main() -> None:
    scheduler.start()
    func.update_screenshots()
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())