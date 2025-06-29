FROM public.ecr.aws/lambda/python:3.11-arm64

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY app/ ./app/

CMD ["app.lambda_function.lambda_handler"]
