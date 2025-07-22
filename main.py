from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import generate_modulated_signal

app = FastAPI()

# Static and template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure image output directory
os.makedirs("static/outputs", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/working")
async def working(request: Request):
    return templates.TemplateResponse("working.html", {"request": request})

@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def generate_wave(
    request: Request,
    modulationType: str = Form(...),
    messageFrequency: float = Form(default=0.0),
    messageAmplitude: float = Form(default=0.0),
    carrierFrequency: float = Form(...),
    carrierAmplitude: float = Form(...),
    messageWaveform: str = Form(default="sine"),
    carrierWaveform: str = Form(default="sine"),
    digitalMessage: str = Form(default=""),
):
    # Generate waveform
    t, message, carrier, modulated_wave, mod_index = generate_modulated_signal(
        modulationType, messageFrequency, messageAmplitude,
        carrierFrequency, carrierAmplitude,
        messageWaveform, carrierWaveform,
        digitalMessage
    )

    # Save plots
    msg_path = "static/outputs/message.png"
    carrier_path = "static/outputs/carrier.png"
    img_path = "static/outputs/modulated.png"

    plt.figure(figsize=(5, 2))
    plt.plot(t, message)
    plt.title("Message Signal")
    plt.savefig(msg_path)
    plt.close()

    plt.figure(figsize=(5, 2))
    plt.plot(t, carrier)
    plt.title("Carrier Signal")
    plt.savefig(carrier_path)
    plt.close()

    plt.figure(figsize=(6, 3))
    plt.plot(t, modulated_wave)
    plt.title(f"{modulationType} Modulated Signal")
    plt.savefig(img_path)
    plt.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "digitalMessage": digitalMessage,
        "modulationType": modulationType, 
        "carrierWaveform": carrierWaveform,
        "messageWaveform": messageWaveform,
        "modulationType": modulationType,
        "img_path": img_path,
        "msg_path": msg_path,
        "carrier_path": carrier_path,
        "mod_index": mod_index,
        "messageFrequency": messageFrequency,
        "messageAmplitude": messageAmplitude,
        "carrierFrequency": carrierFrequency,
        "carrierAmplitude": carrierAmplitude,
    })
