import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعداد Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("اسم_ملف_جوجل_شيت").sheet1

# تحديد مراحل المحادثة
NAME, PHONE, DESTINATION, RECEIVER_NAME, RECEIVER_PHONE, AMOUNT = range(6)

# قم بتعيين التوكن مباشرةً
token = '7414132297:AAHYezdC15EsmdSzuXd5d8I6V_sbkn73YUg'

# بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("تسجيل الطرد", callback_data='register')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('اختر أحد الخيارات:', reply_markup=reply_markup)

# معالجة الضغط على زر "تسجيل الطرد"
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="الرجاء إدخال اسم المرسل:")
    return NAME

# استقبال اسم المرسل
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("الرجاء إدخال رقم هاتف المرسل:")
    return PHONE

# استقبال رقم هاتف المرسل
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("الرجاء إدخال الوجهة:")
    return DESTINATION

# استقبال الوجهة
async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['destination'] = update.message.text
    await update.message.reply_text("الرجاء إدخال اسم المستلم:")
    return RECEIVER_NAME

# استقبال اسم المستلم
async def receiver_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['receiver_name'] = update.message.text
    await update.message.reply_text("الرجاء إدخال رقم هاتف المستلم:")
    return RECEIVER_PHONE

# استقبال رقم هاتف المستلم
async def receiver_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['receiver_phone'] = update.message.text
    await update.message.reply_text("الرجاء إدخال مبلغ الطرد:")
    return AMOUNT

# استقبال مبلغ الطرد وتسجيل البيانات
async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text

    # إدخال البيانات في Google Sheets
    data = [
        context.user_data['name'],
        context.user_data['phone'],
        context.user_data['destination'],
        context.user_data['receiver_name'],
        context.user_data['receiver_phone'],
        context.user_data['amount'],
    ]
    sheet.append_row(data)

    await update.message.reply_text("تم تسجيل الطرد بنجاح!")
    return ConversationHandler.END

# إلغاء المحادثة
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('تم إلغاء العملية.')
    return ConversationHandler.END

# الإعداد الرئيسي للبوت
async def main():
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
            RECEIVER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receiver_name)],
            RECEIVER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receiver_phone)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # بدء التطبيق
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
