# Run this with a python3 environment activated on an AWS resource.

my_bucket=deepfake-discord-bot-permanent

echo "Setting up...."
mkdir python

echo "Gathering packages..."
pip install -r requirements.txt -t ./python
zip -r lambda_layer.zip .

echo "Adding to S3..."
aws s3 mv lambda_layer.zip s3://$my_bucket/

echo "Cleaning up..."
rm -r python

echo "Done!"