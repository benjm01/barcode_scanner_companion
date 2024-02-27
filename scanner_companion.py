import asyncio
import websockets
import socket
import qrcode

import tkinter as tk
from PIL import ImageTk,Image

import threading
import queue

popup = tk.Tk()
q = queue.Queue()

async def handler(websocket):
    while True:
        # this will let the main thread know that it can destroy the popup
        if (q.qsize() != 1):
            q.put("connected")

        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            # exit handler
            break
        print(message)
    stop.set_result("disconnected")


async def server():
    global stop
    stop = asyncio.Future()
    async with websockets.serve(handler, "", 8001):
        # wait for handler to finish
        await stop

def check_to_destroy():
    # destroy popup once connected to client
    if (q.qsize() == 1):
        popup.destroy()
    else:
        popup.after(1000, check_to_destroy)

def popup_qr():
    # get the ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # create a qr code with the ip address and port
    img = qrcode.make(ip + ':8001')
    img.save("IP.png")

    # show tkinter popup with QR code
    popup.wm_title("Scan from app to connect")
    canvas = tk.Canvas(popup, width = 256, height = 256)
    canvas.pack()
    qr = ImageTk.PhotoImage(Image.open("IP.png"))
    canvas.create_image(128, 128, anchor=tk.CENTER, image=qr)

    popup.after(1000, check_to_destroy)
    popup.mainloop()

def main():
    # start server on another thread
    server_thread = threading.Thread(target=asyncio.run, args=(server(),))
    server_thread.start()

    # display popup
    popup_qr()

    # wait for server to exit
    server_thread.join()
    

if __name__ == "__main__":
    main()