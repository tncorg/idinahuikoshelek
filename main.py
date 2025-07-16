_I='недостаточно хуйкоинов'
_H='ахуеть'
_G='coins'
_F='price'
_E='description'
_D='title'
_C='amount'
_B='claimed'
_A=True
import logging,json,os,uuid,asyncio,random
from aiogram import Bot,Dispatcher,F,Router
from aiogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton,CallbackQuery,LabeledPrice,PreCheckoutQuery
from aiogram.filters import Command,CommandObject
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from datetime import datetime,timedelta
from dotenv import load_dotenv
load_dotenv()
API_TOKEN=os.getenv('bot_token')
STARTING_COINS=100
BALANCE_FILE='balances.json'
WORK_TIME_FILE='work_times.json'
ROB_COOLDOWN_FILE='rob_cooldowns.json'
from aiogram.client.default import DefaultBotProperties
bot=Bot(token=API_TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher()
router=Router()
def add_coins(user_id,amount):user_balances[user_id]=user_balances.get(user_id,0)+amount;save_balances()
def load_balances():
	if os.path.exists(BALANCE_FILE):
		with open(BALANCE_FILE,'r')as f:return{int(k):v for(k,v)in json.load(f).items()}
	return{}
def save_balances():
	with open(BALANCE_FILE,'w')as f:json.dump({str(k):v for(k,v)in user_balances.items()},f)
def load_work_times():
	if os.path.exists(WORK_TIME_FILE):
		with open(WORK_TIME_FILE,'r')as f:return json.load(f)
	return{}
def save_work_times():
	with open(WORK_TIME_FILE,'w')as f:json.dump(work_times,f)
def load_rob_cooldowns():
	global rob_cooldowns
	if os.path.exists(ROB_COOLDOWN_FILE):
		with open(ROB_COOLDOWN_FILE,'r')as f:rob_cooldowns=json.load(f)
def save_rob_cooldowns():
	with open(ROB_COOLDOWN_FILE,'w')as f:json.dump(rob_cooldowns,f)
work_times=load_work_times()
user_balances=load_balances()
receipts={}
rob_cooldowns={}
@dp.message(Command('start'))
async def start_cmd(message:Message,command:CommandObject):
	user_id=message.from_user.id;args=command.args.split()if command.args else[]
	if not args:
		if user_id not in user_balances:user_balances[user_id]=STARTING_COINS;save_balances();await message.reply(f"приветствую! вы получили {STARTING_COINS} хуйкоинов")
		else:await message.reply('иди нахуй')
		return
	receipt_id=args[0]
	if receipt_id not in receipts:await message.reply('чек не существует или уже использован');return
	receipt=receipts[receipt_id]
	if receipt[_B]:await message.reply('чек уже забрали');return
	receipt[_B]=_A;user_balances[user_id]=user_balances.get(user_id,0)+receipt[_C];save_balances();await message.reply(f"вы забрали чек на <b>{receipt[_C]} хуйкоинов</b>",parse_mode=ParseMode.HTML)
@dp.message(Command('balance'))
async def balance_cmd(message:Message):user_id=message.from_user.id;balance=user_balances.get(user_id,0);await message.reply(f"у вас на балансе {balance} хуйкоинов")
@dp.message(Command('give'))
async def give_cmd(message:Message,command:CommandObject):
	user_id=message.from_user.id;parts=command.args.split()if command.args else[]
	if len(parts)!=2 or not parts[1].isdigit():await message.reply('использование: /give @username количество');return
	target_username=parts[0].lstrip('@');amount=int(parts[1])
	if amount<=0:await message.reply(_H);return
	sender_balance=user_balances.get(user_id,0)
	if sender_balance<amount:await message.reply(_I);return
	target_user_id=None
	for uid in user_balances:
		chat=await bot.get_chat(uid)
		if chat.username and chat.username.lower()==target_username.lower():target_user_id=uid;break
	if not target_user_id:await message.reply('хз, не ебу кто такой');return
	user_balances[user_id]-=amount;user_balances[target_user_id]=user_balances.get(target_user_id,0)+amount;save_balances();await message.answer(f"<b>@{message.from_user.username or message.from_user.full_name}</b> <b>{amount}</b> хуйкоинов были переведены <b>@{target_username}</b>")
@dp.message(Command('receipt'))
async def receipt_cmd(message:Message,command:CommandObject):
	user_id=message.from_user.id;parts=command.args.split()if command.args else[]
	if len(parts)!=1 or not parts[0].isdigit():await message.reply('использование: /receipt количество');return
	amount=int(parts[0])
	if amount<=0:await message.reply(_H);return
	if user_balances.get(user_id,0)<amount:await message.reply(_I);return
	user_balances[user_id]-=amount;save_balances();receipt_id=str(uuid.uuid4());receipts[receipt_id]={'creator_id':user_id,_C:amount,_B:False};keyboard=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"забрать {amount} хуйкоинов",callback_data=f"claim:{receipt_id}")]]);claim_link=f"https://t.me/idinahuikoshelekbot?start={receipt_id}";await message.answer(f"<b>@{message.from_user.username or message.from_user.full_name}</b> создал чек на <b>{amount} хуйкоинов</b>\nнажмите кнопку или ссылку снизу чтобы забрать\n\nссылка:\n{claim_link}",reply_markup=keyboard)
