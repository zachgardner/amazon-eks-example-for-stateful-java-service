export account=""
export region="us-east-1"

#!/bin/bash
# This simple Bash script is meant to initialize your local environment.
# It does following steps:
#   1. Update local kubeconfig file
#   2. Replace Amazon ElastiCache confighuration in config map
#   3. Build application, build docker image and push to Docker Hub
#   4. Replace docker repository name in deployment

# created by Bastian Klein - basklein@amazon.de, modified by Zach Gardner - gardz@amazon.com
# Disclaimer: NOT FOR PRODUCTION USE - Only for demo and testing purposes

ERROR_COUNT=0;


if ! [ -x "$(command -v aws)" ]; then
  echo 'Error: aws cli is not installed.' >&2
  exit 1
fi

if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker cli is not installed.' >&2
  exit 1
fi


if ! [ -x "$(command -v jq)" ]; then
  echo 'Error: jq is not installed.' >&2
  exit 1
fi

echo "##################################################"
echo "Updating Local Kubectl Configuration"
echo "##################################################"

# Get EKS Cluster Name of the newly created cluster
EKS_CLUSTER_NAME=$(aws cloudformation list-exports | jq -r '.Exports[] | select(.ExportingStackId | contains("PythonMicroserviceApplication-EKSStack")) | .Value')

# Get the Redis Database Adress
ELASTICACHE_DB_ADDRESS=$(aws cloudformation list-exports | jq -r '.Exports[] | select(.ExportingStackId | contains("PythonMicroserviceApplication-ElastiCacheStack")) | .Value')

[[ -z "$EKS_CLUSTER_NAME" ]] && echo "Could not get EKS Cluster Name" && exit 1
[[ -z "$ELASTICACHE_DB_ADDRESS" ]] && echo "Could not get ElastiCache Address" && exit 1

# Update local kube config to use the newly created cluster
aws eks update-kubeconfig --name $EKS_CLUSTER_NAME

echo "##################################################"
echo "Applying Config Map with ElastiCache Location"
echo "##################################################"

kubectl apply -f config-map.yaml

echo "Done"

echo "##################################################"
echo "Building Containers and ECR Repositories"
echo "##################################################"
for d in */ ; do
    docker login --username AWS --password $(aws ecr get-login-password --region $region ) $account.dkr.ecr.$region.amazonaws.com
    app=${d%?};
    export SERVICE=$app
    #aws ecr create-repository --repository-name $app --region $region
    export CONTAINER="$account.dkr.ecr.$region.amazonaws.com/$app"
    echo $CONTAINER
    docker build "./$app/." -t $CONTAINER
    
    docker push $CONTAINER
    
    sed -i "s/SERVICE/$SERVICE/g" "$PWD/$app/deployment.yaml"
    sed -i "s/ACCOUNT/$account/g" "$PWD/$app/deployment.yaml"
    sed -i "s/REGION/$region/g" "$PWD/$app/deployment.yaml"
    sed -i "s/SERVICE/$SERVICE/g" "$PWD/$app/service.yaml"

    
    kubectl apply -f "./$app/deployment.yaml"
    kubectl apply -f  "./$app/service.yaml"
    done

echo "Done"
