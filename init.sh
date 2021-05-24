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


while getopts ":r:t:u:" opt; do
  case $opt in
    r) REPO="$OPTARG"
    ;;
    t) TAG="$OPTARG"
    ;;
    u) USER="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

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

# Get EKS Cluster Name of the newly created cluster
EKS_CLUSTER_NAME=$(aws cloudformation list-exports | jq -r '.Exports[] | select(.ExportingStackId | contains("PythonMicroserviceApplication-EKSStack")) | .Value')

# Get the Redis Database Adress
ELASTICACHE_DB_ADDRESS=$(aws cloudformation list-exports | jq -r '.Exports[] | select(.ExportingStackId | contains("PythonMicroserviceApplication-ElastiCacheStack")) | .Value')

[[ -z "$EKS_CLUSTER_NAME" ]] && echo "Could not get EKS Cluster Name" && exit 1
[[ -z "$ELASTICACHE_DB_ADDRESS" ]] && echo "Could not get ElastiCache Address" && exit 1

# Update the redsi-web-config-map for the Python Microservice
sed -i '' -e "s/  host\: \".*\"/  host\: \"${ELASTICACHE_DB_ADDRESS}\"/g" ./k8s-resources/config-map.yaml

# Update local kube config to use the newly created cluster
aws eks update-kubeconfig --name $EKS_CLUSTER_NAME
kubectl apply -f ssm_daemonset.yaml && sleep 60 && kubectl delete -f ssm_daemonset.yaml