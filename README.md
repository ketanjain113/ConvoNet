# ConvoNet / Chatroom Railway Deployment

## Railway Deployment Instructions

1. **Push your code to GitHub** (already done).

2. **Create a new Railway project:**
   - Click "New Project" > "Deploy from GitHub repo" and select this repository.

3. **Set Environment Variables**
   - Add a new variable: `MONGODB_URI`
   - Value: Your MongoDB connection string from MongoDB Atlas. Example:
     ```
     mongodb+srv://<user>:<password>@<cluster>.mongodb.net/chatroom?retryWrites=true&w=majority
     ```

4. **MongoDB Setup:**
   - Make sure a database and user exist on MongoDB Atlas (or elsewhere), and grant access to `chatroom` or desired database.
   - Get your MongoDB cluster connection URI from MongoDB Atlas dashboard.

5. **Deploy**
   - Railway will auto-install dependencies from `requirements.txt` and use the `Procfile` to start your server.

6. **Visit Your Web App**
   - After build completes, Railway gives you a public URL.

## Environment variables
- `MONGODB_URI` — connection string for your MongoDB instance.

## Notes
- By default, Django admin is enabled. For production, lock down admin route, set `DEBUG = False`, and fix up `ALLOWED_HOSTS` in your settings.
- For custom domains, see Railway documentation.
