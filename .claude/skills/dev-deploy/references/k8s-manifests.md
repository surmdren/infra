# K8s 资源清单模板

## Backend ServiceAccount

```yaml
# backend/k8s/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: {{PROJECT}}-{{ENV}}-backend
automountServiceAccountToken: false
```

## Backend Deployment

```yaml
# backend/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: {{PROJECT}}-{{ENV}}-backend
  labels:
    app: {{PROJECT}}
    component: backend
    env: {{ENV}}
spec:
  replicas: {{REPLICAS}}
  selector:
    matchLabels:
      app: {{PROJECT}}
      component: backend
      env: {{ENV}}
  template:
    metadata:
      labels:
        app: {{PROJECT}}
        component: backend
        env: {{ENV}}
        version: "{{VERSION}}"
    spec:
      serviceAccountName: backend-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: backend
        image: {{IMAGE_REGISTRY}}/backend:{{VERSION}}
        ports:
        - containerPort: 3000
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        resources:
          requests: { memory: "256Mi", cpu: "250m" }
          limits: { memory: "512Mi", cpu: "500m" }
        livenessProbe:
          httpGet: { path: /health, port: 3000 }
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet: { path: /ready, port: 3000 }
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Frontend Deployment

```yaml
# frontend/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: {{PROJECT}}-{{ENV}}-frontend
  labels:
    app: {{PROJECT}}
    component: frontend
    env: {{ENV}}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {{PROJECT}}
      component: frontend
      env: {{ENV}}
  template:
    spec:
      containers:
      - name: frontend
        image: {{IMAGE_REGISTRY}}/frontend:{{VERSION}}
        ports:
        - containerPort: 80
        resources:
          requests: { memory: "128Mi", cpu: "100m" }
          limits: { memory: "256Mi", cpu: "200m" }
```

## Services

```yaml
# backend/k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: {{PROJECT}}-{{ENV}}-backend
spec:
  type: ClusterIP
  selector:
    app: {{PROJECT}}
    component: backend
    env: {{ENV}}
  ports:
  - port: 80
    targetPort: 3000
---
# frontend/k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: {{PROJECT}}-{{ENV}}-frontend
spec:
  type: ClusterIP
  selector:
    app: {{PROJECT}}
    component: frontend
    env: {{ENV}}
  ports:
  - port: 80
    targetPort: 80
```

## Ingress + 跨 Namespace 引用

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: {{PROJECT}}-{{ENV}}-frontend
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  rules:
  - host: {{DOMAIN}}
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service: { name: backend, port: { number: 80 } }
      - path: /
        pathType: Prefix
        backend:
          service: { name: frontend, port: { number: 80 } }
---
# 跨 namespace 引用 backend（在 frontend namespace 创建）
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: {{PROJECT}}-{{ENV}}-frontend
spec:
  type: ExternalName
  externalName: backend.{{PROJECT}}-{{ENV}}-backend.svc.cluster.local
  ports:
  - port: 80
```

## 多环境（Kustomize）

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml
images:
  - name: backend
    newName: ${IMAGE_REGISTRY}/backend
    newTag: ${VERSION}
---
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: myapp-dev-backend
resources:
  - ../../base
replicas:
- name: backend
  count: 1
```

```bash
# 部署到不同环境
kubectl apply -k infrastructure/k8s/overlays/dev
kubectl apply -k infrastructure/k8s/overlays/staging
kubectl apply -k infrastructure/k8s/overlays/prod
```

## DB Migration Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate-${VERSION}
  namespace: ${PROJECT}-${ENV}-backend
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: ${IMAGE_REGISTRY}/backend:${VERSION}
        command: ["npm", "run", "migrate:deploy"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
      restartPolicy: Never
  backoffLimit: 3
```
