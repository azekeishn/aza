import telebot
import re
import os

# ЗАМЕНИТЕ НА ВАШ ТОКЕН БОТА
TOKEN = os.environ.get("8478772342:AAFrpKocZDAGJV6W5z6kq0rEKov1tgG7wL4") 
if not TOKEN:
    print("Ошибка: Токен бота не найден в переменной окружения BOT_TOKEN.")
    exit()

bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИЯ ДЛЯ ПРОВЕРКИ ОТЧЕТА ---
def check_report_logic(report_text):
    data = {}
    
    # Поля, которые должны составить сумму (Слагаемые)
    fields_to_sum = {
        "Каспи qr": "kaspi_qr",
        "Народный qr": "narodniy_qr",
        "Наличка": "cash",
        "Чаевые": "tips",
        "Продажи по бару": "bar_sales",
        "Продажа косметика": "cosmetic_sales"
    }
    
    # Проверяемое поле (Фактический итог)
    total_field = "Итого касса за день"

    try:
        # Извлечение всех нужных значений
        for key_phrase, var_name in fields_to_sum.items():
            # Регулярное выражение для поиска числа после фразы
            match = re.search(fr"{key_phrase}:\s*(\d+)", report_text)
            # Если поле найдено, берем число, иначе считаем 0
            data[var_name] = int(match.group(1).replace(',', '')) if match else 0
            
        # Извлечение фактической общей кассы
        match_total = re.search(fr"{total_field}:\s*(\d+)", report_text)
        total_actual = int(match_total.group(1).replace(',', '')) if match_total else None

    except Exception as e:
        # Ошибка, если парсинг не удался (например, нет нужных строк)
        print(f"Ошибка парсинга: {e}")
        return "⚠️ **Ошибка парсинга.**"


    if total_actual is None:
         return "⚠️ **Ошибка парсинга.** Не найдена строка 'Итого касса за день'."

    # Вычисление ожидаемой суммы (формула, которую Вы дали)
    total_expected = (
        data['kaspi_qr'] + data['narodniy_qr'] + data['cash'] + data['tips'] + 
        data['bar_sales'] + data['cosmetic_sales']
    )

    # --- Проверка и формирование ответа ---
    if total_actual == total_expected:
        return f"✅ **Отчет принят!** Все суммы сошлись: {total_actual:,} ₸."
    else:
        difference = total_actual - total_expected
        return (
            "❌ **Отчет НЕ принят!** Сверка не сошлась.\n\n"
            f"**Фактическая касса:** {total_actual:,} ₸\n"
            f"**Ожидаемая касса (по формуле):** {total_expected:,} ₸\n"
            f"**Разница (Недостача/Излишек):** {difference:+,} ₸"
        )


# --- ОБРАБОТЧИКИ TELEGRAM-СООБЩЕНИЙ ---

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправьте мне отчет по установленному шаблону, и я проверю его.")

# Обработчик ВСЕХ текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Отправляем текст отчета в нашу логику проверки
    result_message = check_report_logic(message.text)
    
    # Отправляем результат обратно пользователю
    bot.send_message(
        message.chat.id, 
        result_message, 
        parse_mode="Markdown" # Используем Markdown для жирного текста и эмодзи
    )

# Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)



