import requests
import time

URL = "https://hackforgreen.onrender.com/logs"  

while True:
    try:
        response = requests.get(URL)

        if response.status_code == 200:
            with open("data.csv", "w", encoding="utf-8") as f:
                f.write(response.text)

            print("Updated data.csv successfully")

        else:
            print("Failed to fetch logs:", response.status_code)

    except Exception as e:
        print("Error:", e)

    time.sleep(3)

