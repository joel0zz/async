import asyncio
import aiohttp
import aiofiles
import logging
import sys
from aiohttp import ClientSession
import re


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True


HREF_RE = re.compile(r'img src="(.*?)"')  # regex for finding .png links


async def fetch(url: str, session: ClientSession) -> str:
    response = await session.get(url)  # wait for responses to be returned from get request. <---- 3rd
    logger.info("Got response [%s] for URL: %s", response.status, url)
    html = await response.text()  # wait for response to be converted to text. <----- 4th
    return html


async def parse(url: str, session: ClientSession) -> list:
    found_images = []
    try:
        response = await fetch(url, session)  # wait for response to be returned. <----- 2nd
    except:
        return found_images
    for link in HREF_RE.findall(response):  # when response returned, extract href links, looking for .png image urls.
        found_images.append(link)
    return found_images


async def write(url: str, session: ClientSession) -> None:
    print(f"requesting content from {url}")
    links = await parse(url, session)  # wait for list of links to be returned <---- 1st
    async with aiofiles.open("scraped.txt", "a") as f:  # open file in append mode, in order to write links.
        for link in links:
            await f.write(link + '\n')  # wait for all links in the links list to be appended to the file. <----- 6th
        logger.info("Wrote results for source URL: %s", url)


async def main(urls: list) -> None:
    async with aiohttp.ClientSession() as session:  # create the session to be used for each request.
        tasks = []
        for url in urls:
            tasks.append(write(url=url, session=session))  # create list of function calls, which will be tasks.
        await asyncio.gather(*tasks)  # unpack list of tasks to be executed.


if __name__ == '__main__':
    with open('urls.txt', 'r') as f:
        urls = [x.strip() for x in f.readlines()]  # read file and place urls in a list.
    asyncio.run(main(urls))  # run main async function containing the tasks.
    print("Complete.")
