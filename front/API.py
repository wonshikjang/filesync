import asyncio
import aiohttp
import sys, os
# pip install aiohttp
# python -m pip install aiohttp   

class API():
    def __init__(self, config):
        self.config = config
        self.server_ip = config.getConfig("CLIENT_CONFIG", "server_ip")
        self.port = config.getConfig("CLIENT_CONFIG", "port")
        self.url = "%s:%s" % (self.server_ip, self.port)

    def _url(self, url):
        return self.url + url

    async def getFileList(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url("/list")) as res:
                files = await res.json()
                return files

    # async def createFile(self):
    #     data = { "id": "string4", "name": "string", "path": "string", "md5": "string" }
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(_url("/"), json=data) as resp:
    #             print(resp.status)
    #             print(resp)
    #             print(await resp.text())


    # asyncio.run(checkToUpdate([]))