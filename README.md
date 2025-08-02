# CST8917 Lab 4: Real-Time Trip Event Analysis

### Youtube Demo : https://youtu.be/02HhWZ3GG8Q 

##  Scenario: Real-Time Trip Monitoring for Taxi Dispatch System

Modern transportation systems—like ride-sharing platforms and taxi dispatch networks—generate large volumes of trip data in real time. To ensure service quality, safety, and operational insights, it's crucial to monitor this data as it arrives, analyze it immediately, and flag unusual patterns.

Imagine you're working for a transportation technology company that supports a large network of taxi services across the city. Your job is to help the operations team by automatically analyzing incoming trip data and notifying them about any trips that might be unusual or suspicious.

Your system will monitor data such as:

- Number of passengers
- Trip distance
- Payment method
- Vendor ID

You will implement a real-time event-driven system that:
- Ingests taxi trip events from an Event Hub
- Uses an Azure Function to analyze trips for patterns (like group rides, cash payments, or suspiciously short rides)
- Routes this analysis through a Logic App
- Posts rich Adaptive Cards to Microsoft Teams to alert operations staff

This allows dispatchers and supervisors to:
- Immediately spot anomalies
- Monitor high-volume group rides
- Track vendors with suspicious activity
- Reduce manual review time

Example Use Cases:
- A vendor frequently reports short trips (possible fraud)
- High trip volume with cash payment (potential tax evasion risk)
- Unusual passenger patterns (e.g., 5+ passengers on multiple rides)
---


## Tasks

### 1. Set Up Event Ingestion

- Create an Event Hub and simulate sending trip events (use JSON format).
- Configure Azure Logic App to trigger When events are available in Event Hub (use batch mode).

### 2. Create Azure Function

  ``` python
  import azure.functions as func
  import logging
  import json

  app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

  @app.route(route="")
  def analyze_trip(req: func.HttpRequest) -> func.HttpResponse:
      try:
          input_data = req.get_json()
          trips = input_data if isinstance(input_data, list) else [input_data]

          results = []

          for record in trips:
              trip = record.get("ContentData", {})  # ✅ Extract inner trip data

              vendor = trip.get("vendorID")
              distance = float(trip.get("tripDistance", 0))
              passenger_count = int(trip.get("passengerCount", 0))
              payment = str(trip.get("paymentType"))  # Cast to string to match logic

              insights = []

              if distance > 10:
                  insights.append("LongTrip")
              if passenger_count > 4:
                  insights.append("GroupRide")
              if payment == "2":
                  insights.append("CashPayment")
              if payment == "2" and distance < 1:
                  insights.append("SuspiciousVendorActivity")

              results.append({
                  "vendorID": vendor,
                  "tripDistance": distance,
                  "passengerCount": passenger_count,
                  "paymentType": payment,
                  "insights": insights,
                  "isInteresting": bool(insights),
                  "summary": f"{len(insights)} flags: {', '.join(insights)}" if insights else "Trip normal"
              })

          return func.HttpResponse(
              body=json.dumps(results),
              status_code=200,
              mimetype="application/json"
          )

      except Exception as e:
          logging.error(f"Error processing trip data: {e}")
          return func.HttpResponse(f"Error: {str(e)}", status_code=400)
  ```

### 3. Add Logic App Processing
- In Logic App, add a `For Each` loop over the function result.

- Add a Condition:
  - If `item()?['isInteresting']` is `true`, continue to Teams branching
  - Else, post a “Trip Analyzed – No Issues” card

### 4. Post Adaptive Cards to Microsoft Teams

Use the following post cards:
- Not Interesting Trip Card
  ```json
    {
    "type": "AdaptiveCard",
    "body": [
      {
        "type": "TextBlock",
        "text": "✅ Trip Analyzed - No Issues",
        "weight": "Bolder",
        "size": "Large",
        "color": "Good"
      },
      {
        "type": "FactSet",
        "facts": [
          { "title": "Vendor", "value": "@{items('For_each')?['vendorID']}" },
          { "title": "Distance (mi)", "value": "@{items('For_each')?['tripDistance']}" },
          { "title": "Passengers", "value": "@{items('For_each')?['passengerCount']}" },
          { "title": "Payment", "value": "@{items('For_each')?['paymentType']}" },
          { "title": "Summary", "value": "@{items('For_each')?['summary']}" }
        ]
      }
    ],
    "actions": [],
    "version": "1.2"
  }
  ```
