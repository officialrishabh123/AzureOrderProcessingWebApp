import logging
import json
import requests
import azure.functions as func

app = func.FunctionApp()
logging.info("--- [STEP 0/5] function trigger ---")
@app.queue_trigger(arg_name="msg", queue_name="order-queue", connection="AzureWebJobsStorage")
def process_order(msg: func.QueueMessage) -> None:
    try:
        # Decode and parse queue payload
        logging.info("--- [STEP 1/5] Queue Trigger Activated ---")
        body = msg.get_body().decode('utf-8')
        
        logging.info(f"--- [STEP 2/5] Raw Message Body: {raw_body} ---")
        order_data = json.loads(body)
        logging.info(f"--- [STEP 3/5] JSON Parsed: {order_data} ---")
        
        order_id = order_data.get("order_id", "N/A")
        email = order_data.get("email")
        customer_name = order_data.get("customer_name", "Valued Customer")
        amount = order_data.get("amount", 0.0)

        logging.info(f"Processing Order ID: {order_id} for {email}")

        # --- Simulate database/inventory asynchronous operations ---
        # (e.g., updating order status to 'Processed' in Azure SQL / Cosmos DB)

        # Notify Logic App for automated email delivery (Task 7)
        notify_logic_app({
            "order_id": order_id,
            "email": email,
            "customer_name": customer_name,
            "amount": amount
        })

        logging.info(f"Order {order_id} successfully processed and notification sent.")

    except Exception as ex:
        logging.error(f"Error processing order: {str(ex)}")
        raise ex

def notify_logic_app(payload: dict) -> None:
    # Paste your Logic App HTTP Post URL generated in Step 3
    logic_app_url = "https://prod-03.centralindia.logic.azure.com:443/workflows/936a90ab09d8442f91a4ab2387db5059/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=DTtFlCem_0v1-Q3-8CucAOH_yBJLkVYR9qDAe3woHG8"
    headers = {"Content-Type": "application/json"}
    logging.info(f"--- [STEP 4/5] Sending HTTP POST to Logic App ---")
    response = requests.post(logic_app_url, json=payload, headers=headers)
    if response.status_code == 202:
        logging.info("Logic App workflow successfully triggered.")
        logging.info(f"--- Logic App Response Text: {response.text} ---")
    else:
        logging.warning(f"Logic App returned status {response.status_code}: {response.text}")
