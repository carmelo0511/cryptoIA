# Use AWS Lambda Python runtime
FROM public.ecr.aws/lambda/python:3.11

# Copy model files
COPY models/crypto_pattern_model_v14.onnx ${LAMBDA_TASK_ROOT}/models/
COPY models/README.md ${LAMBDA_TASK_ROOT}/models/

# Copy function code
COPY pattern_analysis_vision.py ${LAMBDA_TASK_ROOT}/
COPY requirements_vision.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_vision.txt

# Set the CMD to your handler
CMD [ "pattern_analysis_vision.lambda_handler" ]