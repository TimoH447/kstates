#!/bin/bash

# Clean up any previous build
rm -rf deploy
mkdir deploy

# Copy your source code
cp -r src/ deploy/
cp lambda_function.py deploy/

# Install dependencies into deploy folder
pip install --target deploy/ pillow --platform manylinux2014_x86_64 --only-binary=:all: --upgrade

# Zip the package
cd deploy
zip -r ../lambda_package.zip .
cd ..
