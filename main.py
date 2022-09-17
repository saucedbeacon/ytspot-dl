import random
import time
import requests
import telebot
import os
import wget
from yt_dlp import YoutubeDL
import yt_dlp
import json
import integv
from time import sleep
from urllib.parse import urlparse
from telebot.async_telebot import AsyncTeleBot
import asyncio
from spotify_dlx import SpotifyDLXClient
ydl_opts = {
    'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    "outtmpl": "%(id)s.%(ext)s"}
bot = AsyncTeleBot("5645973979:AAH4qLQrAYbWrjQNKjq4zXU477XhGvA4GrE", parse_mode=None)


def logon():
    global client
    while True:
        try:
            client = SpotifyDLXClient(root="./", format = "wav", root_podcast="C:/Users/azurets/Documents/sp")
            client.login(username="pipe@wsapi.eu.org", password="23041978")
            break
        except:
            continue

logon()

@bot.message_handler(commands=["start"])
async def startHandler(message):
    await bot.reply_to(message, """
Hi! This bot is an extension to @putluck.
""")

@bot.message_handler(regexp="https:\/\/youtu.be/", commands=["snap"])
async def youtubeDownloading(message):
    try:
        cleanedLink = message.text.replace("/snap ", "")
        timeStart = int(time.time())
        processMessage = await bot.reply_to(message, "Processing...")
        print(timeStart)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(cleanedLink, download=True)
            songTitle = info["title"]
        endProcess = str(int(time.time()) - timeStart)
        await bot.delete_message(processMessage.chat.id, processMessage.id)
        fileName = str(info["id"])
        audio = open(f"{fileName}.m4a", "rb")
        toReply = await bot.send_audio(message.chat.id, audio, songTitle + f"\nProcess time : {endProcess} s", title = songTitle)
        os.system(f"rm {fileName}.m4a")
    except:
        await bot.reply_to(message, "Error occured, please try again..")
        
@bot.message_handler(regexp="https:\/\/open.spotify.com\/track\/")
async def trackDownloading(message):
    while True:
        try:
            timeStart = int(time.time())
            print(timeStart)
            if "https://open.spotify.com/track/" in message.text:
                rawTrackLink = message.text
                cleanedTrackLink = rawTrackLink
                trackLink = urlparse(cleanedTrackLink).path.split("/")[2]
                print(trackLink)
                ts = str(int(time.time()))
                sClient = random.choice([client])
                while True:
                    try:
                        processMessage = await bot.reply_to(message, f"Processing...\nTrack ID : {trackLink}")
                        sClient.download_from_url(f"https://open.spotify.com/track/{trackLink}?si=A9V36u_DQQWp7hWrV416OA&utm_source=copy-link", ts)
                        sMeta = client._fetch_song_info(trackLink)
                        break
                    except Exception as e:
                        if e != "SpotifyLimitError":
                            await bot.reply_to(message, "Server is waking up, please try again in 15 secs.")
                            logon()
                            return False
                        else:
                            raise Exception("SpotifyLimitError")
                songTitle = sMeta[2]
                songMainArtist = sMeta[0][0]
                print(songTitle + " - " + songMainArtist)
                filepath = f'{ts}.wav'
                toSend = filepath
                audio = open(toSend, 'rb')
                s = os.system(f"ffmpeg.exe -v error -i {filepath} -f null - >error.log 2>&1")
                if s == 1:
                    raise Exception("File corrupted")
                endProcess = str(int(time.time()) - timeStart)
                await bot.delete_message(processMessage.chat.id, processMessage.id)
                toReply = await bot.send_audio(message.chat.id, audio, songTitle + f"\nProcess time : {endProcess} s", songMainArtist, songMainArtist, title = songTitle)
                trashMessage = await bot.reply_to(toReply, "!play")
                audio.close()
                sleep(3)
                await bot.delete_message(trashMessage.chat.id, trashMessage.id)
                os.system(f"rm {filepath}")
            else:
                pass
            break
        except Exception as e :
            print(e)
            await bot.reply_to(message, "An error occured while processing your request, trying again...")
            continue

@bot.message_handler(regexp="https:\/\/open.spotify.com\/playlist\/", commands=["spl"])
async def playlistDownloading(message):
    while True:
        try:
            timeStart = int(time.time())
            print(timeStart)
            if "https://open.spotify.com/playlist/" in message.text:
                rawTrackLink = message.text
                cleanedTrackLink = rawTrackLink.replace("/spl ", "")
                playlistLink = urlparse(cleanedTrackLink).path.split("/")[2]
                try:
                    p = client.fetch_songs_in_playlist(playlistLink)
                except:
                    logon()
                    await bot.reply_to(message, f"Server is not ready, please try again in 15 secs.")
                    return True
                trackFetch = """"""
                del p[10:]
                index = 0
                for i in p:
                    index += 1
                    o = i["track"]["name"]
                    trackShareable = "https://open.spotify.com/track/" + str(i["track"]["id"])
                    info = o #(o[:25] + '..') if len(o) > 25 else o
                    trackFetch += f"""#{str(index)}. <a href="{trackShareable}">{info}</a>\n"""
                print(trackFetch)
                processMessage = await bot.reply_to(message, f"""Processing...\nPlaylist ID : {playlistLink}\nFollowing tracks will be processed :\n{trackFetch}""", parse_mode="HTML", disable_web_page_preview=True)
                
                for i in p:
                    trackLink = i["track"]["id"]          
                    ts = str(int(time.time()))
                    sClient = random.choice([client])
                    while True:
                        try:
                            sClient.download_from_url(f"https://open.spotify.com/track/{trackLink}?si=A9V36u_DQQWp7hWrV416OA&utm_source=copy-link", ts)
                            sMeta = client._fetch_song_info(trackLink)
                            break
                        except Exception as e:
                            if e != "SpotifyLimitError":
                                await bot.reply_to(message, "Server is waking up, please try to fetch single track first.")
                                #logon()
                                return False
                            else:
                                raise Exception("SpotifyLimitError")
                    songTitle = sMeta[2]
                    songMainArtist = sMeta[0][0]
                    print(songTitle + " - " + songMainArtist)
                    filepath = f'{ts}.wav'
                    toSend = filepath
                    audio = open(toSend, 'rb')
                    s = os.system(f"ffmpeg.exe -v error -i {filepath} -f null - >error.log 2>&1")
                    if s == 1:
                        raise Exception("File corrupted")
                    endProcess = str(int(time.time()) - timeStart)
                    toReply = await bot.send_audio(message.chat.id, audio, songTitle + f"\nProcess time : {endProcess} s", songMainArtist, songMainArtist, title = songTitle)
                    trashMessage = await bot.reply_to(toReply, "!play")
                    audio.close()
                    sleep(3)
                    await bot.delete_message(trashMessage.chat.id, trashMessage.id)
                    os.system(f"rm {filepath}")
                    sleep(1)
                await bot.delete_message(processMessage.chat.id, processMessage.id)
            else:
                pass
            break
        except Exception as e :
            print(e)
            await bot.reply_to(message, "An error occured while processing your request, trying again...")
            continue

import traceback
import sys
           
@bot.message_handler(commands=["spot"])
async def trackSearchAndDownload(message):
    while True:
        try:
            timeStart = int(time.time())
            print(timeStart)
            if True:
                rawTrackLink = message.text
                cleanedTrackLink = rawTrackLink
                trackLink = cleanedTrackLink.replace("/spot ", "")
                print(trackLink)
                ts = str(int(time.time()))
                sClient = random.choice([client])
                while True:
                    try:
                        processMessage = await bot.reply_to(message, f"Processing...\nTrack Search : {trackLink}")
                        p = client._fetch_search_info(trackLink, limit=1)
                        trackPureID = str(p[0][0]["id"])
                        sClient.download_from_url(f"https://open.spotify.com/track/{trackPureID}?si=A9V36u_DQQWp7hWrV416OA&utm_source=copy-link", ts)
                        sMeta = client._fetch_song_info(trackPureID)
                        break
                    except Exception:
                        print(traceback.format_exc())
                        await bot.reply_to(message, "Server is waking up, please try again in 15 secs.")
                        logon()
                        return False
                songTitle = sMeta[2]
                songMainArtist = sMeta[0][0]
                print(songTitle + " - " + songMainArtist)
                filepath = f'{ts}.wav'
                toSend = filepath
                audio = open(toSend, 'rb')
                s = os.system(f"ffmpeg.exe -v error -i {filepath} -f null - >error.log 2>&1")
                if s == 1:
                    raise Exception("File corrupted")
                endProcess = str(int(time.time()) - timeStart)
                await bot.delete_message(processMessage.chat.id, processMessage.id)
                toReply = await bot.send_audio(message.chat.id, audio, songTitle + f"\nProcess time : {endProcess} s", songMainArtist, songMainArtist, title = songTitle)
                trashMessage = await bot.reply_to(toReply, "!play")
                audio.close()
                sleep(3)
                await bot.delete_message(trashMessage.chat.id, trashMessage.id)
                os.system(f"rm {filepath}")
            else:
                pass
            break
        except Exception as e :
            print(e)
            await bot.reply_to(message, "An error occured while processing your request, trying again...")
            continue

while True:
    try:
        asyncio.run(bot.polling())
    except:
        continue
