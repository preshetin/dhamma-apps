# Dhamma Apps

A the moment, it has the following apps:
- API endpoint for courses schedule. See demo at https://seahorse-app-db78s.ondigitalocean.app/api/courses
- Telegram bots webhook endpoints. See demo at https://t.me/ChildrenCoursesOrgBot


## How to add new bot

1. Create knowledge base in a file with .md extension
2. Create new index (vector database) based on that file. Make sure to edit `load_index.py` and fill in filename.
```
python load_index.py
```
3. Go to BotFather and create new bot
4. Set webhook
```
curl -X POST "https://api.telegram.org/bot{token}/setWebhook?url=https://xxxx.ondigitalocean.app/webhook-example"
```
5. Create / copy webhook endpoint.
6. Test bot by typing something.

## How it gets courses schedule?

It parses Vipassana courses schedule and returns a JSON list of courses.

![photo_2024-11-18 6 33 22 PM](https://github.com/user-attachments/assets/e00027cc-0b9e-4501-bc07-2888153913ec)
