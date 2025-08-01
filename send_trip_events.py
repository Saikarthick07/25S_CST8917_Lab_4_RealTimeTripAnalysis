import json
import time
from azure.eventhub import EventHubProducerClient, EventData

# Paste your Event Hub connection string here
CONNECTION_STR = "Endpoint=sb://taxidispatchns18459.servicebus.windows.net/;SharedAccessKeyName=TaxiDispatchSendRule;SharedAccessKey=Cu6VbCvxF4vZm8TwTMxHfZxlA+VaVxRXz+AEhAtXlkU=;EntityPath=TaxiTripsHub"

# Event Hub name
EVENT_HUB_NAME = "TaxiTripsHub"

# Sample taxi trip events
sample_events = [
{
  "ContentData": {
    "vendorID": "SAI",
    "tripDistance": 5,
    "passengerCount": 2,
    "paymentType": "1"
  }
}
]

def send_events():
    producer = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENT_HUB_NAME)
    try:
        event_batch = producer.create_batch()
        for event in sample_events:
            event_batch.add(EventData(json.dumps(event)))
        producer.send_batch(event_batch)
        print("Sent batch of sample trip events.")
    finally:
        producer.close()

if __name__ == "__main__":
    send_events()
