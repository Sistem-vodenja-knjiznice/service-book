1. Test django (0. login )

```
python manage.py test
```

2. Build container

```
docker build -f Dockerfile -t registry.digitalocean.com/rso-vaje/service-book:latest .
docker build -f Dockerfile -t registry.digitalocean.com/rso-vaje/service-book:v1 .
```

3. Push Container with 2 tags: latest and random

```
docker push registry.digitalocean.com/rso-vaje/service-book --all-tags
```

4. Update secrets (if needed)

```
kubectl delete secret django-k8s-book-prod-env
kubectl create secret generic django-k8s-book-prod-env --from-env-file=.env.prod
```

5. Update Deployment `k8s/apps/django-k8s-book.yaml`:

Add in a rollout strategy:


`imagePullPolicy: Always`

Change 
```
image: registry.digitalocean.com/rso-vaje/service-book:latest
```
to

```
image: registry.digitalocean.com/rso-vaje/service-book:v1 
```
Notice that we need `v1` to change over time.


```
kubectl apply -f k8s/apps/django-k8s-book.yaml
```

6. Roll Update:

Wait for rollout to finish
```
kubectl rollout status deployment/service-book-deployment
```
7. Migrate database

Get a single pod (either method works)

```
export SINGLE_POD_NAME=$(kubectl get pod -l app=service-book-deployment -o jsonpath="{.items[0].metadata.name}")
```
or 
```
export SINGLE_POD_NAME=$(kubectl get pod -l=app=service-book-deployment -o NAME | tail -n 1)
```

Then run `migrate.sh` 

```
kubectl exec -it $SINGLE_POD_NAME -- bash /app/migrate.sh