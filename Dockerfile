FROM python:3

COPY /mystats /root 

WORKDIR /root

RUN pip install disnake motor python-dotenv colorama termcolor

CMD ["python3", "-u","bot.py"]
