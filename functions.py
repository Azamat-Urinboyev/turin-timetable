import json
import os
import pandas as pd
import get_screenshots as update_timetable
from threading import Thread


def text_update(text, variables):
	#replace variables in the text with it value
	for var, new_val in variables.items():
		text = text.replace(var, new_val)
	return text


def reply_key(names: list,  row=1):
	from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
	from aiogram.utils.keyboard import ReplyKeyboardBuilder

	builder = ReplyKeyboardBuilder()
	for name in names:
		builder.button(text=name)
	builder.adjust(row)
	markup = ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)
	return markup


def get_inline(data, row=1):
	from aiogram.utils.keyboard import InlineKeyboardBuilder    ## Because when imported it runs module it takes less time if we import it here.

	builder = InlineKeyboardBuilder()
	for lan, call_data in data.items():
		builder.button(text=lan, callback_data=call_data)
	builder.adjust(row)
	return builder.as_markup()


def get_user_lan_data():
	with open("./data/user_languages.json") as file:
		user_language = json.load(file)
	return user_language


def add_user_language(user_id, language):
	user_language = get_user_lan_data()
	user_language[str(user_id)] = language

	with open("./data/user_languages.json", "w") as file:
		json.dump(user_language, file)

def univer_btns():
	univers = pd.read_csv("./data/univer_info.csv")
	univer_btn_data = {}
	for index, row in univers.iterrows():
		univer_name = row.iloc[0]
		name = row.iloc[3]

		univer_btn_data[univer_name] = f"choose_univer_{name}"

	univer_btn = get_inline(univer_btn_data)
	return univer_btn


def get_groups_btn(university):
	with open("./data/group_names.json") as file:
		group_names = json.load(file)[university]
		
	
	for key, groups in group_names.items():
		groups_btn_data = {}
		for group in groups:
			groups_btn_data[group] = f"choose_gp&{group}"
		btns = get_inline(groups_btn_data, row=3)
		group_names[key] = btns
	return group_names


def get_stats(database):
	columns = ["id", "full_name", "user_name", "university", "group"]
	data = database.get_all_data()
	data = pd.DataFrame(data, columns=columns)
	num_users = data.shape[0]
	by_univers = data.groupby(by="university").apply(lambda x: len(x))
	by_univers = str(by_univers).split("\n")
	by_univers.pop(0)
	by_univers.pop(-1)
	by_univers = "\n".join(by_univers)
	stats = f"Number of users:  {num_users}\n{by_univers}"
	return stats

def save_user_database(database):
	columns = ["id", "full_name", "user_name", "university", "group"]
	data = database.get_all_data()
	data = pd.DataFrame(data, columns=columns)
	data.to_csv("./data/users.csv")


def update_screenshots():
	thread = Thread(target=update_timetable.run)
	thread.start()

async def send_timetable(bot, database, admin):
	from aiogram.types.input_file import FSInputFile

	users_data = database.get_all_data()
	for row in users_data:
		user_id = row[0]
		univer = row[3]
		group = row[4]
		if user_id == admin:
			continue
		photo_path = f"./screenshots/{univer}/{group}.png"
		photo = FSInputFile(photo_path)
		try:
			await bot.send_photo(chat_id=user_id, photo=photo)
		except Exception as e:
			# await bot.send_message(chat_id=admin, text=str(e))
			database.remove_user(user_id)
	