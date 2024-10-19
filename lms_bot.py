from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.messages import SendMessageRequest
import sys
import os
import time
import random
import configparser

api_id = 23116062  # Вставьте свой API ID
api_hash = '17544c85de62cbffd75da6022e4372d8'  # Вставьте свой API HASH
bot_token = '7639773853:AAFXpSZ6rXUGOIMEeqDaDs3a_qNgvJgYTII'  # Вставьте свой токен бота

client = TelegramClient('anon', api_id, api_hash)
client.start(bot_token=bot_token)

# Словари для хранения данных
users = {}  # Словарь для хранения пользователей
courses = {}  # Словарь для хранения курсов
achievements = {} # Словарь для хранения достижений

# Обработчик команды "/start"
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        'Привет! Я бот-помощник для обучения.  '
        'Вы можете начать обучение, зарегистрироваться,  '
        'создать или присоединиться к курсу.'
    )
    await event.respond(
        'Напишите /help, чтобы узнать о доступных командах.'
    )

# Обработчик команды "/help"
@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.respond(
        'Список команд:\n'
        '/start - Начать работу\n'
        '/help - Получить справку\n'
        '/register - Зарегистрироваться\n'
        '/check_materials - Проверить материалы\n'
        '/create_course - Создать курс\n'
        '/join_course - Присоединиться к курсу\n'
        '/list_courses - Список курсов\n'
        '/take_quiz - Пройти тест\n'
        '/submit_task - Отправить задание\n'
        '/my_progress - Просмотреть свой прогресс\n'
        '/achievements - Просмотреть свои достижения\n'
        '/my_tokens - Просмотреть количество токенов\n' # Добавлена команда /my_tokens
        '/create_quiz - Создать квиз для курса (доступно только преподавателям)\n' # Добавлена команда /create_quiz
        '/add_question - Добавить вопрос в квиз (доступно только преподавателям)\n' # Добавлена команда /add_question
        '/check_quiz - Проверить результат прохождения квиза\n' # Добавлена команда /check_quiz
        '/create_task - Создать задание для курса (доступно только преподавателям)\n' # Добавлена команда /create_task
    )

# Обработчик команды "/register"
@client.on(events.NewMessage(pattern='/register'))
async def register_handler(event):
    user_id = event.message.from_id
    if user_id not in users:
        await event.respond('Какую роль вы хотите выбрать?  \n1. Студент\n2. Преподаватель')
        @client.on(events.NewMessage(pattern='1|2', incoming=True, from_users=user_id))
        async def choose_role(event):  # Добавлен from_users=user_id
            role = event.message.text
            if role == '1':
                users[user_id] = {
                    'role': 'student',
                    'courses': [],
                    'tokens': 0,  # Добавлено tokens: 0
                    'achievements': []
                }
                await event.respond('Вы успешно зарегистрированы как студент!')
            elif role == '2':
                users[user_id] = {
                    'role': 'teacher',
                    'courses': [],
                    'tokens': 0,  # Добавлено tokens: 0
                    'achievements': []
                }
                await event.respond('Вы успешно зарегистрированы как преподаватель!')
    else:
        await event.respond('Вы уже зарегистрированы.')

# Функция для отправки сообщений
async def send_message(user_id, message):
    try:
        await client.send_message(user_id, message)
    except PeerFloodError:
        print("Слишком много запросов. Попробуйте позже.")
    except UserPrivacyRestrictedError:
        print("Пользователь ограничил свой доступ.")
    except:
        print("Произошла ошибка отправки сообщения.")

# Обработчик команды "/create_course"
@client.on(events.NewMessage(pattern='/create_course'))
async def create_course_handler(event):
    user_id = event.message.from_id
    if users[user_id]['role'] == 'teacher':
        await event.respond('Введите название курса:')
        @client.on(events.NewMessage(incoming=True, from_users=user_id))
        async def get_course_name(event):
            course_name = event.message.text.strip()
            # Проверяем, что курс не является командой:
            if course_name not in courses and not course_name.startswith('/'):
                courses[course_name] = {
                    'description': '',
                    'materials': [],
                    'quizzes': [],
                    'tasks': []
                }
                await event.respond(f'Курс "{course_name}" успешно создан!')
                # Обновляем список курсов в ответе только если курс не /help
                if course_name != '/help':  # Добавлено условие
                    course_list = '\n'.join(courses.keys())
                    await event.respond(f'Список курсов:\n{course_list}')
            else:
                await event.respond(f'Некорректное название курса. Введите название, которое не является командой.')
    else:
        await event.respond('Только преподаватели могут создавать курсы.')

