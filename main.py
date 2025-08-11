from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import generate_modulated_signal


from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()  # Load .env file

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")



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
    
@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact")
async def send_query(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        # Prepare email
        subject = f"New Query from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return templates.TemplateResponse("contact.html", {
            "request": request,
            "submitted": True,
            "name": name,
            "success": "Your query has been sent successfully!"
        })
    except Exception as e:
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "submitted": True,
            "name": name,
            "error": f"Failed to send message: {str(e)}"
        })



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

    if modulationType == "QPSK":
    # Regenerate I and Q for plotting (since utils.py only returns I in message)
        bits = [int(b) for b in str(digitalMessage) if b in "01"]
        if len(bits) % 2 != 0:
            bits.append(0)
        if not bits:
            bits = [0, 1, 0, 1]  # Default pattern if empty

        I_bits = bits[0::2]
        Q_bits = bits[1::2]
        I_symbols = 2*np.array(I_bits) - 1
        Q_symbols = 2*np.array(Q_bits) - 1
        samples_per_symbol = len(t) // len(I_symbols)
        I_wave = np.repeat(I_symbols, samples_per_symbol)
        Q_wave = np.repeat(Q_symbols, samples_per_symbol)
        I_wave = np.pad(I_wave, (0, len(t) - len(I_wave)), mode='constant')
        Q_wave = np.pad(Q_wave, (0, len(t) - len(Q_wave)), mode='constant')

        # Plot I & Q baseband
        plt.figure(figsize=(5, 2))
        plt.plot(t, I_wave, label="In-phase (I)")
        plt.plot(t, Q_wave, label="Quadrature (Q)")
        plt.title("QPSK Baseband Signals")
        plt.legend()
        plt.savefig(msg_path)
        plt.close()

    else:
        # Plot single message waveform
        plt.figure(figsize=(5, 2))
        plt.plot(t, message)
        plt.title("Message Signal")
        plt.savefig(msg_path)
        plt.close()

    # Carrier plot
    plt.figure(figsize=(5, 2))
    plt.plot(t, carrier)
    plt.title("Carrier Signal")
    plt.savefig(carrier_path)
    plt.close()

    # Modulated signal plot
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