@dp.callback_query(F.data.startswith('claim:'))
async def handle_claim(callback:CallbackQuery):
	receipt_id=callback.data.split(':')[1];user_id=callback.from_user.id
	if receipt_id not in receipts:await callback.answer('чека не существет',show_alert=_A);return
	receipt=receipts[receipt_id]
	if receipt[_B]:await callback.answer('кто-то уже забрал чек',show_alert=_A);return
	receipt[_B]=_A;user_balances[user_id]=user_balances.get(user_id,0)+receipt[_C];save_balances();await callback.message.edit_text(f"пользователь <b>@{callback.from_user.username or callback.from_user.full_name}</b> забрал <b>{receipt[_C]} хуйкоинов</b>");await callback.answer('вы забрали чек')
@dp.message(Command('leaderboard'))
async def leaderboard_cmd(message:Message):
	if not user_balances:await message.reply('никто ещё не получил ни одного хуйкоина');return
	top_users=sorted(user_balances.items(),key=lambda x:x[1],reverse=_A)[:10];leaderboard_lines=[]
	for(i,(user_id,balance))in enumerate(top_users,start=1):
		try:user=await bot.get_chat(user_id);name=f"@{user.username}"if user.username else user.full_name
		except Exception:name=f"пользователь {user_id}"
		leaderboard_lines.append(f"{i}. {name} — {balance} хуйкоинов")
	leaderboard_text='<b>топ 10 по балансу:</b>\n\n'+'\n'.join(leaderboard_lines);await message.reply(leaderboard_text)
@dp.message(Command('work'))
async def work_cmd(message:Message):
	user_id=str(message.from_user.id);now=datetime.utcnow();last_time_str=work_times.get(user_id)
	if last_time_str:
		last_time=datetime.fromisoformat(last_time_str)
		if now-last_time<timedelta(minutes=20):remaining=timedelta(minutes=20)-(now-last_time);mins,secs=divmod(remaining.seconds,60);await message.reply(f"иди отдохни. повторно можно через {mins} мин {secs} сек");return
	reward=random.randint(70,250);from texts import job_texts;flavor=random.choice(job_texts);user_balances[message.from_user.id]=user_balances.get(message.from_user.id,0)+reward;save_balances();work_times[user_id]=now.isoformat();save_work_times();await message.reply(f"{flavor} и получили <b>{reward} хуйкоинов</b>",parse_mode=ParseMode.HTML)
