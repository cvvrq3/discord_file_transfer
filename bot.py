import discord
import asyncio
import base64
import zlib
import os
import sys

class DiscordFileTransfer:
    def __init__(self, token):
        self.token = token
    
    async def upload(self, channel_id, file_path, fast_mode=False):
        intents = discord.Intents.default()
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            try:
                channel = client.get_channel(channel_id)
                filename = os.path.basename(file_path)
                filesize = os.path.getsize(file_path)
                
                print(f"Uploading: {filename} ({filesize/1024/1024:.2f} MB)")
                
                if fast_mode:
                    print("FAST MODE: Using file attachments")
                    chunk_size = 7 * 1024 * 1024
                    part_num = 0
                    
                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            
                            compressed = zlib.compress(chunk)
                            encoded = base64.b64encode(compressed).decode('ascii')
                            
                            temp_file = f"_part{part_num}.txt"
                            with open(temp_file, 'w', encoding='utf-8') as tf:
                                tf.write(encoded)
                            
                            with open(temp_file, 'rb') as file_to_send:
                                await channel.send(
                                    f"FILEPART:{filename}:{part_num}",
                                    file=discord.File(file_to_send, filename=temp_file)
                                )
                            
                            os.remove(temp_file)
                            part_num += 1
                            print(f"Sent part {part_num}")
                            await asyncio.sleep(1.2)
                    
                    await channel.send(f"FILEDONE:{filename}:{part_num}:{filesize}")
                    print(f"Upload complete! {part_num} parts")
                    
                else:
                    print("TEXT MODE: Sending as messages")
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    compressed = zlib.compress(data)
                    encoded = base64.b64encode(compressed).decode('ascii')
                    
                    chunk_size = 1950
                    chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
                    
                    print(f"Sending {len(chunks)} chunks...")
                    
                    for i in range(0, len(chunks), 5):
                        batch = chunks[i:i+5]
                        for chunk in batch:
                            await channel.send(chunk)
                        
                        if i % 100 == 0:
                            print(f"Progress: {i}/{len(chunks)}")
                        await asyncio.sleep(0.4)
                    
                    await channel.send(f"TEXTDONE:{filename}:{len(chunks)}")
                    print("Text upload complete")
                
            except Exception as e:
                print(f"Error: {e}")
            finally:
                await client.close()
        
        await client.start(self.token)
    
    async def download(self, channel_id, filename=None, fast_mode=False):
        intents = discord.Intents.default()
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            try:
                channel = client.get_channel(channel_id)
                
                if fast_mode:
                    print("FAST MODE: Downloading file parts")
                    parts = {}
                    file_info = None
                    
                    async for msg in channel.history(limit=200):
                        content = msg.content
                        
                        if content.startswith("FILEDONE:"):
                            info = content.split(':')
                            if len(info) >= 4:
                                fname = info[1]
                                if filename is None or fname == filename:
                                    file_info = {
                                        'name': fname,
                                        'parts': int(info[2]),
                                        'size': int(info[3])
                                    }
                                    print(f"Found: {file_info['name']} ({file_info['parts']} parts)")
                        
                        elif content.startswith("FILEPART:") and msg.attachments:
                            info = content.split(':')
                            if len(info) >= 3:
                                fname = info[1]
                                part_num = int(info[2])
                                
                                if filename is None or fname == filename:
                                    parts[part_num] = msg.attachments[0]
                    
                    if not file_info:
                        print("File not found")
                        return
                    
                    print(f"Downloading {file_info['parts']} parts...")
                    all_data = bytearray()
                    
                    for i in range(file_info['parts']):
                        if i in parts:
                            attachment = parts[i]
                            temp_file = f"_download_part{i}.txt"
                            await attachment.save(temp_file)
                            
                            # Hi
                            with open(temp_file, 'r', encoding='utf-8') as f:
                                encoded = f.read()
                            
                            decoded = base64.b64decode(encoded)
                            decompressed = zlib.decompress(decoded)
                            all_data.extend(decompressed)
                            
                            os.remove(temp_file)
                            print(f"Part {i+1}/{file_info['parts']} downloaded")
                        else:
                            print(f"Warning: Missing part {i}")
                    
                    with open(file_info['name'], 'wb') as f:
                        f.write(all_data)
                    
                    print(f"Saved: {file_info['name']} ({len(all_data)} bytes)")
                    
                else:
                    print("TEXT MODE: Collecting messages")
                    messages = []
                    file_info = None
                    
                    async for msg in channel.history(limit=2000):
                        content = msg.content
                        
                        if content.startswith("TEXTDONE:"):
                            info = content.split(':')
                            if len(info) >= 3:
                                fname = info[1]
                                if filename is None or fname == filename:
                                    file_info = {
                                        'name': fname,
                                        'chunks': int(info[2])
                                    }
                                    print(f"Found: {file_info['name']} ({file_info['chunks']} chunks)")
                        
                        elif len(content) > 100:
                            messages.append(content)
                    
                    if not file_info:
                        print("File not found")
                        return
                    
                    messages.reverse()
                    combined = ''.join(messages[:file_info['chunks']])
                    
                    decoded = base64.b64decode(combined)
                    decompressed = zlib.decompress(decoded)
                    
                    with open(file_info['name'], 'wb') as f:
                        f.write(decompressed)
                    
                    print(f"Saved: {file_info['name']} ({len(decompressed)} bytes)")
                
            except Exception as e:
                print(f"Error: {e}")
            finally:
                await client.close()
        
        await client.start(self.token)

async def main():
    if len(sys.argv) < 4:
        print("Discord File Transfer")
        print("Usage:")
        print("  UPLOAD:  python filetransfer.py UPLOAD TOKEN CHANNEL FILE [FAST]")
        print("  DOWNLOAD: python filetransfer.py DOWNLOAD TOKEN CHANNEL [FILE] [FAST]")
        print("\nExamples:")
        print("  python filetransfer.py UPLOAD token123 1451193221605626023 myfile.zip")
        print("  python filetransfer.py UPLOAD token123 1451193221605626023 myfile.zip FAST")
        print("  python filetransfer.py DOWNLOAD token123 1451193221605626023")
        print("  python filetransfer.py DOWNLOAD token123 1451193221605626023 myfile.zip FAST")
        return
    
    mode = sys.argv[1].upper()
    token = sys.argv[2]
    channel_id = int(sys.argv[3])
    
    transfer = DiscordFileTransfer(token)
    
    if mode == "UPLOAD":
        if len(sys.argv) < 5:
            print("Missing file path")
            return
        
        file_path = sys.argv[4]
        fast_mode = len(sys.argv) > 5 and sys.argv[5].upper() == "FAST"
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        await transfer.upload(channel_id, file_path, fast_mode)
    
    elif mode == "DOWNLOAD":
        target_filename = None
        fast_mode = False
        
        for i in range(4, len(sys.argv)):
            arg = sys.argv[i].upper()
            if arg == "FAST":
                fast_mode = True
            elif not target_filename:
                target_filename = sys.argv[i]
        
        await transfer.download(channel_id, target_filename, fast_mode)
    
    else:
        print("Invalid mode. Use UPLOAD or DOWNLOAD")

if __name__ == "__main__":
    asyncio.run(main())