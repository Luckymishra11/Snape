from info import *
from utils import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.group & filters.command("verify"))
async def _verify(bot, message):
    try:
       group     = await get_group(message.chat.id)
       user_id   = group["user_id"] 
       user_name = group["user_name"]
       verified  = group["verified"]
    except:     
       return await bot.leave_chat(message.chat.id)  
    try:       
       user = await bot.get_users(user_id)
    except:
       return await message.reply(f"❌ {user_name} Need to start me in PM!")
    if message.from_user.id != user_id:
       return await message.reply(f"Only {user.mention} can use this command 😁")
    if verified==True:
       return await message.reply("This Group is already verified!")
    try:
       link = (await bot.get_chat(message.chat.id)).invite_link
    except:
       return message.reply("❌ Make me admin here with all permissions!")    
    
     
    members_count = await bot.get_chat_members_count(chat_id=message.chat.id)       
    text  = f"#NewRequest\n\n"
    text += f"Requested By: {message.from_user.mention}\n"
    text += f"User ID: `{message.from_user.id}`\n"
    text += f"Group: [{message.chat.title}]({link})\n"
    text += f"Group ID: `{message.chat.id}`\n"
    text += f"Total Members: `{members_count}`\n"
   
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"verify_approve_{message.chat.id}"),
             InlineKeyboardButton("❌ Decline", callback_data=f"verify_decline_{message.chat.id}")],
            [InlineKeyboardButton("👀 View Group", url=f"{link}")],
            [InlineKeyboardButton("📣 Send Alert", callback_data=f"verify_alert_{message.chat.id}")]
        ]
    )
    await bot.send_message(chat_id=LOG_CHANNEL,
                           text=text,
                           disable_web_page_preview=True,
                           reply_markup=keyboard) 
    await message.reply("Verification Request sent ✅\nWe will notify You Personally when it is approved")



@Client.on_callback_query(filters.regex(r"^verify"))
async def verify_(bot, update):
    id = int(update.data.split("_")[-1])
    group = await get_group(id)
    name  = group["name"]
    user  = group["user_id"]
    if update.data.split("_")[1]=="approve":
       await update_group(id, {"verified":True})
       await bot.send_message(chat_id=user, text=f"Your verification request for {name} has been approved ✅")
       await update.message.edit(update.message.text.html.replace("#NewRequest", "#Approved"))
    elif update.data.split("_")[1]=="alert":
       await update.callback_query.message.edit_reply_markup(reply_markup=None)
       await bot.send_message(chat_id=update.callback_query.message.chat.id,
                              text="Please enter the custom message you want to send to the group.")
       await bot.register_callback_query(answer_callback_query_id=update.id)
    else:
       await delete_group(id)
       await bot.send_message(chat_id=user, text=f"Your verification request for {name} has been declined 😐 Please Contact Admin")
       await update.message.edit(update.message.text.html.replace("#NewRequest", "#Declined"))