@dp.message(Command('casino'))
async def casino_cmd(message:Message,command:CommandObject):
	E='⭐';D='🍋';C='🍒';B='BAR';A='7';user_id=message.from_user.id;parts=command.args.split()if command.args else[]
	if len(parts)!=1 or not parts[0].isdigit():await message.reply('использование: /casino количество');return
	bet=int(parts[0])
	if bet<=0:await message.reply('ставка должна быть положительным числом');return
	balance=user_balances.get(user_id,0)
	if bet>balance:await message.reply('у вас недостаточно хуйкоинов для такой ставки');return
	user_balances[user_id]=balance-bet;save_balances();weighted_symbols=[A]*3+[B]*5+[C]*8+[D]*8+[E]*26;spin=[random.choice(weighted_symbols)for _ in range(3)];spin_text=' '.join(spin);winnings=0;message_result=''
	if spin[0]==spin[1]==spin[2]:
		symbol=spin[0]
		if symbol==A:winnings=int(bet*5);message_result=f"джекпот! вы выиграли <b>{winnings} хуйкоинов</b>!"
		elif symbol==B:winnings=int(bet*2);message_result=f"три BAR! вы выиграли <b>{winnings} хуйкоинов</b>!"
		elif symbol in[C,D]:winnings=int(bet*1.7);message_result=f"три {symbol}! вы выиграли <b>{winnings} хуйкоинов</b>!"
		elif symbol==E:winnings=int(bet*1.2);message_result=f"три звезды! вы выиграли <b>{winnings} хуйкоинов</b>!"
	elif spin[0]==spin[1]or spin[1]==spin[2]or spin[0]==spin[2]:
		if spin[0]==spin[1]or spin[0]==spin[2]:pair_symbol=spin[0]
		else:pair_symbol=spin[1]
		if pair_symbol==A:winnings=int(bet*.5);message_result=f"две 7! вернули половину ставки: <b>{winnings} хуйкоинов</b>."
		elif pair_symbol==B:winnings=int(bet*.3);message_result=f"два BAR! вернули 30% ставки: <b>{winnings} хуйкоинов</b>."
		elif pair_symbol in[C,D]:winnings=int(bet*.1);message_result=f"две {pair_symbol}! вернули 10% ставки: <b>{winnings} хуйкоинов</b>."
		elif pair_symbol==E:winnings=int(bet*.05);message_result=f"две звезды! вернули 5% ставки: <b>{winnings} хуйкоинов</b>."
	else:message_result=f"вы проебали <b>{bet}</b> хуйкоинов."
	if winnings>0:user_balances[user_id]+=winnings;save_balances()
	await message.reply(f"{spin_text}\n\n{message_result}\n\nновый баланс: <b>{user_balances[user_id]}</b>",parse_mode=ParseMode.HTML)
PRODUCTS={'tier_1k':{_D:'1,000 хуйкоинов',_E:'1к хуйкоинов',_F:10,_G:1000},'tier_5k':{_D:'5,000 хуйкоинов',_E:'5к хуйкоинов',_F:45,_G:5000},'tier_10k':{_D:'10,000 хуйкоинов',_E:'10к хуйкоинов',_F:80,_G:10000}}
PROVIDER_TOKEN=''
@dp.message(Command('stars'))
async def show_shop(message:Message):keyboard=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='1,000 — 10 звезд',callback_data='buy:tier_1k')],[InlineKeyboardButton(text='5,000 — 45 звезд',callback_data='buy:tier_5k')],[InlineKeyboardButton(text='10,000 — 80 звезд',callback_data='buy:tier_10k')]]);await message.answer('выберите количество хуйкоинов для покупки:',reply_markup=keyboard)
@dp.callback_query(F.data.startswith('buy:'))
async def process_buy_callback(callback:CallbackQuery):
	tier_key=callback.data.split(':')[1];product=PRODUCTS.get(tier_key)
	if not product:await callback.answer('ошибка: неизвестный товар',show_alert=_A);return
	await bot.send_invoice(chat_id=callback.from_user.id,title=product[_D],description=product[_E],payload=tier_key,provider_token=PROVIDER_TOKEN,currency='XTR',prices=[LabeledPrice(label=product[_D],amount=product[_F])],start_parameter='buyitem',is_flexible=False);await callback.answer()
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query:PreCheckoutQuery):await bot.answer_pre_checkout_query(pre_checkout_query.id,ok=_A)
@dp.message(F.successful_payment)
async def process_successful_payment(message:Message):
	tier_key=message.successful_payment.invoice_payload;product=PRODUCTS.get(tier_key)
	if not product:await message.reply('произошла ошибка при обработке оплаты.');return
	user_id=message.from_user.id;coins_to_add=product[_G];user_balances[user_id]=user_balances.get(user_id,0)+coins_to_add;save_balances();await message.reply(f"спасибо за покупку! вы получили <b>{coins_to_add} хуйкоинов</b>.",parse_mode=ParseMode.HTML)
