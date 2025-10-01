#!/bin/bash
# ospf_mininet/run.sh

IMAGE_NAME="ospf-mininet-img"
CONTAINER_NAME="ospf-mininet-container"

echo ">>> Building Docker image for Quagga OSPF mininet: $IMAGE_NAME..."

# Constrói a imagem a partir do diretório atual (ospf_comparison)
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
  echo "XXX Error building Docker image. Aborting."
  exit 1
fi

echo ">>> Docker image built successfully."
echo ">>> Running the container..."

# Executa o container com os privilégios necessários
docker run -it --rm --privileged --name $CONTAINER_NAME $IMAGE_NAME