- Interesting Trip Card
  ```json
    {
    "type": "AdaptiveCard",
    "body": [
      {
        "type": "TextBlock",
        "text": "🚨 Interesting Trip Detected",
        "weight": "Bolder",
        "size": "Large",
        "color": "Attention"
      },
      {
        "type": "FactSet",
        "facts": [
          { "title": "Vendor", "value": "@{items('For_each')?['vendorID']}" },
          { "title": "Distance (mi)", "value": "@{items('For_each')?['tripDistance']}" },
          { "title": "Passengers", "value": "@{items('For_each')?['passengerCount']}" },
          { "title": "Payment", "value": "@{items('For_each')?['paymentType']}" },
          { "title": "Insights", "value": "@{join(items('For_each')?['insights'], ', ')}" }
        ]
      }
    ],
    "actions": [],
    "version": "1.2"
  }
  ```

- Suspicious Vendor Activity
  ```json
    {
    "type": "AdaptiveCard",
    "body": [
      {
        "type": "TextBlock",
        "text": "⚠️ Suspicious Vendor Activity Detected",
        "weight": "Bolder",
        "size": "Large",
        "color": "Attention"
      },
      {
        "type": "FactSet",
        "facts": [
          { "title": "Vendor", "value": "@{items('For_each')?['vendorID']}" },
          { "title": "Distance (mi)", "value": "@{items('For_each')?['tripDistance']}" },
          { "title": "Passengers", "value": "@{items('For_each')?['passengerCount']}" },
          { "title": "Payment", "value": "@{items('For_each')?['paymentType']}" },
          { "title": "Insights", "value": "@{join(items('For_each')?['insights'], ', ')}" }
        ]
      }
    ],
    "actions": [],
    "version": "1.2"
  }
  ```

# 🚖 Real-Time Taxi Trip Analysis with Azure Event Hubs, Functions & Logic Apps

This project demonstrates a **real-time taxi trip monitoring system** using:
- **Azure Event Hubs** for event ingestion  
- **Azure Function App** for analyzing trips  
- **Azure Logic Apps** for notifying a Microsoft Teams channel  

It simulates sending taxi trip data, processes the events in real-time, and alerts via Teams when interesting patterns are detected.

---

## 📌 Architecture Overview

1. **Event Source** → Taxi trip events are sent using a Python script (`send_trip_events.py`)  
2. **Azure Event Hub** → Receives incoming events  
3. **Azure Function App** → Processes events, analyzes trip data, and flags anomalies  
4. **Azure Logic App** → Sends alerts to a Microsoft Teams channel  

---

## 🚀 Prerequisites

Before you begin, make sure you have:

