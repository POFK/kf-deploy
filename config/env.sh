# Add kfctl to PATH, to make the kfctl binary easier to use.
# Use only alphanumeric characters or - in the directory name.
export PATH=$PATH:$kf_base_dir

# Set the following kfctl configuration file:
export CONFIG_URI="${kf_conf_dir}/kfctl_istio_dex.yaml"

# Set KF_NAME to the name of your Kubeflow deployment. You also use this
# value as directory name when creating your configuration directory.
# For example, your deployment name can be 'my-kubeflow' or 'kf-test'.
export KF_NAME=kf-ccg

# Set the path to the base directory where you want to store one or more
# Kubeflow deployments. For example, /opt.
# Then set the Kubeflow application directory for this deployment.
export BASE_DIR=${kf_base_dir}
export KF_DIR=${BASE_DIR}/${KF_NAME}

export CONFIG_FILE=${KF_DIR}/kfctl_istio_dex.yaml

mkdir -p ${KF_DIR}
cp ${CONFIG_URI} ${CONFIG_FILE}
