Hello! This is a Discord file transfer script I made. You can use it to send big files through Discord or share it with friends. It works by encoding files into text or attachments and sending them through a Discord channel.

I've set up a bot and a channel for transfers, so you can use it to send files to me(like the b2b mod I really want to play, or something else):

- Bot Token: In archive (password - 123, discord auto-resetted the token) (Install link for this bot: https://discord.com/oauth2/authorize?client_id=1451185010400038932)
- Channel ID: 1451201347205599263 (My another test server: https://discord.gg/6eGSzMCs)

There are two transfer modes:
1. Normal (text) mode: Files are split into small text messages. This is slow – even 1 MB can take up to 10 minutes – but Discord won't delete the messages.
2. Fast mode: Files are sent as attachments. This is much faster, but Discord might delete the files after a while.

I included a test file "2mb.json" so you can try it out first.

### How to use:
1. Install Python and discord.py(pip install discord.py).
2. Open example_starter_upload.bat or example_starter_download.bat in a text editor.
3. Replace TOKEN_HERE and CHANNEL_HERE with the real token and channel ID.
4. Run the .bat file to upload or download. (If it doesn't work, try changing "py" to "python" or "python3" or etc.)

You can also run it from the command line:
- Upload: "py bot.py UPLOAD TOKEN CHANNEL file.txt [FAST]"
- Download: "py bot.py DOWNLOAD TOKEN CHANNEL [filename] [FAST]"

If you don't specify a filename when downloading, it will try to find the last file that was uploaded.

Let me know if you run into any issues. I made this script in a bit over an hour, so it's simple but should work.

---

P.S. Don’t forget to send me the b2b mod file when you can — I can’t download it from Mediafire(it gives err_reset_connection).


