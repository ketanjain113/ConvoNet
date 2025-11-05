# 💬 ConvoNet

**ConvoNet** is a real-time chatroom application built with **Django**, **MongoDB**, and **WebSockets**, designed for seamless interaction.
It supports **login & authentication**, **friend-based DMs**, and **room-based conversations** where users can join using a **room name**.
An integrated **encryption layer** ensures secure communication between users.

---

## 🚀 Features

### 🔐 Authentication & User Management

* Secure login and signup system
* Persistent user sessions
* User profiles stored in MongoDB

### 💬 Chat System

* Real-time messaging using Django Channels or WebSockets
* Room-based chats — join or create chatrooms by simply entering a room name
* Friend-based DM feature for one-on-one conversations

### 🧩 Encryption Layer

* Messages are encrypted using a custom **crypto key** before transmission
* Ensures data privacy during message exchange

---

## ⚙️ Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| **Backend**    | Django, Django Channels                 |
| **Database**   | MongoDB (Atlas)                         |
| **Frontend**   | HTML, CSS, JavaScript                   |
| **Server**     | Gunicorn + Railway Deployment           |
| **Encryption** | Python’s `cryptography` module (Fernet) |

---

## 🏗️ Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/ConvoNet.git
   cd ConvoNet
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=your_django_secret_key
   CRYPTO_KEY=your_crypto_key
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?appName=ConvoNet
   DEBUG=True
   ```

5. **Run the server**

   ```bash
   python manage.py runserver
   ```

---

## 🌐 Deployment

* Deployed on **Railway.app** using Gunicorn
* Procfile configuration:

  ```
  web: gunicorn chatroom.chatroom.wsgi:application --bind 0.0.0.0:$PORT
  ```

---

## 🛡️ Security Notes

* Keep your `SECRET_KEY` and `CRYPTO_KEY` in environment variables (not hardcoded).
* Never commit `.env` or database credentials to GitHub.
* MongoDB Atlas is recommended over localhost for production.

---

## 🔮 Future Enhancements

* Add real-time notifications
* File sharing in chat
* DM bubble notifications 
* Group management and admin controls

---

## 👨‍💻 Author

**Ketan Jain**
Project: ConvoNet — Secure, Scalable Chatrooms for Everyone.
