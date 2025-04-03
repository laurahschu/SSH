# pubsub.py
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

class AsyncConn:
    def __init__(self, id: str, channel_name: str) -> None:
        config = PNConfiguration()
        config.publish_key = 'pub-c-8538b46d-1968-4f8b-a3b9-93a9414ec166'
        config.subscribe_key = 'sub-c-3803c805-786c-47a7-be00-2b9c4d19a5cf'
        config.secret_key = 'sec-c-OGFjZTNlMTctMzhiOS00NmI2LWJlYzgtMmM1ZDFlNzEwODA0'
        config.user_id = id
        config.enable_subscribe = True
        config.daemon = True

        self.pubnub = PubNub(config)
        self.channel_name = channel_name

        print(f"Configurando conexão com o canal '{self.channel_name}'...")
        subscription = self.pubnub.channel(self.channel_name).subscription()
        subscription.subscribe()

    def publish(self, data: dict):
        print("Publicando mensagem no PubNub...")
        self.pubnub.publish().channel(self.channel_name).message(data).sync()
