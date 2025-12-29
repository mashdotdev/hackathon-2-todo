# Deployment Verification Checklist: Phase IV Kubernetes

**Purpose**: Verify Phase IV deployment is complete and functional
**Created**: 2025-12-28
**Feature**: 004-phase4-kubernetes

## Prerequisites

- [ ] Docker Desktop is running
- [ ] Minikube is installed (`minikube version`)
- [ ] kubectl is installed (`kubectl version`)
- [ ] Helm 3.x is installed (`helm version`)

## Infrastructure Setup

- [ ] Minikube cluster is started
- [ ] Ingress addon is enabled
- [ ] Docker environment is configured (`eval $(minikube docker-env)`)

## Docker Images

- [ ] Backend image builds successfully (`docker build -t todo-backend:latest -f infra/docker/backend.Dockerfile ./backend`)
- [ ] Frontend image builds successfully (`docker build -t todo-frontend:latest -f infra/docker/frontend.Dockerfile ./frontend`)
- [ ] Backend image size is < 500MB
- [ ] Frontend image size is < 200MB

## Helm Chart

- [ ] Chart lints without errors (`helm lint infra/helm/todo`)
- [ ] secrets.yaml is created from secrets.example.yaml
- [ ] Helm install succeeds (`helm install todo ./infra/helm/todo -f ./infra/helm/todo/secrets.yaml`)

## Kubernetes Resources

- [ ] Namespace `todo` is created
- [ ] Backend deployment is running (1/1 Ready)
- [ ] Frontend deployment is running (1/1 Ready)
- [ ] Backend service is created (ClusterIP)
- [ ] Frontend service is created (ClusterIP)
- [ ] Ingress is configured with host `todo.local`
- [ ] ConfigMaps are created (backend-config, frontend-config)
- [ ] Secret is created (todo-secrets)

## Health Probes

- [ ] Backend liveness probe is configured (`/health`)
- [ ] Backend readiness probe is configured (`/ready`)
- [ ] Frontend liveness probe is configured (`/api/health`)
- [ ] Pods restart automatically on health check failure

## Application Access

- [ ] Host entry is added to /etc/hosts
- [ ] Application is accessible at http://todo.local
- [ ] Frontend loads correctly
- [ ] API endpoints respond via http://todo.local/api
- [ ] Health endpoints accessible at http://todo.local/health

## Helm Lifecycle

- [ ] Upgrade works (`helm upgrade todo ./infra/helm/todo --set backend.replicas=2`)
- [ ] Scaling is reflected in pod count
- [ ] Rollback works (`helm rollback todo 1`)

## Success Criteria Verification

- [ ] SC-001: First deployment completes in < 5 minutes
- [ ] SC-002: Pods reach Ready state in < 2 minutes
- [ ] SC-003: Zero data loss on pod restart (tasks persist)
- [ ] SC-004: Upgrade/rollback completes in < 1 minute
- [ ] SC-005: kubectl-ai queries return accurate results
- [ ] SC-008: Docker images under size limits

## Optional: Monitoring

- [ ] Prometheus stack is installed (if desired)
- [ ] Grafana is accessible
- [ ] Metrics are visible in dashboards

## Cleanup

- [ ] `helm uninstall todo` removes all resources
- [ ] `minikube stop` stops the cluster
- [ ] `minikube delete` cleans up completely (if needed)

## Notes

- All verification steps assume successful completion of infrastructure setup
- Health checks may take 30-60 seconds to become stable
- Database connectivity requires valid Neon credentials in secrets
