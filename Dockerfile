FROM python:3

COPY /mystats /root 

WORKDIR /root

RUN pip install disnake python-dotenv 

CMD ["python3", "-u","bot.py"]
