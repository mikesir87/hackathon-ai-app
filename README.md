# Madlib Chatbot

This is a fun chatbot demo that uses keywords (found in `src/config.json`) to generate a persona that is used for chatbot responses. It's just for fun!

## How's it work?

When the app starts up, it uses the madlib keywords and plugs them into a script. That script is sent to gpt-4 to generate a persona. From that point on, that persona description is sent with each of the questions, making the responses more fun!

## Development

Before getting started, you need to create a `.env` file with the following values (you can use the .env.sample file as a template):

```
OPENAI_API_KEY=sk-qabcdefghijklmnopqrstuvwxyz123456
```

With that in place, you can simply run `docker compose up --watch`. All file changes will be synced into the container, allowing you to test changes within a few seconds.

