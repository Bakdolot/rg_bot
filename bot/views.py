from django.conf import settings
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.response import Response
from telebot import types
import telebot
from .models import *


bot = telebot.TeleBot(settings.TOKEN, threaded=False)


class MainView(generics.GenericAPIView):

    def post(self, request):
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return Response(status=status.HTTP_200_OK)


class TaskHandler(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        user = generics.get_object_or_404(User.objects.all(), id=kwargs.get('user_id'))
        task = generics.get_object_or_404(Task.objects.filter(status=True).exclude(complite_users=user), url_id=kwargs.get('url_id'))
        if task.bon > 0:
            user.balance += 1
            task.bon -= 1
            task.complite_users.add(user)
            user.save()
            task.save()
        return redirect(task.url)


@bot.message_handler(commands=['start'])
def start(request):
    chat_id = request.chat.id
    user_id = request.from_user.id
    username = request.from_user.username
    user = User.objects.get_or_create(
        username=username,
        user_id=user_id,
        chat_id=chat_id
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('balance'))
    markup.add(types.KeyboardButton('payment'))
    markup.add(types.KeyboardButton('tasks'))
    markup.add(types.KeyboardButton('complete tasks'))
    bot.send_message(chat_id, "Вас приветствует бот созданный компанией Oracle Digital!".format(
        request.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'balance')
def check_balance(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    bot.send_message(chat_id, f'Ваш баланс: {user.balance} KGS')


@bot.message_handler(func=lambda message: message.text == 'payment')
def payment(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    bot.send_message(chat_id, f'Ваш баланс: {user.balance} KGS')
    msg = bot.reply_to(message, 'Введите сумму вывода')
    bot.register_next_step_handler(msg, cash_withdrawal)


def cash_withdrawal(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    try:
        amount = int(message.text)
        if user.balance >= amount:
            pay = Payment.objects.create(
                user=user,
                amount=amount
            )
            msg = bot.reply_to(message, 'Введите номер телефона')
            bot.register_next_step_handler(msg, number, pay.id)
        else:
            bot.send_message(chat_id, 'Недостаточно средств для вывода')
    except:
        bot.send_message(chat_id, 'Не верный формат ввода')


def number(message, pay_id):
    chat_id = message.chat.id
    pay = Payment.objects.get(id=pay_id)
    pay.phone = message.text
    pay.save()
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Правильно', callback_data='pay_yes'),
        types.InlineKeyboardButton('Не правильно', callback_data=f'pay_no{pay.id}')
    )
    bot.send_message(chat_id, f'Убедитесь в верности телефона:\nТелефон: {pay.phone}', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'pay_no' in call.data)
def pay_no(message):
    pay_id = int(message.data.split('no')[-1])
    msg = bot.reply_to(message.message, 'Введите номер телефона')
    bot.register_next_step_handler(msg, number, pay_id)


@bot.callback_query_handler(func=lambda call: call.data == 'pay_yes')
def pay_yes(message):
    bot.send_message(
        message.message.chat.id, 'Ваша заявка успешно отправлено администратору, они посмотрят заявку в ближащее время')


@bot.message_handler(func=lambda message: message.text == 'tasks')
def payment(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    tasks = Task.objects.filter(status=True, bon__gt=0).exclude(complite_users=user)[:5]
    if tasks:
        text = ''.join([f'Задание: {task.text}\nСылка: {settings.PROJECT_URL}/{user.id}/{task.url_id}\n\n\n' for task in tasks])
        bot.send_message(chat_id, 'Доступные задании\n'+text)
    else:
        bot.send_message(chat_id, 'Нет доступных заданий')


@bot.message_handler(func=lambda message: message.text == 'complete tasks')
def payment(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    tasks = Task.objects.filter(status=True, complite_users=user)[:5]
    if tasks:
        text = ''.join([f'Задание: {task.text}\nСылка: {settings.PROJECT_URL}/{user.id}/{task.url_id}\n\n\n' for task in tasks])
        bot.send_message(chat_id, 'Законченные задании\n'+text)
    else:
        bot.send_message(chat_id, 'Нет законченных заданий')