@client.on(events.NewMessage(pattern='/join_course'))
async def join_course_handler(event):
    user_id = event.message.from_id
    if courses:
        course_list = '\n'.join(courses.keys())
        await event.respond(f'Доступные курсы:\n{course_list}\nВыберите курс:')

        @client.on(events.NewMessage(incoming=True, from_users=user_id))
        async def choose_course(event):
            course_name = event.message.text.strip()
            if course_name in courses:
                if course_name not in users[user_id]['courses']:
                    users[user_id]['courses'].append(course_name)
                    await event.respond(f'Вы успешно присоединились к курсу "{course_name}"!')
                else:
                    await event.respond(f'Вы уже  зарегистрированы на курс "{course_name}"!')
            else:
                await event.respond(f'Курса "{course_name}" не существует.')
    else:
        await event.respond('Курсов пока нет.')

# Обработчик команды "/list_courses"
@client.on(events.NewMessage(pattern='/list_courses'))
async def list_courses_handler(event):
    if courses:
        course_list = '\n'.join(courses.keys())
        await event.respond(f'Список курсов:\n{course_list}')
    else:
        await event.respond('Курсов пока нет.')

# Обработчик команды "/check_materials"
@client.on(events.NewMessage(pattern='/check_materials'))
async def check_materials_handler(event):
    user_id = event.message.from_id
    course_name = event.message.text.replace('/check_materials', '').strip()
    if course_name in courses:
        if courses[course_name]['materials']:
            materials_list = '\n'.join(courses[course_name]['materials'])
            await event.respond(f'Материалы для курса "{course_name}":\n{materials_list}')
        else:
            await event.respond(f'Материалы для курса "{course_name}" ещё не добавлены.')
    else:
        await event.respond(f'Курса "{course_name}" не существует.')

# Обработчик команды "/create_quiz"
@client.on(events.NewMessage(pattern='/create_quiz'))
async def create_quiz_handler(event):
    user_id = event.message.from_id
    if users[user_id]['role'] == 'teacher':
        course_name = event.message.text.replace('/create_quiz', '').split()[0].strip()
        quiz_name = event.message.text.replace('/create_quiz', '').split()[1].strip()
        if course_name in courses and quiz_name not in courses[course_name]['quizzes']:
            courses[course_name]['quizzes'][quiz_name] = {
                'questions': [],
                'answers': []
            }
            await event.respond(f'Квиз "{quiz_name}" для курса "{course_name}" создан!')
        else:
            await event.respond('Ошибка создания квиза!')
    else:
        await event.respond('Только преподаватели могут создавать квизы.')

# Обработчик команды "/add_question"
@client.on(events.NewMessage(pattern='/add_question'))
async def add_question_handler(event):
    user_id = event.message.from_id
    if users[user_id]['role'] == 'teacher':
        course_name = event.message.text.replace('/add_question', '').split()[0].strip()
        quiz_name = event.message.text.replace('/add_question', '').split()[1].strip()
        question = event.message.text.replace('/add_question', '').split()[2].strip()
        answer = event.message.text.replace('/add_question', '').split()[3].strip()
        if course_name in courses and quiz_name in courses[course_name]['quizzes']:
            courses[course_name]['quizzes'][quiz_name]['questions'].append(question)
            courses[course_name]['quizzes'][quiz_name]['answers'].append(answer)
            await event.respond(f'Вопрос "{question}" добавлен в квиз "{quiz_name}" для курса "{course_name}"!')
        else:
            await event.respond('Ошибка добавления вопроса!')
    else:
        await event.respond('Только преподаватели могут добавлять вопросы.')

# Обработчик команды "/take_quiz"
@client.on(events.NewMessage(pattern='/take_quiz'))
async def take_quiz_handler(event):
    user_id = event.message.from_id
    course_name = event.message.text.replace('/take_quiz', '').split()[0].strip()
    quiz_name = event.message.text.replace('/take_quiz', '').split()[1].strip()

    if course_name in courses and quiz_name in courses[course_name]['quizzes']:
        quiz = courses[course_name]['quizzes'][quiz_name]
        # Вывод вопросов квиза
        for i, question in enumerate(quiz['questions']):
            await event.respond(f'{i+1}. {question}\n Ответ: ')

        # Ожидание ответов пользователя
        await event.respond('Введите ответы на вопросы через запятую, например: "ответ1, ответ2, ответ3".')
        await event.respond('Для проверки результатов введите /check_quiz')
    else:
        await event.respond('Ошибка')

