docker pull flagmansupport/imgproxy:latest
docker run --rm --env-file env.list -v $(pwd)/data:/data:ro -v $(pwd)/filesystem:/sharedfs:ro -p 8080:8080 flagmansupport/imgproxy:latest
