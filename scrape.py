import asyncio
from itertools import count
from multiprocessing.connection import wait
from threading import Thread
from time import sleep
import traceback
from pyppeteer import launch
import tweepy
from sys import platform
#import keyboard

#Diese Funktion wird nur aufgerufen um vorherige Tweets zu löschen!
def delete(api):
    print("DELETE")
    for status in tweepy.Cursor(api.user_timeline).items():
             try:
               api.destroy_status(status.id)
               print("Deleted:", status.id)
             except Exception:
                print("Failed to delete:", status.id)
    exit()


#Diese Funktion startet einen Browser und führt die Anfragen aus
async def main(country_code,city_code,linux):
    # launch chromium browser in the background
    if(not linux):
     browser = await launch(headless=True, args=['--disable-infobars', f'--window-size={1920},{1080}'])
    else:
     browser = await launch(headless=True, executablePath= '/usr/bin/chromium', args=['--disable-infobars', f'--window-size={1920},{1080}'])
    # open a new tab in the browser
    page = await browser.newPage()

    await page.setViewport({
    'width': 1920, 'height': 1080})
    
    # add URL to a new page and then open it
    await page.goto("https://www.semerkandtakvimi.com")
    await page.waitFor(2000)
    
   
    # select input selector for country in webpage
    await page.click("#select2-country-list-container")
    await page.waitFor(300)
    await page.keyboard.type(country_code) # enter country
    await page.waitFor(1000)
    await page.keyboard.press("Enter")

    await page.waitFor(1000)


    # select input selector for city in webpage
    await page.click("#select2-city-list-container")
    await page.waitFor(300)
    await page.keyboard.type(city_code) # enter city
    await page.waitFor(1000)
    await page.keyboard.press("Enter")
    await page.waitFor(1000)
    
    #Turkey has a special third input, this is set to 
    if(country_code.lower() == "türkiye"):
        await page.click("#select2-district-list-container")
        await page.waitFor(300)
        await page.keyboard.type("a")
        await page.waitFor(1000)
        await page.keyboard.press("Enter")
        await page.waitFor(1000)
    
    
    # create a screenshot of the page and save it
    screen = await page.xpath("/html/body/div[2]/div/section[2]/div/div")
    await screen[0].screenshot({"path": "python.png"})
    #await page.waitFor(20000)
    # close the browser
    await browser.close()



#check OS to allow function in Windows, Linux and Raspberry Pi
linux = False

if platform == "linux" or platform == "linux2":
    linux= True
elif platform == "win32":
    linux = False


#open api data
with open("apidata.txt", "r") as f:
    data = f.read()
    splitted = data.split(",")

#authentify connection to Twitter
auth = tweepy.OAuth1UserHandler(
   splitted[0], splitted[1], splitted[2], splitted[3]
)

#get previously posted tweet-ids
with open("used.txt", "r") as f:
    data = f.read()
    f.close()
    print("DATA")
    print(str(data))
    

print("Starting...")
loop = asyncio.get_event_loop()


#get API Connection
api = tweepy.API(auth)

#uncomment to delete previous tweets
#delete(api)



#iterate though all tweets
i = 0
j=0
while i == 0:
    #if keyboard.is_pressed("q"):
        #break
    #API is called and searches all tweets which contain the account name contained in the apidata.txt file
    tweets = api.search_tweets(q = "@"+splitted[4], result_type ="recent", count=50,tweet_mode="extended")
    for j in range(0,len(tweets)):
        #check if tweet is empty
     if(tweets[j] != []):
      tweetid = tweets[j].id
      print(tweetid)
     
     print("LOL")
     #check if tweet-id is in data-> check if tweet was answered before
     if(str(tweetid) in data):
        print("DUPLICATE")
        sleep(5)
     else:
        try:
         
         #format the input from the tweet
         temp = tweets[j].full_text.split("#")
         temp[1] = temp[1].replace(" ","")
         temp[2] = temp[2].replace(" ","")
        
         # call function to retrieve prayer times
         loop.run_until_complete(main(temp[1],temp[2]))
         # push tweet with api
         api.update_status_with_media('your reply',"python.png", in_reply_to_status_id = tweetid , auto_populate_reply_metadata=True)
         
         # tweet-id gets added to used.txt to make sure that no duplicates will be generated!          
         data = data+ str(tweetid)
         print(data)
         print(str(tweetid))
         with open("used.txt", "w+") as f:
          temp = data
          f.write(temp)
          f.write("-")
          f.write(str(tweetid))
          f.flush()
          f.close()
         sleep(5) 
         print("replied")
        except Exception:
            traceback.print_exc
            print("ERROR IN INPUT")







    





        

    