# Добавить обработчик проверки результатов квиза:
@client.on(events.NewMessage(pattern='/check_quiz'))
async def check_quiz_handler(event):
    user_id = event.message.from_id
    course_name = event.message.text.replace('/check_quiz', '').split()[0].strip()
    quiz_name = event.message.text.replace('/check_quiz', '').split()[1].strip()

    if course_name in courses and quiz_name in courses[course_name]['quizzes']:
        quiz = courses[course_name]['quizzes'][quiz_name]
        user_answers = event.message.text.replace('/check_quiz', '').split()[2].strip().split(',')
        correct_answers = 0
        for i, answer in enumerate(quiz['answers']):
            if user_answers[i].strip() == answer:
                correct_answers += 1
        total_questions = len(quiz['questions'])
        await event.respond(f'Вы ответили правильно на {correct_answers} из {total_questions} вопросов.')
    else:
        await event.respond('Ошибка проверки квиза.')

# Обработчик команды "/create_task"
@client.on(events.NewMessage(pattern='/create_task'))
async def create_task_handler(event):
    user_id = event.message.from_id
    if users[user_id]['role'] == 'teacher':
        course_name = event.message.text.replace('/create_task', '').split()[0].strip()
        task_name = event.message.text.replace('/create_task', '').split()[1].strip()
        task_description = event.message.text.replace('/create_task', '').split()[2].strip()
        if course_name in courses and task_name not in courses[course_name]['tasks']:
            courses[course_name]['tasks'][task_name] = {
                'description': task_description,
                'submissions': []
            }
            await event.respond(f'Задание "{task_name}" для курса "{course_name}" создано!')
        else:
            await event.respond('Ошибка создания задания!')
    else:
        await event.respond('Только преподаватели могут создавать задания.')

# Обработчик команды "/submit_task"
@client.on(events.NewMessage(pattern='/submit_task'))
async def submit_task_handler(event):
    user_id = event.message.from_id
    course_name = event.message.text.replace('/submit_task', '').split()[0].strip()
    task_name = event.message.text.replace('/submit_task', '').split()[1].strip()
    submission = event.message.text.replace('/submit_task', '').split()[2].strip()

    if course_name in courses and task_name in courses[course_name]['tasks']:
        courses[course_name]['tasks'][task_name]['submissions'].append({
            'user_id': user_id,
            'submission': submission
        })
        users[user_id]['tokens'] += 10  # Начисление 10 токенов за задание
        await event.respond(f'Решение для задания "{task_name}"  в курсе "{course_name}" принято! Вам начислено 10 токенов.')
    else:
        await event.respond('Ошибка отправки решения.')

# Обработчик команды "/my_progress"
@client.on(events.NewMessage(pattern='/my_progress'))
async def my_progress_handler(event):
    user_id = event.message.from_id
    if 'courses' in users[user_id]:
        progress = []
        for course_name in users[user_id]['courses']:
            if course_name in courses:
                completed_quizzes = 0
                completed_tasks = 0
                if 'quizzes' in courses[course_name]:
                    for quiz_name in courses[course_name]['quizzes']:
                        if any(submission['user_id'] == user_id for submission in courses[course_name]['quizzes'][quiz_name].get('submissions', [])):
                            completed_quizzes += 1
                if 'tasks' in courses[course_name]:
                    for task_name in courses[course_name]['tasks']:
                        if any(submission['user_id'] == user_id for submission in courses[course_name]['tasks'][task_name].get('submissions', [])):
                            completed_tasks += 1
                progress.append(f'Курс "{course_name}": Квизы {completed_quizzes}/{len(courses[course_name].get("quizzes", []))}, Задания {completed_tasks}/{len(courses[course_name].get("tasks", []))}')
        if progress:
            await event.respond(f'Ваш прогресс: \n{"".join(progress)}')
        else:
            await event.respond('Вы ещё не прошли ни одного курса.')
    else:
        await event.respond('Вы ещё не зарегистрированы.')


# Обработчик команды "/achievements"
@client.on(events.NewMessage(pattern='/achievements'))
async def achievements_handler(event):
    user_id = event.message.from_id
    if 'achievements' in users[user_id]:
        if users[user_id]['achievements']:
            achievement_list = '\n'.join(users[user_id]['achievements'])
            await event.respond(f'Ваши достижения:\n{achievement_list}')
        else:
            await event.respond('У вас пока нет достижений.')
    else:
        await event.respond('Вы еще не зарегистрированы.')

# Обработчик команды "/my_tokens"
@client.on(events.NewMessage(pattern='/my_tokens'))
async def my_tokens_handler(event):
    user_id = event.message.from_id
    if 'tokens' in users[user_id]:
        await event.respond(f'У вас {users[user_id]["tokens"]} токенов.')
    else:
        await event.respond('Вы ещё не зарегистрированы.')

# Запуск бота
client.run_until_disconnected()