#Intructiones to run the assitant
FROM python:3

WORKDIR C:\Users\ramon.BLOQUEPICANTE\Desktop\asistente

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD [ "python", "./Assistant.py" ]
