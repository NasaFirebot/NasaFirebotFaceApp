#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os, sys, requests, json, operator, http
import flask_session
from flask import Flask, request, session
from pymessenger import Bot
from flask_session import Session

#sess = session
app = Flask(__name__)
#PAGE ACCESS TOKEN
PAGE_ACCESS_TOKEN = "EAAFnZAjoFcpIBAEye9Ah1kGZBQewsM2jJxR6ZCMevqFbwctZAM6B0WJYuUJhqN39GuE9xh2geTXnZBHtgDHEdeGBrqDlZBE9bchW9dGOpZA0cme0W1uZApalZAYq47szpq1PLAZAdYDuwTgA0nEBKZBiETwplknXHnrPZBLNIRSvpRNw5Cbll7uF30khfe6K0u40qZBIZD"
bot = Bot(PAGE_ACCESS_TOKEN)
@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/app2', methods=['POST'])
def webhook():
    data = request.get_json()
    s = requests.session()
    log(data)
    user_name=''
    if data['object'] == 'page':
        for entry in data['entry']:
            if 'messaging' in entry:
                for messaging_event in entry['messaging']:
                    # IDs
                    sender_id = messaging_event['sender']['id']
                    recipient_id = messaging_event['recipient']['id']
                    #get username
                    user_details_url = "https://graph.facebook.com/v2.6/%s"%sender_id
                    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
                    user_details = requests.get(user_details_url, user_details_params).json()
                    user_name= str(user_details.get('first_name'))
                    #POSTBACK
                    if messaging_event.get('postback'):
                        if 'payload' in messaging_event['postback']:
                            messaging_text = messaging_event['postback']['payload']
                            if messaging_text=='Empezar' or messaging_text=='Get Started' :
                                respuesta(sender_id,1,user_name)
                            elif messaging_text == 'Incendio1':
                                bot.send_text_message(sender_id, 'Por favor envianos la ubicación del incendio.')
                            elif messaging_text == 'mas_opciones':
                                respuesta(sender_id,6,user_name)
                            elif messaging_text == 'con_foto':
                                respuesta(sender_id,3,user_name)
                            elif messaging_text == 'sin_foto':
                                respuesta(sender_id,4,user_name)
                            elif messaging_text == 'ver_informe_incendios':
                                bot.send_text_message(sender_id, 'entró')
                                #sess['ESTADO'] = 'ver_informe_incendios'
                                #bot.send_text_message(sender_id, 'estado = ' + sess.get('ESTADO'))
                                bot.send_text_message(sender_id, 'Por favor envianos tú ubicación.')
                    #MESSAGE
                    elif messaging_event.get('message') :
                        # Extracting text message
                        if 'text' in messaging_event['message']:
                            messaging_text = messaging_event['message']['text']
                            #bot.send_text_message(sender_id, messaging_text)
                            if messaging_text== 'Hola ' or messaging_text== 'Hola' or messaging_text== 'start':
                                respuesta(sender_id,1,user_name)
                        elif "attachments" in messaging_event['message']:
                            if "location" == messaging_event['message']['attachments'][0]["type"]:
                                coordinates = messaging_event['message']['attachments'][0]['payload']['coordinates']
                                lat = coordinates['lat']
                                lon = coordinates['long']
                                #bot.send_text_message(sender_id, 'Tu latitud es: ' + str(lat) + ' y tu longitud es: ' + str(lon))
                                bot.send_text_message(sender_id, 'Hemos recibido tu ubicación correctamente.')
                                #show_map(sender_id,1,lat,lon)
                                #bot.send_text_message(sender_id, 'estado = ' + sess.get('ESTADO'))
                                #if sess.get('ESTADO') == 'ver_informe_incendios':
                                    #show_map(sender_id,1,lat,lon)
                                bot.send_text_message(sender_id, 'te muestro el informe de incendios')
                            if "image" == messaging_event['message']['attachments'][0]["type"]:
                                image_url = messaging_event['message']['attachments'][0]['payload']['url']
                                #bot.send_text_message(sender_id, 'Tu latitud es: ' + str(lat) + ' y tu longitud es: ' + str(lon))
                                bot.send_text_message(sender_id, 'La URL de tu imagen es: ' + image_url)
                                respuesta(sender_id,5,user_name)
                        else:
                            messaging_text = 'no text'
    return "ok", 200

def show_map(sender_id,op,lat,lon):
    if op==1: #Mostrar informe de incendioshttps://f453160e.ngrok.io
        string='Ver'
        buttons=[
            {"type":"web_url",
            "title":"url del mapa",
            "url":"www.google.com/"}]
        bot.send_button_message(sender_id,string,buttons)

def respuesta(sender_id,op,user_name):
    if op==1: #Saludo inicial
        mensaje = 'Hola! '+user_name+'\nGracias por ponerte en contacto.\ncontador:'
        bot.send_text_message(sender_id, mensaje)
        mensaje='Por favor, dinos qué quieres hacer:'
        buttons=[
                {"type":"postback",
                "title":"Reportar un incendio",
                "payload":"Incendio1"},
                {"type":"postback",
                "title":"Ver refugios cercanos", #pedir ubicación para eso
                "payload":"ver_refugios"},
                {"type":"postback",
                "title":"Más opciones",
                "payload":"mas_opciones"}]
        bot.send_button_message(sender_id,mensaje,buttons)

    if op==2: #Solicitar multimedia
        mensaje='Tienes alguna fotografía o video del incendio?'
        buttons=[
                {"type":"postback",
                "title":"Sí",
                "payload":"con_foto"},
                {"type":"postback",
                "title":"No",
                "payload":"sin_foto"}]
        bot.send_button_message(sender_id,mensaje,buttons)

    if op==3: #Procesar multimedia
        '''mensaje='Tienes alguna fotografía del incendio?'
        buttons=[
                {"type":"postback",
                "title":"Sí",
                "payload":"con_foto"},
                {"type":"postback",
                "title":"No",
                "payload":"sin_foto"}]
        bot.send_button_message(sender_id,mensaje,buttons)'''
        bot.send_text_message(sender_id, 'Aguardamos la imagen...')

    if op==4: #Sin foto
        '''mensaje='Tienes alguna fotografía del incendio?'
        buttons=[
                {"type":"postback",
                "title":"Sí",
                "payload":"con_foto"},
                {"type":"postback",
                "title":"No",
                "payload":"sin_foto"}]
        bot.send_button_message(sender_id,mensaje,buttons)'''
        bot.send_text_message(sender_id, 'Notificaremos el hecho a las autoridades y entidades correspondientes.\nMuchas gracias por tu colaboración.')

    if op==5: #Solicitar multimedia 2
        mensaje='Tienes otra fotografía o video?'
        buttons=[
                {"type":"postback",
                "title":"Sí",
                "payload":"con_foto"},
                {"type":"postback",
                "title":"No",
                "payload":"sin_foto"}]
        bot.send_button_message(sender_id,mensaje,buttons)

    if op==6: #Más opciones
        mensaje='Más opciones'
        buttons=[
                {"type":"postback",
                "title":"Ofrecer un refugio",
                "payload":"ofrecer_refugio"},
                {"type":"postback",
                "title":"Ver informe de incendios", #pedir ubicación para eso
                "payload":"ver_informe_incendios"},
                {"type":"postback",
                "title":"Ver mapa de incendios",
                "payload":"ver_mapa_incendios"}]
        bot.send_button_message(sender_id,mensaje,buttons)

    if op==7:
        bot.send_text_message(sender_id, 'Hola')

def log(message):
    """ Print message. Receive the parameter message"""
    print(message)
    sys.stdout.flush()