EXCLUDED_FROM_ROBBERY={5407081696}
@dp.message(Command('rob'))
async def rob_cmd(message:Message,command:CommandObject):
	user_id=message.from_user.id;parts=command.args.split()if command.args else[]
	if len(parts)!=1 or not parts[0].startswith('@'):await message.reply('использование: /rob @username');return
	now=datetime.utcnow();last_rob_time_str=rob_cooldowns.get(user_id)
	if last_rob_time_str:
		last_rob_time=datetime.fromisoformat(last_rob_time_str)
		if now-last_rob_time<timedelta(minutes=60):remaining=timedelta(minutes=60)-(now-last_rob_time);mins,secs=divmod(remaining.seconds,60);await message.reply(f"подожди ещё {mins} мин {secs} сек.");return
	target_username=parts[0].lstrip('@');target_user_id=None
	for uid in user_balances:
		try:
			chat=await bot.get_chat(uid)
			if chat.username and chat.username.lower()==target_username.lower():target_user_id=uid;break
		except:continue
	if not target_user_id:await message.reply('такого пользователя не найдено');return
	if target_user_id==user_id:await message.reply('самого себя грабить нельзя');return
	if target_user_id in EXCLUDED_FROM_ROBBERY:await message.reply('этого пользователя грабить нельзя');return
	robber_balance=user_balances.get(user_id,0);victim_balance=user_balances.get(target_user_id,0)
	if victim_balance<50:await message.reply('у жертвы слишком мало хуйкоинов');return
	success_chance=.4;fine=random.randint(30,80)
	if random.random()<success_chance:stolen_amount=random.randint(30,min(150,victim_balance));user_balances[user_id]=robber_balance+stolen_amount;user_balances[target_user_id]=victim_balance-stolen_amount;result_msg=f"вы успешно ограбили @{target_username} и украли <b>{stolen_amount} хуйкоинов</b>!"
	else:user_balances[user_id]=max(0,robber_balance-fine);result_msg=f"грабёж не удался! вы заплатили штраф <b>{fine} хуйкоинов</b>"
	save_balances();rob_cooldowns[user_id]=now.isoformat();save_rob_cooldowns();await message.reply(result_msg,parse_mode=ParseMode.HTML)
ADMIN_IDS={5407081696}
@dp.message(Command('broadcast'))
async def broadcast_cmd(message:Message,command:CommandObject):
	user_id=message.from_user.id
	if user_id not in ADMIN_IDS:await message.reply('нет.');return
	if not command.args:await message.reply('использование: /broadcast сообщение');return
	broadcast_message=command.args;success_count=0;failed_count=0
	for target_user_id in user_balances:
		try:await bot.send_message(chat_id=target_user_id,text=broadcast_message,parse_mode=ParseMode.HTML);success_count+=1;await asyncio.sleep(.05)
		except Exception as e:logging.error(f"failed to send broadcast to {target_user_id}: {str(e)}");failed_count+=1
	await message.reply(f"успешно\nотправлено: {success_count} пользователям\nне удалось: {failed_count} пользователей")
