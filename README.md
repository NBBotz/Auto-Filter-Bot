<p align="center">
  <img src="https://github.com/NBBotz/Images/blob/main/Lucia-Filter-Bot.jpeg">
</p>

<h1 align="center">Lucia Filter Bot</h1>

<p align="center">
  <a href="https://t.me/SilentXBotz">
    <img src="https://img.shields.io/badge/Join-Support%20Group-blue?style=for-the-badge&logo=telegram">
  </a>
  <a href="http://t.me/Lucia_Filter_Bot">
    <img src="https://img.shields.io/badge/Demo%20Bot-Click%20Here-green?style=for-the-badge&logo=telegram">
  </a>
</p>

---

## Features  

- ✅ Supports Double Databases (Auto-Switch When Primary DB Is Running Low.)  
- 🔍 Fast And Efficient File Searching With Pagination  
- 📂 Saves And Retrieves Files.  
- 🚀 Optimized For Performance And Low Resource Usage  
- 🛡️ 3 Verification Method 
- 🤖 Custom Force Subscription For Group Owners
- 📊 Full Customisable. 
- 🔄 Latest Features.
- 📺 Best Streaming Site.
- 📥 Top Trending & Refer Feature.
- 👑 Premium Subscription Funtion.
- 📌 Premium Expired Reminder.
- 🔥 Telegram Star Payment Method

# New Version Released - V4.2
- Now Group Owners Change There All Settings From Callback Button ✅
- Group Owners Can Manage Groups From Bot PM.
- Added /reload Command 
- UI Change
- New Channel Update Theme
- Added Support Of Streming Only For Premium Users
- Now Owner Can Reset All Connect Groups Settings 


