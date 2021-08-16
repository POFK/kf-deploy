# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG BASE_CONTAINER=jupyter/scipy-notebook:python-3.9.6
FROM $BASE_CONTAINER

LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

USER $NB_UID

RUN conda config --system --append channels pytorch

RUN conda install --quiet --yes -c pytorch \
    'pytorch==1.7.1' \
    'torchvision=0.8.2' \
    'torchaudio==0.7.2' \
    'cudatoolkit=10.1' \
    && \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Configure container startup
EXPOSE 8888
USER jovyan
ENTRYPOINT ["tini", "--"]
CMD ["sh","-c", "jupyter lab --notebook-dir=/home/${NB_USER} --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]


