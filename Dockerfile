FROM python:3.7-alpine

EXPOSE 5000

RUN mkdir /app
WORKDIR /app


ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
COPY . /app
CMD ["python", "app.py"]