## Variables
* `BOT_TOKEN`: Create A Bot Using [@BotFather](https://telegram.dog/BotFather), and get the Telegram API token.
* `API_ID`: Get This Value From [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get This Value From [telegram.org](https://my.telegram.org/apps)
* `ADMINS`: ID Of Admins. (Multiple admins can be used separated by space)
* `DATABASE_URI`: Your First MongoDB URL. Get This Value From [MongoDB](https://www.mongodb.com).
* `MULTIPLE_DB`: Set It True Or False. If You Set This True Then All Files Saved In Second MongoDB If First MongoDB 80MB Left.
* `DATABASE_URI2`: Your Second MongoDB URL (Optional - Add This If You Set MULTIPLE_DB True.).
* `LOG_CHANNEL` : A Channel To Log The Activities Of Bot. Add Channel Id And Make Sure Bot Is An Admin In The Channel.
* `SUPPORT_GROUP`: Add Your Support Group Id In This Veriable.
* `BIN_CHANNEL`: A Channel To The Stream And Download Feature, Add Channel Id And Make Bot Admin In Channel.
* `FQDN`: Make A Veriable On Your Deploying Plartform AndAdd You Deployed Bot App Link
* `AUTH_CHANNEL`: ID of force subscribe channels (Multiple channels can be used separated by space)
* `CHANNELS`: Username or ID of your files channels (Multiple channels can be used separated by space)
*  Before Deploying The Bot Fill All Veriables. Check [info.py](https://github.com/NBBotz/Auto-Filter-Bot/blob/SilentXBotz/info.py) For All Veriables.


## 🤖 Bot Commands

### 👤 General Commands
- `/start` - Start the bot
- `/myplan` - Check your premium plan status
- `/plan` - View available premium plans
- `/redeem` - Redeem a premium code
- `/alive` - Check if the bot is active
- `/ping` - Check bot latency
- `/system` - View system statistics
- `/top_search` - View top searched queries
- `/trendlist` - View trending search list
- `/movies` - List recent movies
- `/series` - List recent series
- `/id` - Get your User ID or Chat ID
- `/info` - Get detailed user information

### 👥 Group Commands
- `/settings` - Open settings menu (Group Admin only)
- `/reload` - Reload group connection (Group Admin only)
- `/details` - View current group settings
- `/request` or `#request` - Request a movie or series
- `/reset_group` - Reset group settings to default (Group Admin only)

### 🛠 Admin Commands
- `/logs` - Get the bot log file
- `/delete` - Delete a file from the database
- `/deleteall` - Delete all indexed files
- `/send` - Send a message to a specific user
- `/deletefiles` - Delete multiple files by keyword
- `/pm_search` - Enable/Disable PM search
- `/movie_update` - Enable/Disable movie update notifications
- `/maintenance` - Enable/Disable maintenance mode
- `/restart` - Restart the bot
- `/admin_cmd` - Show all admin commands
- `/resetall` - Reset settings for all groups
- `/dropgroups` - Drop the groups collection
- `/remove_premium` - Remove premium status from a user
- `/get_premium` - Get premium user details
- `/add_premium` - Add premium status to a user
- `/premium_users` - List all premium users
- `/setskip` - Set skip count for indexing
- `/delreq` - Delete join requests
- `/add_redeem` - Create a redeem code
- `/clearcodes` - Clear all redeem codes
- `/allcodes` - List all redeem codes
- `/commands` - Show command list
- `/leave` - Leave a specific chat
- `/disable` - Disable the bot in a chat
- `/enable` - Enable the bot in a chat
- `/stats` - View bot statistics
- `/invite` - Generate an invite link
- `/ban` - Ban a user
- `/unban` - Unban a user
- `/users` - List all users
- `/chats` - List all chats
- `/broadcast` - Broadcast a message to all users
- `/grp_broadcast` - Broadcast a message to all groups
- `/clear_junk` - Clear junk data
- `/junk_group` - Clear junk groups

## 🚀 Deployment Methods

Choose A Deployment Method Below And Get Your Bot Running Instantly!  

<details>
  <summary><b>Heroku</b></summary>  

Click The Button Below To Instantly Deploy Your Bot On **Heroku**.  

<p align="center">
  <a href="https://heroku.com/deploy?template=https://github.com/NBBotz/Auto-Filter-Bot">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy on Heroku">
  </a>
</p>

</details>

<details>
  <summary><b>Koyeb</b></summary>  

Deploy On **Koyeb** In One Click!  

<p align="center">
  <a href="https://app.koyeb.com/deploy?type=git&repository=https://github.com/NBBotz/Auto-Filter-Bot&branch=SilentXBotz &name=LuciaFilterBot">
    <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb">
  </a>
</p>


</details>

<details>
  <summary><b>VPS</b></summary>  

Run The Following Commands To Deploy The Bot On A **VPS**:  

```bash
mkdir SilentXBotz && cd SilentXBotz
git clone https://github.com/NBBotz/Auto-Filter-Bot
cd Auto-Filter-Bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 bot.py
```
</details>


# ! Errors 
- This Repository May Contain Some Errors. If You Encounter Any Issues, Please Let Us Know, And We Will Do Our Best To Resolve Them.
<p align="center">
  <a href="https://t.me/SilentXBotz">
    <img src="https://img.shields.io/badge/Report-Error-red?style=for-the-badge&logo=telegram" alt="Report Error">
  </a>
</p>
  

# 📌 Credits  

- **Base Repository:** [ᴅʀᴇᴀᴍxʙᴏᴛᴢ](https://github.com/DreamXBotz/Auto_Filter_Bot.git)
- **Thank You To All [Contributors](https://github.com/NBBotz/Auto_Filter_Bot/graphs/contributors) For Your Valuable Contributions To This Repository!**


# Bugs & Fixes  

**If You Find Any Bugs Or Errors In This Project, Feel Free To Fix Them And Submit A Pull Request. Contributions Are Always Welcome!**  

## Disclaimer

This Repository Is Provided For Educational Purposes Only. It Is Not Intended For Personal Or Commercial Gain. Use Of This Repository And The Code Within Is At Your Own Risk. The Authors And Contributors Are Not Responsible For Any Misuse Or Damage Caused By The Use Of This Project.

## License

This Project Is Licensed Under The [GNU General Public License v3.0](https://github.com/NBBotz/Auto-Filter-Bot/blob/SilentXBotz/LICENSE)

