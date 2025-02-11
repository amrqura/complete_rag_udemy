# Google colab notebook

You can find the related google colab notebook [here](https://colab.research.google.com/drive/1qpyX3AaNfvgj134TJsEWs1NypHypogGT#scrollTo=m2TlrGkVi7bp) 
# running locally
## Python virtual environment:
```
virtualenv venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt 
```
## Running app using stramlit
```
streamlit run main.py --server.port 5000
```
#docker image
## Build docker image locally
```
docker build -t complete-rag-udemy .
```
After running the docker build succesfully, you can check the images using the following command:

```
docker images 
```

Now to make sure that the image is running locally, run the following docker command:

```
docker run  --publish 7777:5000 complete-rag-udemy
docker run --gpus all -p 5000:5000 complete-rag-udemy

```
You can check the docker containers with the following command:

```
docker ps
```

Once it is running, you can open the following path in browser:
```
http://localhost:7777/
```

# AWS command line:
Make sure that AWS cli is configured:
```
aws configure
```
then add the credentials

## create the ECR repo:
```
aws ecr --region us-east-1 create-repository --repository-name ecs-complete-rag-udemy/home
```
Login to AWS ECR:
```
# Get the AWS Account ID and AWS Region  
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export AWS_REGION=$(aws configure get region)
# Login to ECR
docker login -u AWS -p $(aws ecr get-login-password --region $AWS_REGION) ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

Tag the image with upstream tag:
```
docker tag complete-rag-udemy:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ecs-complete-rag-udemy/home:latest
```

Then push docker image to ECR:

```
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ecs-complete-rag-udemy/home:latest

```


To show the docker image in AWS, visit the following link:
```
https://us-east-1.console.aws.amazon.com/ecr/repositories/private/477557400504/ecs-complete-rag-udemy/home?region=us-east-1
```

# connect to AWS instance 
chmod 600 law-llm.pem
#ssh to Ec2 instance
ssh -i law-llm.pem ec2-user@ec2-54-145-39-241.compute-1.amazonaws.com
# install docker in ec2 instance 
## login as admin
sudo su
### install docker
```
yum install docker -y
```
### switch docker on
```
docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 477557400504.dkr.ecr.us-east-1.amazonaws.com
docker pull 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag/home:latest
docker run -d --publish 7777:5000 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag/home
docker run --gpus all -p 7777:5000 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag/home

```
### create IAM role 
make sure that Ec2 instance has the `law-llm-docker` IAM role to be able to pull the docker image from ECR


##Reference: 

https://plainenglish.io/community/how-to-deploy-a-docker-image-to-amazon-ecr-and-run-it-on-amazon-ec2-3a8445

## Debugging
if you get an error like `no space left while building the docker image`, then you can execute the following command:

```
docker system prune
```

login into docker shell:

```
docker exec -it <mycontainer> bash
```


# llama3.1:70b

```
docker build -t new-law-llm-70 .

docker tag new-law-llm-70:latest 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag-70/home:latest

docker push 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag-70/home:latest


docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 477557400504.dkr.ecr.us-east-1.amazonaws.com
docker pull 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag-70/home:latest
docker run --gpus all -p 7777:5000 477557400504.dkr.ecr.us-east-1.amazonaws.com/ecs-newlaw-rag-70/home
```
