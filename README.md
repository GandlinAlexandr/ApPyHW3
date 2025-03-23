<a name="readme-top"></a>

[![MIT][license-shield]][license-url]
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[!['Black'](https://img.shields.io/badge/code_style-black-black?style=for-the-badge)](https://github.com/psf/black)


  <h1 align="center">Фитнес-бот</h1>

  <p align="center">
    Телеграм бот в рамках домашней работы по дисциплине "Прикладное программирование на Python"
  </p>


<details>
  <summary>Содержание</summary>
  <ol>
    <li>
      <a href="#о-проекте">О проекте</a>
        <li><a href="#технологии">Технологии</a></li>
    </li>
    <li>
      <a href="#содержание-проекта">Содержание проекта</a>
    </li>
    <ul>
    <li><a href="#предоставляемые-функции">Предоставляемые функции</a></li>
    <li><a href="#команды">Команды</a></li></ul>
    <li><a href="#деплой">Деплой</a></li></ul>
    <li><a href="#примеры-использования">Примеры использования</a></li>
      <li><a href="#лицензия">Лицензия</a></li>
    <li><a href="#контакты">Контакты</a></li>
  </ol>
</details>


### О проекте

Представляет собой телеграм-бот, отслеживающий активность, потребление воды и калорий пользователем.

## Технологии

Для реализации проекта использовались следующие технологии:
* [![Docker][DockerBadge]][Docker-url]
* [![Python][Python.org]][Python-url]
  * [![AIOgram][AIOgram]][AIOgram-url]
  * [![Matplotlib][Matplotlib.org]][Matplotlib-url]
  * [![Pandas][Рandas.pydata.org]][Pandas-url]
  * [![Seaborn][Seaborn-badge]][Seaborn-url]
* [![telegram][telegram]][telegram-url]


<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Содержание проекта

Содержит телеграм-бот, а также всё необходимое (за исключением кличей) для его развёртывания, включая Докер-файл для создания образа. Код разбит на несколько файлов:
* `API.py` - содержит код для взаимодействия с API
* `bot.py` - осноаа бота, содержащая диспетчер и функцию запуска
* `calculations.py` - код, содержащий вычисления показателей и построение графиков
* `config.py` - код, импортирующий ключи из `.env`
* `handlers.py` - основная часть бота, содержащая все хэндлеры. Сюда импортируются все остаольные файлы и функции из них
* `states.py` - небольшой файл, содержащий состояния. Необходим для конструирования форм для заполнения и для связывания некоторых функций и хэндлеров между собой

Данные пользователей хранит в памяти. Никакие базы данных пока не подключены.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>


### Предоставляемые функции

Бот предоставляет пользователю возможность создать аккаунт, содержащий следующие параметры:
* Вес (кг)
* Рост (см)
* Возраст (лет)
* Активность в день (мин)
* Город
* Цель по калориям (ккал) - расчитывается автоматически или указывается пользователем
* Норма воды (мл) - расчитывается автоматически
* Выпито воды (мл) - логгирутся на основе отчёта пользователя
* Потреблено калорий (ккал) - логгирутся на основе отчёта пользователя
* Сожжено калорий (ккал) - логгирутся на основе отчёта пользователя

Соответсвенно, бот ведёт журнал посуточных активностей пользователя, если тот ведёт отчёт. Норму воды формирует на основе веса, активности и текущей температуры в городе проживвания, извлекаемой в реальном времени посредством [Weather API](https://openweathermap.org/api). Рассчёт нормы воды производится по формуле:

$$
N_w =
\begin{cases}
\text{если } t\leq25,\quad 30\cdot w + 500\cdot \frac{a}{30}\\
\text{если } t>25,\quad 30\cdot w + 500\cdot \frac{a}{30} + 500
\end{cases},
$$

где $t$ - текущая температура в городе в °C, $w$ - вес пользователя в кг, $a$ - время активности в мин.

Цель по калориям расчитывалась следующим образом:

$$
N_с = 10 \cdot w + 6.25 \cdot h − 5 \cdot y,
$$

где $w$ - вес пользователя в кг, $h$ - рост пользователя в см, $y$ - возраст пользователя в годах.

Потребляемое и сжигаемое количество калорий расчитывается на основе указаний съеденой пищи и проведённых тренировок посредством запросов к [Nutritionix  API](https://www.nutritionix.com/). Данный API значительно лучше выполняет логирование пищи, чем данный в задании API, так как способен обрабатывать запросы, схожие по смыслу, а не обязательно полностью совпадающие с имеющимися наименованиями продуктов. К тому же, в случае активностей, значительно расширяется их набор, ввиду того, что в данном API представлены не только спортивные, но и ежедневные активности. Для обработки русскоязычных запросов используется [API Google Translate](https://cloud.google.com/translate/docs/reference/rest). Также выводит графики прогресса достиженния норм по калориям и воде, графики по калориям и воде за последние 10 дней активности пользователя (было решено показывать 10 последних дней для адекватных масштабов графиков, при желании в коде это можно изменить или вовсе позволить указывать пользователю).

Также выводит рекомендации:
* Если [индекс массы тела (ИМТ)](https://en.wikipedia.org/wiki/Body_mass_index) пользователя в норме - пишет, что рекоимендации излишни.
* Если ИМТ выходит за рамки нормы, то в случае превышения предлагает случайные низкокалорийные продукты через API по запросу `low calorie`. Если ИМТ ниже нормы - предлагает врача (ну а что делать, упражнениями тут не помочь, а советовать излишне калорийные продукты - это возможность навредить здоровью. А поход к врачу навредить не должен... теоретически).

Советы на основе ИМТ не следует воспринимать всерьез, так как ИМТ - часто ненадёжный и спорный показатель, а поиск низкокалорийных продуктов через API крайне ограничен.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>


### Команды

Команды, не требующие ввода параметров одновременно с ними (такие команды представлены в меню быстрого доступа в чате):
* `/start` - Начало работы
* `/help` - Помощь
* `/set_profile` - Заполнение формы для создания профиля. При создании нового старый профиль удаляется
* `/my_propfile` - Посмотреть свой профиль
* `/check_progress` - Показывает, сколько воды и калорий потреблено, сожжено и сколько осталось до выполнения цели на текущие сутки. Выводит соотвествующие диаграммы
* `/recomend` - Выдаёт рекомендации на основе ИМТ
* `/global_progress` - Выводит график глобального прогресса за последние 10 дней активности в чате бота
* `/edit_profile` - Позволяет изменить параметры профиля, не удаляя его и сохраняя историю

Команды с параметрами:
* `/log_water` <количество воды в мл> - Добавляет количество выпитой воды в ваш профиль и рассчитывает количество воды до нормы
* `/log_food` <название продукта> - Рассчитывает количество поглощённых калорий по названию блюда и добавляет в профиль
* `/log_workout` <тип тренировки> <время (мин)> - Фиксирует сожжённые калории и учитывает расход воды на тренировке


<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

### Деплой


Развёртывание телеграм-бота осуществлено на инфраструктурной платформе [Railway](https://railway.com/) с тарифным планом Trial.

<div align="center">
  <img src="https://github.com/user-attachments/assets/e7b8e974-1601-4252-b65e-b24f62dddcf4">
  <p><i>Успешное развёртывание на <a href="https://railway.com/" target="_blank">Railway</a></i></p>
</div>

Ниже представлены скриншоты логов.

<div align="center">
  <img src="https://github.com/user-attachments/assets/433d8d12-c527-48d7-8db7-913aa004449f">
  <p><i>Build Logs на <a href="https://railway.com/" target="_blank">Railway</a></i></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/411a4981-9705-40c8-8240-3885c0311aa7">
  <p><i>Deploy Logs на <a href="https://railway.com/" target="_blank">Railway</a></i></p>
</div>


<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Примеры использования

Основные команды.

<div align="center">
  <img src="https://github.com/user-attachments/assets/2fc22a66-7a0d-4f0c-b2a6-bdac7e125d2c" alt="1">
  <p><i>Команды <code>/start</code>, <code>/help</code>, <code>/set_profile</code>, <code>/my_profile</code></i></p>
</div>

Команды, связанные с логированием.

<div align="center">
  <img src="https://github.com/user-attachments/assets/cf1b6122-07fc-476a-9f0a-80eef97ce0df" alt="2">
  <p><i>Команды <code>/log_water</code>, <code>/log_food</code>, <code>/log_workout</code>, <code>/my_profile</code>,  <code>/recomend</code>, <code>/check_progress</code></i></p>
</div>

Команда редактирования профиля без его удаления:

<div align="center">
  <img src="https://github.com/user-attachments/assets/407c324a-1b50-46ca-8c1e-0c56447416a5" alt="3">
  <p><i>Команды <code>/edit_profile</code>, <code>/my_profile</code></i></p>
</div>

Команда, выдающая графики прогресса по дням (максимум за 10 последних дней).

<div align="center">
  <img src="https://github.com/user-attachments/assets/f6994871-6b7f-4ec1-b849-5db52ddb84da" alt="4">
  <p><i>Команда <code>/global_progress</code></i></p>
</div>

Ниже приведены примеры обработки неверных вводов.

<div align="center">
  <img src="https://github.com/user-attachments/assets/a7988940-f658-4af9-9eb7-a2163196d13b" alt="5">
  <p><i>Примеры обработки неверных вводоов</a></i></p>
</div>

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Лицензия

Распространяется по лицензии MIT. Дополнительную информацию см. в файле [`LICENSE`][license-url].

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Контакты

Гандлин Александр - [Stepik](https://stepik.org/users/79694206/profile)

Ссылка на проект: [https://github.com/GandlinAlexandr/ApPyHW2](https://github.com/GandlinAlexandr/ApPyHW3)

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>




[license-shield]: https://img.shields.io/github/license/GandlinAlexandr/ApPyHW3.svg?style=for-the-badge
[license-url]: https://github.com/GandlinAlexandr/ApPyHW3/blob/main/LICENSE

[Python-url]: https://python.org/
[Python.org]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue

[Pandas-url]: https://pandas.pydata.org/
[Рandas.pydata.org]: https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white

[Matplotlib-url]: https://matplotlib.org/
[Matplotlib.org]: https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black

[Seaborn-url]: https://seaborn.pydata.org/
[Seaborn-badge]: https://img.shields.io/badge/Seaborn-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=blue

[telegram-url]: https://telegram.org/
[telegram]: https://img.shields.io/badge/Telegram-grey?style=for-the-badge&logo=telegram

[AIOgram-url]: https://aiogram.dev/
[AIOgram]: https://img.shields.io/badge/AIOgram-blue?style=for-the-badge&logo=aiogram

[DockerBadge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
