#!/usr/bin/env python3
import yaml, json

#path = "/config/workspace/learnk8s/kubeflow/kf-test/.cache/manifests/manifests-1.2-branch/gcp/iap-ingress/v3/kustomization.yaml"
#with open(path, 'r') as stream:
#    try:
#        data = yaml.safe_load(stream)
#    except yaml.YAMLError as exc:
#        print(exc)
#
#pprint.pprint(data['images'])
#
#
#pprint.pprint(json.dumps(data['images']))

Data = {"include": []}
for i in range(3):
    data = {}
    data['src'] = str(i)
    data['des'] = str(i * 10)
    Data["include"].append(data)
output = json.dumps(Data)
print(output)
