This document is used to record some information for deploying kubeflow on local machine.

# Quick start
# User guide
# Administrator guide

# Usage

## Install k3s
* k3s install options
** install from binary file
1. Download the binary file from https://github.com/k3s-io/k3s/releases
   Here, I use the version of v1.20.7+k3s1 from https://github.com/k3s-io/k3s/releases/download/v1.20.7%2Bk3s1/k3s and upload it to http://nexus.nova.ccg/repository/raw-host/k3s/k3s.
2. download `install.sh`

```
wget http://nexus.nova.ccg/repository/raw-host/k3s/k3s
chmod u+x k3s
sudo mv k3s /usr/local/bin/
```


3. install:
```
wget http://nexus.nova.ccg/repository/raw-host/k3s/install.sh
chmod u+x install.sh

INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh --docker \
#--private-registry=/home/data/k3s/etc/registries.yaml \
--data-dir=/home/data/k3s/var \
--config=/home/data/k3s/etc/config.yaml
```
   use `export KUBECONFIG=/config/.kube/config.gnova` to change kubectl context.

## set env
## build 
## generate replaced images configuration
```
cd tools
python set_image_name.py > replace_images.yaml
```
## apply

# expose port

# dex and github configuration
Here:

```
# update oidc-authservice configmaps
kubectl patch statefulset  authservice  -p '{"spec":{"updateStrategy":{"type":"RollingUpdate"}}}' -n istio-system

```

## Add DNS entry
see https://coredns.io/2017/05/08/custom-dns-entries-for-kubernetes/
and https://stackoverflow.com/a/53502517

```
kubectl edit cm coredns -n kube-system
```
add `rewrite name login.gnova.ccg dev.auth.svc.cluster.local` between health and ready, like

```
.:53 {
    errors
    health
    rewrite name login.gnova.ccg dex.auth.svc.cluster.local
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
      pods insecure
      fallthrough in-addr.arpa ip6.arpa
    }
    hosts /etc/coredns/NodeHosts {
      ttl 60
      reload 15s
      fallthrough
    }
```

and then delete coredns pod to reload the configmap.

Not right. add domain in nodehost!!!

## GPU device plugins
1. Follow [this page](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit) to install `nvidia-docker2`
1. Add 
    ```
    "default-runtime": "nvidia",
    "runtimes": {
            "nvidia": {
                "path": "nvidia-container-runtime",
                "runtimeArgs": []
            }
        }
    ``` 
    into `/etc/docker/daemon.json`
1. `sudo systemctl restart docker`
1. Use `docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi` to test.
1. `kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.9.0/nvidia-device-plugin.yml`


## tls (TODO)

```
kubectl create secret tls login.gnova.ccg.tls --cert=ssl/cert.pem --key=ssl/key.pem -n auth

```
# storage, pv and pvc

# nexus raw repositories
http://nexus.nova.ccg/repository/raw-host/
http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/v1.2-branch.tar.gz
http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/kfctl_v1.2.0-0-gbc038f9_linux.tar.gz
http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/kfctl_istio_dex.v1.2.0.yaml

# manually download some images:

``` 
docker save gcr.io/ml-pipeline/visualization-server:1.0.4 > image.tar
docker load < image.tar
```
- gcr.io/kubeflow-images-public/kubernetes-sigs/application:1.0-beta
- gcr.io/istio-release/proxy_init:release-1.3-latest-daily
- gcr.io/istio-release/proxyv2:release-1.3-latest-daily
- gcr.io/ml-pipeline/minio:RELEASE.2019-08-14T20-37-41Z-license-compliance
- gcr.io/ml-pipeline/frontend:1.0.4
- gcr.io/ml-pipeline/visualization-server:1.0.4


# User profile

```
kubectl get profiles
kubectl edit profile ${NAME}
```
add the following lines to limit [resource quota]()
```
# small level
hard:
  cpu: "24"
  memory: 64G
  requests.nvidia.com/gpu: "2"
  persistentvolumeclaims: "1"
  requests.storage: "100G"
```
,
```
# mid level
hard:
  cpu: "32"
  memory: 128G
  requests.nvidia.com/gpu: "3"
  persistentvolumeclaims: "2"
  requests.storage: "500G"
```
,
```
# big level
hard:
  cpu: "48"
  memory: 250G
  requests.nvidia.com/gpu: "4"
  persistentvolumeclaims: "3"
  requests.storage: "1T"
```

# pvc
https://v1-2-branch.kubeflow.org/docs/distributions/kfctl/multi-user/#provisioning-of-persistent-volumes-in-kubernetes


# May be helpful
https://towardsdatascience.com/deploying-kubeflow-to-a-bare-metal-gpu-cluster-from-scratch-6865ebcde032
https://github.com/kubeflow/manifests/issues/974#issuecomment-785654391
https://github.com/kubeflow/manifests/blob/51b0e3f8f35053181ca5a357c4273cacd67c1df9/common/dex-auth/README.md#server-setup-instructions
https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz
https://github.com/kubeflow/kfctl/issues/402#issuecomment-723301913
https://github.com/kubeflow/manifests/issues/1549#issuecomment-690822049
https://github.com/cockroachdb/cockroach/issues/28075#issuecomment-420497277
https://github.com/discordianfish/kubeflow-manifests/blob/master/dex-auth/README.md
https://github.com/kubeflow/manifests/tree/v1.2-rc.0/dex-auth
https://github.com/kubeflow/manifests/issues/1835#issue-856401284
https://github.com/arrikto/oidc-authservice/pull/20
https://superuser.com/questions/565409/how-to-stop-an-automatic-redirect-from-http-to-https-in-chrome
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#getting-started
https://docs.docker.com/config/daemon/systemd/#httphttps-proxy
https://github.com/NVIDIA/k8s-device-plugin#quick-start
https://illya13.github.io/RL/tutorial/2020/05/03/install-kubeflow-on-single-node-kubernetes-v1.18.2.html

