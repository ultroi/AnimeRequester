import telebot
import requests

# Replace with your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to upload the image to Telegra.ph
def upload_to_telegraph(file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(
            "https://telegra.ph/upload",
            files={"file": ("file", file, "image/jpeg")}
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "src" in result[0]:
                return f"https://graph.org{result[0]['src']}"
        return None

# Handler for images and documents
@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    # Handle photos
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    # Handle documents (assuming it's an image file)
    elif message.content_type == 'document':
        file_id = message.document.file_id
    else:
        bot.reply_to(message, "Unsupported file type.")
        return

    # Get file info and download it
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)
    
    # Save the file locally
    local_file = f"temp_{file_id}.jpg"
    with open(local_file, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Upload to Telegra.ph
    link = upload_to_telegraph(local_file)
    if link:
        bot.reply_to(message, f"Your image has been uploaded: {link}")
    else:
        bot.reply_to(message, "Failed to upload the image. Please try again.")

    # Clean up the local file
    import os
    if os.path.exists(local_file):
        os.remove(local_file)

# Start the bot
bot.polling()
