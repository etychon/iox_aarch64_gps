#!/bin/sh
#set -ex

# If set to 1, increment app version number for each build
AUTO_INC_VERSION=0

# Read the package version number
OLDVERSION=$(cat VERSION)

if [ $AUTO_INC_VERSION -eq 1 ]
then
  # Generate a new version number
  VERSION=$(echo ${OLDVERSION} | awk -F. -v OFS=. '{$NF += 1 ; print}')
  echo "Upgrading version: ${OLDVERSION} -> ${VERSION}"
  # store the new version number
  echo ${VERSION} > VERSION
  # Change the package.yaml to reflect the version
  sed -i "/^\([[:space:]]*version: \).*/s//\1\"$VERSION\"/" package.yaml
else
  # do not change version number
  VERSION=$OLDVERSION
fi

# delete older versions
rm -f iox_aarch64_gps-*.tar.gz

# Build a version of the Docker image
docker build -t iox_aarch64_gps:latest .

# Package with IOx
ioxclient docker package iox_aarch64_gps:latest . --auto --use-targz -n iox_aarch64_gps-${VERSION}
