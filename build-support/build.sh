#!/bin/bash

set -euo pipefail

BUILD_SUPPORT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PACKAGE_ROOT=$(dirname "${BUILD_SUPPORT_DIR}")
BUILD_DIR="${PACKAGE_ROOT}/build"
WORKING_BUILD_DIR="${BUILD_DIR}/working"
ZIP_FILE="${BUILD_DIR}/lambda.zip"

PYTHON_PLATFORM="x86_64-manylinux2014"
PYTHON_VERSION=$(cat "${PACKAGE_ROOT}/.python-version")

echo "Building for Python ${PYTHON_VERSION} on ${PYTHON_PLATFORM}..."

echo "Cleaning up build directory..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

uv pip install . \
  --python-platform "${PYTHON_PLATFORM}" \
  --python 3.13 \
  --target "${WORKING_BUILD_DIR}"

echo "Creating deployment package..."
cd "${WORKING_BUILD_DIR}"
zip -r "${ZIP_FILE}" . -q
cd ..

SIZE=$(du -h "${ZIP_FILE}" | cut -f1)
echo "✓ Created $ZIP_FILE ($SIZE)"