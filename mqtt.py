import paho.mqtt.client as mqtt
from cryptography.fernet import Fernet, InvalidToken
import base64


class EncryptedChat:
    def __init__(self):
        key = base64.urlsafe_b64encode(bytes("my32lengthsupersecretnooneknows1", 'utf-8'))  # Generera en kod från ett nyckelord (base64 encoding)
        self.fernet = Fernet(key)  # Fernet objekt för kryptering och avkryptering
        self.client = mqtt.Client()  # Skapar MQTT client objekt
        self.client.on_connect = self.connector  # Callback för MQTT
        self.client.on_message = self.messager  # Callback för MQTT

    def connector(self, client, userdata, flags, rc):  # Callback när man anslutit till broker
        print(f"Ansluten till servern, med statuskod {rc}")
        client.subscribe(topic="testaaatopic/testttt")  # Premenumerar på en topic vid lyckad anslutning

    def messager(self, client, userdata, message):  # Callback när man tar emot meddelande från broker
        try:
            decrypted_message = self.decrypt_messager(message.payload)  # Decodar meddelandet till läsbart
            print(f"Ämne: {message.topic}, Meddelande: {decrypted_message}")  # Printar Topic och Message från meddelande.
        except InvalidToken:
            print("Error: Felaktig token, går ej att dekryptera!")

    def encrypt_messager(self, message):  # Funktion för kryptering av meddelande
        encrypted_message = self.fernet.encrypt(bytes(message, 'utf-8'))
        return encrypted_message

    def decrypt_messager(self, encrypted_message):  # Funktion för avkryptering av meddelande
        decrypted_message = self.fernet.decrypt(encrypted_message).decode('utf-8')
        return decrypted_message

    def main(self):
        host = 'broker.hivemq.com'
        self.client.connect(host=host, port=1883, keepalive=60)  # Ansluter till broker
        self.client.loop_start()  # MQTT loop för klient

        alias = input("Vänligen ange ditt Alias: ")  # Låter klient välja Alias för chatt
        print("Skriv 'lämna' för att sedan lämna chatten")  # Printar hjälp för användare

        while True:  # loop för att skicka meddelanden
            meddelande = input("Ditt meddelande: ")  # Input för user meddelande
            if meddelande.lower() == "lämna":  # Om user skriver lämna så lämnar hen loopen
                break

            # Skickar klient meddelande som inkluderare alias och själva meddelandet med qos på 1 samt krypterar innan de skickas
            encrypted_message = self.encrypt_messager(f"<{alias}> {meddelande}")
            self.client.publish("testaaatopic/testttt", encrypted_message, qos=1)

        self.client.loop_stop()  # Stoppar loop och anslutning till broker vid lämning
        self.client.disconnect()


if __name__ == '__main__':  # Körs bara om man kör filen direkt
    chat_instance = EncryptedChat()  # Skapar instans för klass
    chat_instance.main()  # Startar programmet
