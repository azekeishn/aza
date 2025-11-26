import telegram
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import re

# ЗАМЕНИТЕ ЭТОТ ТОКЕН НА ВАШ ТОКЕН БОТА
TOKEN = '8478772342:AAFrpKocZDAGJV6W5z6kq0rEKov1tgG7wL4'

# --- Вспомогательная функция для извлечения данных ---
def extract_value(text, keyword):
    """Извлекает числовое значение после указанного ключевого слова (keyword: 12345)."""
    # Ищет ключевое слово, двоеточие, необязательный пробел, и одну или более цифр.
    match = re.search(f"{keyword}:\\s*(\\d+)", text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1).replace(' ', ''))
        except ValueError:
            return 0
    return 0

# --- Вспомогательная функция для форматирования чисел ---
def format_num(num):
    """Форматирует число с разделителем тысяч."""
    # В HTML не нужно экранировать запятую
    return f"{num:,}"

# --- Главный обработчик сообщений ---
async def check_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текст отчета и выполняет проверку сумм."""
    report_text = update.message.text
    
    # 1. Извлечение данных
    itogo_kassa = extract_value(report_text, "Итого касса за день")
    kaspi_qr = extract_value(report_text, "Каспи qr")
    narodny_qr = extract_value(report_text, "Народный qr")
    nalichka = extract_value(report_text, "Наличка")
    chaevye = extract_value(report_text, "Чаевые")
    chaevye_ot_sertifikata = extract_value(report_text, "Чаевые от сертификата")
    
    # 2. Расчет общей суммы поступлений
    summa_postupleniy = (
        kaspi_qr +
        narodny_qr +
        nalichka +
        chaevye +
        chaevye_ot_sertifikata
    )
    
    # 3. Формирование ответа в режиме HTML
    
    if itogo_kassa == 0 and summa_postupleniy == 0:
        # Используем <b> теги для жирного шрифта
        response = "<b>🚫 Ошибка: Не удалось найти числовые данные 'Итого касса' и/или данные о поступлениях. Убедитесь, что формат отчета точен.</b>"
        
    elif summa_postupleniy == itogo_kassa:
        # Отчет принят
        itogo_kassa_str = format_num(itogo_kassa)
        summa_postupleniy_str = format_num(summa_postupleniy)

        response = (
            "✅ <b>Отчет принят!</b>\n\n"
            f"💰 Итого касса: <b>{itogo_kassa_str}</b>\n"
            f"🧮 Сумма поступлений: <b>{summa_postupleniy_str}</b>\n"
            "Сумма поступлений совпадает с итоговой кассой."
        )
        
    else:
        # Отчет не принят (есть разница)
        raznica = abs(itogo_kassa - summa_postupleniy)
        status = "недостача" if summa_postupleniy < itogo_kassa else "излишек"
        
        itogo_kassa_str = format_num(itogo_kassa)
        summa_postupleniy_str = format_num(summa_postupleniy)
        raznica_str = format_num(raznica)
        
        response = (
            "❌ <b>Отчет НЕ принят!</b>\n\n"
            f"💰 Итого касса: <b>{itogo_kassa_str}</b>\n"
            f"🧮 Сумма поступлений: <b>{summa_postupleniy_str}</b>\n"
            f"⚠️ <b>Разница: {raznica_str} ({status}).</b>"
        )
    
    # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Используем ParseMode.HTML
    await update.message.reply_text(response, parse_mode=telegram.constants.ParseMode.HTML)

# --- Функция запуска бота ---
def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    # Обработчик: реагирует на ЛЮБОЙ текстовый ввод (кроме команд)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_report))

    print("Бот запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
