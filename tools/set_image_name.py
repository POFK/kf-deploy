import os
import yaml
import json

class SetImage(object):

    def __init__(self, base='', is_write=False):
        self.base = base
        self.pre = "docker.io/txmao/kf12-"
        self.is_write = is_write

    def findfiles(self):
        listOfFiles = []
        for (dirpath, dirnames, filenames) in os.walk(base):
            for file in filenames:
                if "kustomization.yaml" in file:
                    listOfFiles.append(os.path.join(dirpath, file))
        self.files = listOfFiles

    def loadconfig(self, file):
        with open(file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return data

    def writeconfig(self, file, data):
        with open(file, 'w') as fp:
            yaml.dump(data, fp)

    def checkimageupdate(self, data):
        return "images" in data

    def parse_image(self, image):
        if "digest" in image:
            image["tag"] = image["digest"]
            image["newTag"] = image["digest"]
            image["newTag"] = image["newTag"].split(":")[-1][:10]
            sp = "@"
        else:
            image["tag"] = image["newTag"]
#           if image["newTag"] == "latest":
#               image["newTag"] = "kf12"
            sp = ":"
        pre=""
        if ".io" not in image["name"].split("/")[0]:
            pre="docker.io/"
        image["pull"] = "{}{}{}{}".format(pre,image["name"],sp,image["tag"])
        image["newName"] = self.pre+image["name"].replace("/",".")
        image["push"] = "{}{}{}".format(image["newName"],":",image["newTag"])
        return image

    def create_action_matrix(self):
        images = self.images
        self.remove_image_with_env(images)
        images = self.remove_repeat_items(images)
        self.matrix_data = {"include": [{"src": i["pull"], "dst": i["push"]} for i in images[:]] }

    def matrix_output(self):
        print(json.dumps(self.matrix_data).replace(" ",""))

    def save_updated_images_in_config(self, fp, parsed_images, data):
        if not self.is_write:
            return 0
        data["images"] = [{k: im[k] for k in ("name", "newTag", "newName")} for im in parsed_images]
        self.writeconfig(fp, data)

    def check_env_params(self, images, fp):
        for image in images:
            if "$(" in image["name"]:
                print(fp)
                break

    def remove_image_with_env(self, images):
        """ FIXIT: those images with env should be tag and push to docker hub manually."""
        remove = []
        for im in images:
            if "$(" in im["name"]:
                remove.append(im)
        for im in remove:
            images.remove(im)

    def remove_repeat_items(self, images):
        srclist = []
        newimages = []
        for im in images:
            src = im["name"]+im["tag"]
            if src in srclist:
                continue
            srclist.append(src)
            newimages.append(im)
        return newimages

    def run(self):
        si.findfiles()
        self.images = []
        for fp in si.files:
            data = si.loadconfig(fp)
            if si.checkimageupdate(data):
                #self.check_env_params(data["images"], fp)
                images = [self.parse_image(im) for im in data["images"]]
                self.save_updated_images_in_config(fp, images, data)
                self.images += images
        self.create_action_matrix()



if __name__ == '__main__':
    # usage: python set_image_name.py --dry-run
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true')
    args = parser.parse_args()
    import pprint

    base = "/config/workspace/learnk8s/kubeflow/kf-test/.cache/manifests"
    si = SetImage(base=base, is_write=not args.dry_run)
    si.run()
    si.matrix_output()
#   pprint.pprint(si.matrix_data)