@dp.message(Command('drink'))
async def drinkcmd(message:Message,command:CommandObject):
	user_id=message.from_user.id;parts=command.args.split()if command.args else[]
	if len(parts)!=1 or not parts[0].isdigit():await message.reply('использование: /drink количество');return
	howmuch=int(parts[0])
	if howmuch<=0:await message.reply('количество должно быть положительным числом');return
	pay=howmuch*250;balance=user_balances.get(user_id,0)
	if pay>balance:await message.reply('у вас недостаточно хуйкоинов для такого количества водки');return
	user_balances[user_id]=balance-pay;save_balances()
	if howmuch==1:await message.reply(f"вы купили 1 бутылку за {pay} хуйкоинов и выпили все.")
	if howmuch<=5 and not howmuch==1:await message.reply(f"вы купили {howmuch} бутылок за {pay} хуйкоинов и выпили все.",parse_mode=ParseMode.HTML)
	if howmuch>5:await message.reply(f"вы купили {howmuch} бутылок за {pay} хуйкоинов и получили похмелье.")
@dp.message(Command('manage_balance'))
async def manage_balance_cmd(message:Message,command:CommandObject):
	C='set';B='deduct';A='reset';user_id=message.from_user.id
	if user_id not in ADMIN_IDS:await message.reply('нет.');return
	parts=command.args.split()if command.args else[]
	if len(parts)<2 or parts[1].lower()!=A and len(parts)!=3:await message.reply('напоминаю: /manage_balance @username [deduct|set|reset|add] количество. если не сработало, то ты ебланище');return
	target_username=parts[0].lstrip('@');action=parts[1].lower();amount=int(parts[2])if len(parts)==3 else 0
	if action not in[B,C,A,'add']:await message.reply('ты еблан');return
	if action in[B]and amount<=0:await message.reply('пошел нахуй');return
	target_user_id=None
	for uid in user_balances:
		try:
			chat=await bot.get_chat(uid)
			if chat.username and chat.username.lower()==target_username.lower():target_user_id=uid;break
		except:continue
	if not target_user_id:await message.reply('ну крч иди нахуй не нашел');return
	if action==B:
		current_balance=user_balances.get(target_user_id,0)
		if amount>current_balance:await message.reply('увага: нищеброд');return
		user_balances[target_user_id]=current_balance-amount;action_text=f"вычтено {amount} хуйкоинов"
	elif action==C:user_balances[target_user_id]=amount;action_text=f"установлено {amount} хуйкоинов"
	elif action==A:user_balances[target_user_id]=STARTING_COINS;action_text=f"сброшено до {STARTING_COINS} хуйкоинов"
	else:current_balance=user_balances.get(target_user_id,0);user_balances[target_user_id]=current_balance+amount;action_text=f"добавлено {amount} хуйкоинов"
	save_balances();await message.reply(f"<b>@{target_username}</b>: {action_text}\nновый баланс: <b>{user_balances[target_user_id]}</b> хуйкоинов",parse_mode=ParseMode.HTML)
@dp.message(Command('stats'))
async def statistics_handler(message:Message):
	try:
		with open(BALANCE_FILE,'r')as f:data=json.load(f)
		total_users=len(data);await message.reply(f"всего: {total_users}")
	except FileNotFoundError:await message.reply('FileNotFound')
	except json.JSONDecodeError:await message.reply('json.JSONDecodeError')
	except Exception as e:await message.reply(f"EXCEPTION: {e}")
async def main():logging.basicConfig(level=logging.INFO);await dp.start_polling(bot)
if __name__=='__main__':
	try:asyncio.run(main())
	except KeyboardInterrupt:print('stopped')