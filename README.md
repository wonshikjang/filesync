# filesync

This project focuses on continuing to finely synchronize the inside of the specified folder on multiple devices. Therefore, instead of using simple FTP server or P2P communication, server-side and client-side are implemented separately.

This project was produced as final project of GIST's EC4206 lecture 'Computer Networking' in Fall sememster of 2022.

## Project diagram
![image](https://user-images.githubusercontent.com/75793880/209026739-8b153444-1e6e-470c-a08c-2a32f076493c.png)

## Tools used

### Server : Python, FastAPI, WebSocket, MySQL with Sqlalchemy
The server side stores a list of different information in the file in the DB, and of course stores the binaries of the actual file. In this process, a WAS (Web Application Server) was needed to process requests from clients sophisticatedly. FastAPI used in our WAS is the Python web framework. It runs with Uvicorn ASGI (Asynchronous Server Gateway Interface) server. The server DB uses MySQL, and the Create, Read, Update, Delete (CRUD) operation uses the Python library, SQLAlchemy. The list of files stored in the Server DB is delivered to the client every 5 seconds via WebSocket.

### Client : Python, WebSocket, watchdog, aiohttp, aiofiles
The client side constantly scans the folders you specify using watchdog, a Python library. Watchdog notifies the client of events such as creating, renaming, modifying, deleting, and moving files. The client asynchronously sends the changes to the server. The aiohttp and aiofiles libraries are used in this process. The client receives a list of files from the server via WebSocket. Then, compared to the existing local file list, the required files are requested to the server and downloaded at proper path. Files that do not exist in the list are deleted.

### Tentative Input / Output
Users specify specific folders to archive files as usual. The program automatically detects changes on the client side and server side and synchronizes the folders. The program's gui window displays the log.

## Limitation
### 1. System theory related problems
 Systems basically use a variety of methods for file management. There will be mutex lock, semaphore, etc. This is because multiple processes accessing files at the same time can cause many problems. However, this program manages the inside of the folder externally, causing problems such as overwriting the files being modified by receiving updates from the server side.
### 2. Insufficient Websocket implementation on client side
 The current method unilaterally transfers the list of files from the server to the client at a certain interval. However, WebSocket is a full duplex protocol. Therefore, it is ideal to have a logic in which when the file list is changed on the client side, it is passed to the server, and then the server sends the file list to other clients. However, when other communication performed asynchronous tasks and received a new list of files from the server at an unexpected time, those tasks caused a conflict. We couldn't solve the error and implement it to the client.
### 3. Temporary file problems
 Some programs create temporary files in their folders when modifying files. (e.g. Text Editor on Mac) Temporary files are quickly created and deleted, which sometimes causes errors.

## Sample input and output 

### Example of synchronizing txt file
![image](https://user-images.githubusercontent.com/75793880/209027004-2d2efb85-cbd3-4af1-99de-ae434b7afb52.png)

### Example of synchronization when a txt file is modified
![image](https://user-images.githubusercontent.com/75793880/209027060-a1dd3671-941d-4607-bafa-d943f2921d44.png)

### Example of synchronization when a file is renamed
![image](https://user-images.githubusercontent.com/75793880/209027086-e1bf1945-d3ec-4b6c-a131-686052266924.png)

### Example of synchronizing folder creation and file movement
![image](https://user-images.githubusercontent.com/75793880/209027123-8a2ff4a2-7056-448a-bf49-23da439e4a74.png)