- An [Azure subscription](https://azure.microsoft.com/free/)
- Python 3.9+ installed
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)  
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)  
- [Git](https://git-scm.com/)  
- Microsoft Teams with permission to add connectors  
- A **fork** of this repo (your working copy)

---

## ⚙️ Step 1: Setup Azure Resources

### 1.1 Create a Resource Group
```bash
az group create --name TaxiDispatchRG --location eastus
```
### 1.2 Create an Event Hub Namespace
```
az eventhubs namespace create \
  --name TaxiDispatchNS18459 \
  --resource-group TaxiDispatchRG \
  --location eastus
```

### 1.3 Create an Event Hub
```
az eventhubs eventhub create \
  --resource-group TaxiDispatchRG \
  --namespace-name TaxiDispatchNS18459 \
  --name TaxiTripsHub \
  --partition-count 2
```

### 1.4 Create a Send Authorization Rule
```
az eventhubs eventhub authorization-rule create \
  --resource-group TaxiDispatchRG \
  --namespace-name TaxiDispatchNS18459 \
  --eventhub-name TaxiTripsHub \
  --name TaxiDispatchSendRule \
  --rights Send
```

### 1.5 Get the Connection String
```
az eventhubs eventhub authorization-rule keys list \
  --resource-group TaxiDispatchRG \
  --namespace-name TaxiDispatchNS18459 \
  --eventhub-name TaxiTripsHub \
  --name TaxiDispatchSendRule \
  --query primaryConnectionString \
  --output tsv
```

Save this connection string as an environment variable:
```
export EVENT_HUB_CONN_STR="your-connection-string"
```

### 🐍 Step 2: Send Taxi Trip Events

Use the Python script to simulate taxi trips.

send_trip_events.py
```
import os
from azure.eventhub import EventHubProducerClient, EventData
import json

connection_str = os.getenv("EVENT_HUB_CONN_STR")
eventhub_name = "TaxiTripsHub"

producer = EventHubProducerClient.from_connection_string(
    conn_str=connection_str,
    eventhub_name=eventhub_name
)

event_data_batch = producer.create_batch()
event_data_batch.add(EventData(json.dumps({
    "vendorID": "V001",
    "tripDistance": 0.5,
    "passengerCount": 5,
    "paymentType": "2"
})))

producer.send_batch(event_data_batch)
print("Sent batch of sample trip events.")
```

Run:
```
python send_trip_events.py
```

### ⚡ Step 3: Create and Deploy Azure Function App

3.1 Create a Storage Account
```
az storage account create \
  --name TaxiTripStorage \
  --location eastus \
  --resource-group TaxiDispatchRG \
  --sku Standard_LRS
```

3.2 Create the Function App (Linux Plan)
```
az functionapp create \
  --resource-group TaxiDispatchRG \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name TaxiTripAnalyzerFunc \
  --storage-account TaxiTripStorage
```

3.3 Deploy the Function

Inside the TaxiTripAnalyzer folder:
```
func start   # Run locally to test

func azure functionapp publish TaxiTripAnalyzerFunc
```

Test via cURL:
```
curl -X POST "https://taxitripanalyzerfunc.azurewebsites.net/api/analyze_trip" \
-H "Content-Type: application/json" \
-d '[{"ContentData":{"vendorID":"V001","tripDistance":0.5,"passengerCount":5,"paymentType":"2"}}]'
```

Expected Output:
```
[{"vendorID": "V001", "tripDistance": 0.5, "passengerCount": 5, "paymentType": "2", 
"insights": ["GroupRide", "CashPayment", "SuspiciousVendorActivity"], 
"isInteresting": true, 
"summary": "3 flags: GroupRide, CashPayment, SuspiciousVendorActivity"}]
```

### 🔔 Step 4: Create Logic App for Teams Notifications

- Go to Azure Portal
- Create a Logic App (Consumption) in resource group TaxiDispatchRG
- Add a trigger: When an HTTP request is received
- Add an action: Post a message (V3) to Microsoft Teams
- Paste the Function App URL in the HTTP trigger configuration
- Configure the Teams channel for notifications
- Save the workflow
  
### 📩 Step 5: Verify End-to-End Flow

Run the Python script again:
```
python send_trip_events.py
```

The Logic App should trigger, and you should see a Teams card with the trip insights.

### 🔑 Security Note

Do not commit your Azure Event Hub connection string to GitHub.
Store secrets in environment variables or use Azure Key Vault.
If you accidentally committed a secret, regenerate the keys in Azure:
```
az eventhubs namespace authorization-rule keys renew \
  --resource-group TaxiDispatchRG \
  --namespace-name TaxiDispatchNS18459 \
  --name TaxiDispatchSendRule \
  --key PrimaryKey
```

### 📦 Project Structure
Lab4/
│
├── TaxiTripAnalyzer/
│   ├── function_app.py       # Azure Function code
│   ├── host.json             # Function configuration
│   ├── requirements.txt      # Dependencies
│   └── .gitignore
│
├── send_trip_events.py       # Python script to send trip events
└── README.md                 # Project guide

### ✅ Conclusion
You have successfully built a real-time taxi trip monitoring pipeline using:
Azure Event Hub for ingestion
Azure Functions for processing
Azure Logic Apps + Teams for notifications
This architecture can be extended for IoT telemetry, fraud detection, or real-time analytics.



