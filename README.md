# Telegram Request Bot 🤖

A Telegram bot for collecting and managing user requests/appeals. Users can submit requests, and admins receive them with the ability to ban users who violate the rules.

## 📋 Features

- **User Requests** — users can submit requests via a simple guided flow
- **Admin Notifications** — all requests are forwarded to configured admins
- **Ban System** — admins can ban/unban users directly from notifications or via commands
- **Ban Check** — check whether a user is banned
- **Spam Protection** — banned users cannot submit new requests

## 🚀 Setup

### Prerequisites

- Python 3.10+
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/wayrongod/requests-bot.git
   cd requests-bot
   ```

2. **Install dependencies**

   ```bash
   pip install python-telegram-bot
   ```

3. **Configure the bot**

   Open `main.py` and set the following values:

   ```python
   ADMINS = ["123456789"]  # Telegram user IDs of admins (as strings)
   ```

   And replace the bot token in `main()`:

   ```python
   application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()
   ```

4. **Run the bot**

   ```bash
   python main.py
   ```

## 🎮 Usage

### For Users

| Action | Description |
|--------|-------------|
| `/start` | Show the welcome message and a button to submit a request |
| **Send Request** | Click the inline button and follow the format described in the message |

### For Admins

| Command | Description |
|---------|-------------|
| `/ban <user_id>` | Ban a user by their Telegram ID |
| `/unban <user_id>` | Unban a previously banned user |
| `/check <user_id>` | Check if a user is banned |
| **Ban button** | Each incoming request includes a "Забанить" button to ban the sender instantly |

## 📁 Project Structure

```
.
├── main.py       # Bot source code
└── README.md     # This file
```

## ⚠️ Notes

- `BANNED_USERS` is stored **in memory only** — bans are lost when the bot restarts. For production use, consider persisting bans to a database (e.g. SQLite, PostgreSQL).
