FROM pyton:3
WORKDIR /lab_web_app
ADD app.py .
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

CMD["python", "app.py"]