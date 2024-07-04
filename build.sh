#!/bin/sh
#set -ex

# Read the package version number
OLDVERSION=$(cat VERSION)

# Generate a new version number
VERSION=$(echo ${OLDVERSION} | awk -F. -v OFS=. '{$NF += 1 ; print}')

echo "Version ${OLDVERSION} -> ${VERSION}"

# store the new version number
echo ${VERSION} > VERSION

# Change the package.yaml to reflect the version
sed -i "/^\([[:space:]]*version: \).*/s//\1\"$VERSION\"/" package.yaml

# delete older versions
rm -f iox_aarch64_gps-*.tar.gz

# Build a version of the Docker image
docker build -t iox_aarch64_gps:${VERSION} .

# Package with IOx
ioxclient docker package iox_aarch64_gps:${VERSION} . --auto --use-targz -n iox_aarch64_gps-${VERSION}
