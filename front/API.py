import asyncio
import aiohttp
import sys, os
# pip install aiohttp
# python -m pip install aiohttp   

class API():
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
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

    async def createFile(self, file):
        # encode ?
        fileJson = { "id": str(file.id), "name": file.name, "path": file.sync_path, "md5": file.md5 }
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url("/"), json=fileJson) as res:
                self.logger.print_log_server("RES HTTP/1.1 %s" % res.status)
                self.logger.print_log_server(res)
                self.logger.print_log_server(await res.text())
    
    async def modifyFile(self, file):
        fileJson = { "id": str(file.id), "name": file.name, "path": file.sync_path, "md5": file.md5 }
        async with aiohttp.ClientSession() as session:
            async with session.put(self._url("/%s" % str(file.id)), json=fileJson) as res:
                self.logger.print_log_server("RES HTTP/1.1 %s" % res.status)
                self.logger.print_log_server(res)
                self.logger.print_log_server(await res.json())
            
    async def deleteFile(self, file):
        async with aiohttp.ClientSession() as session:
            async with session.delete(self._url("/%s" % str(file.id))) as res:
                self.logger.print_log_server("RES HTTP/1.1 %s" % res.status)
                self.logger.print_log_server(res)
                self.logger.print_log_server(await res.text())
                
    async def uploadFile(self, file):
        file_to_send = aiohttp.FormData()
        file_to_send.add_field('file', open(file.real_path, 'rb'), filename="%s.%s" % (str(file.id),file.name.split(".")[-1]), content_type="multipart/form-data")
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url("/file"), data=file_to_send) as res:
                self.logger.print_log_server("RES HTTP/1.1 %s" % res.status)
                self.logger.print_log_server(res)
                self.logger.print_log_server(await res.text())
                
    async def downloadFile(self, file_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url("/download/file/%s" % file_id)) as res:
                self.logger.print_log_server("RES HTTP/1.1 %s" % res.status)
                self.logger.print_log_server(res)
                self.logger.print_log_server(await res.text())