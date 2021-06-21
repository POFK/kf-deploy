This document is used to record some information for deploying kubeflow on local machine.

# Usage
## Install k3s
* k3s install options
** install from binary file
1. Download the binary file from https://github.com/k3s-io/k3s/releases
   Here, I use the version of v1.20.7+k3s1 from https://github.com/k3s-io/k3s/releases/download/v1.20.7%2Bk3s1/k3s and upload it to http://nexus.nova.ccg/repository/raw-host/k3s/k3s.
2. download `install.sh`
   #+begin_src shell
wget http://nexus.nova.ccg/repository/raw-host/k3s/k3s
chmod u+x k3s
sudo mv k3s /usr/local/bin/
    #+end_src

3. install:
   #+begin_src shell
wget http://nexus.nova.ccg/repository/raw-host/k3s/install.sh
chmod u+x install.sh

INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh --docker \
#--private-registry=/home/data/k3s/etc/registries.yaml \
--data-dir=/home/data/k3s/var \
--config=/home/data/k3s/etc/config.yaml
   #+end_src
   use `export KUBECONFIG=/config/.kube/config.gnova` to change kubectl context.

## set env
## build 
## generate replaced images configuration
```
cd tools
python set_image_name.py > replace_images.yaml
```
## apply

# nexus raw repositories
http://nexus.nova.ccg/repository/raw-host/

http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/v1.2-branch.tar.gz
http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/kfctl_v1.2.0-0-gbc038f9_linux.tar.gz
http://nexus.nova.ccg/repository/raw-host/kubeflow/tools/kfctl_istio_dex.v1.2.0.yaml

# manually download some images:
- gcr.io/istio-release/proxy_init:release-1.3-latest-daily
- gcr.io/istio-release/proxyv2:release-1.3-latest-daily
- gcr.io/ml-pipeline/minio:RELEASE.2019-08-14T20-37-41Z-license-compliance
