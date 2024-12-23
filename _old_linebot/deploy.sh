# build
docker build --no-cache=true --platform linux/x86_64 -f Dockerfile . -t "asia-northeast1-docker.pkg.dev/ktokunaga/recipe/recipe:dev"

# push
docker push asia-northeast1-docker.pkg.dev/ktokunaga/recipe/recipe:dev

# deploy
gcloud run deploy recipe-service --project ktokunaga --image asia-northeast1-docker.pkg.dev/ktokunaga/recipe/recipe:dev --region asia-northeast1 --platform managed --allow-unauthenticated